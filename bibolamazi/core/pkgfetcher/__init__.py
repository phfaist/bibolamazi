################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2019 by Philippe Faist                                       #
#   philippe.faist@bluewin.ch                                                  #
#                                                                              #
#   Bibolamazi is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   Bibolamazi is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with Bibolamazi.  If not, see <http://www.gnu.org/licenses/>.        #
#                                                                              #
################################################################################

"""
This module provides support for fetching filter packages that are stored on
remote locations, such as on github.
"""

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr
from future.standard_library import install_aliases
install_aliases()

import os
import os.path
import re
import logging
import datetime
import shutil
from urllib.parse import urlparse, urlencode
import json
import hashlib

import appdirs


import bibolamazi.init
from .butils import BibolamaziError
# set up logger after bibolamazi.init
logger = logging.getLogger(__name__)


class UnknownPackageLocation(BibolamaziError):
    def __init__(self, url):
        super(UnknownPackageLocation, self).__init__(
            "Unknown package location '{}'".format(url)
        )


# a downloaded cache gets invalidated and removed after this amount of time
max_cache_age = datetime.timedelta(days=365)

rx_valid_cachedirname = re.compile('^[A-Za-z0-9_.-]$')
rx_valid_subdirpart = re.compile('^[A-Za-z0-9_.-]+$')


def default_pkg_providers():
    return [
        GithubUrlPkgProvider()
    ]


def datetime_to_str(dati):
    return dati.strftime('%Y-%m-%dT%H:%M:%S TZ=%z')

def datetime_from_str(s):
    if ' ' in s:
        (sdt, stz) = s.split(' ')
    else:
        sdt = s
        stz = 'TZ='
    #
    if stz == 'TZ=': # empty time zone string
        return datetime.datetime.strptime(sdt, "%Y-%m-%dT%H:%M:%S")
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S TZ=%z")


class PackageProviderManager(object):
    def __init__(self, user_cache_dir=None, pkg_providers=None):
        super(PackageProviderManager, self).__init__()
        if user_cache_dir is None:
            user_cache_dir = appdirs.user_cache_dir("bibolamazi")
        self.user_cache_dir = user_cache_dir

        if pkg_providers is None:
            pkg_providers = default_pkg_providers()
        self.pkg_providers = pkg_providers

        # ensure the user cache directory itself exists
        if not os.path.isdir(self.user_cache_dir):
            os.mkdir(self.user_cache_dir)

        self.pkgcacheinfo = {
            # self.pkgcacheinfo['pkgcaches'][cachedirname] = {
            #     'cachedirname': cachedirname
            #     'url': <str object>,
            #     'downloaded_datetime': <datetime.datetime object>,
            #     'provider_data': <any data that the PkgProvider might which to associate with this cache>
            # }
            'pkgcaches': {}
        }

        pkgcacheinfofile = self._pkgcacheinfofile()
        if os.path.exists(pkgcacheinfofile):
            with open(pkgcacheinfofile, 'b') as f:
                self.pkgcacheinfo = json.load(f)

        # check to see if there are caches that are very old
        pkgs_to_remove = []
        for cachedirname, pkgi in iteritems(self.pkgcacheinfo['pkgcaches']):
            pkgi_datetime = datetime_from_str(pkgi.get('downloaded_datetime', datetime.datetime(2000,1,1)))
            if (datetime.now() - pkgi_datetime) > max_cache_age:
                logger.debug("Removing cached package %s which was downloaded on %s",
                             cachedirname, pkgi_datetime)
                # don't remove right away, we're still iterating over the pkg info dict
                pkgs_to_remove.append(cachedirname)
        for cachedirname in pkgs_to_remove:
            self._rmcachedir(cachedirname)
        

    def _pkgcacheinfofile(self):
        return os.path.join(self.user_cache_dir, "pkgcacheinfo.json")

    def _fullcachedir(self, cachedirname):
        return os.path.join(self.user_cache_dir, cachedirname)

    def _rmcachedir(self, cachedirname):
        assert self.user_cache_dir and os.path.isdir(self.user_cache_dir)
        assert rx_valid_cachedirname.match(cachedirname)
        assert cachedirname in self.pkgcacheinfo['pkgcaches']

        logger.warning("Here we would call shutil.rmtree(%r); I'm not daring to do so "
                       "until I uncomment the relevant line of code...", self._fullcachedir(cachedirname))
        #shutil.rmtree(self._fullcachedir(cachedirname))

        del self.pkgcacheinfo['pkgcaches'][cachedirname]

    def _createcachedir(self, cachedirname, url):
        assert self.user_cache_dir and os.path.isdir(self.user_cache_dir)
        assert rx_valid_cachedirname.match(cachedirname)
        fullcachedir = self._fullcachedir(cachedirname)
        assert not os.path.exists(fullcachedir)

        os.mkdir(fullcachedir)
        
        d = {
            'cachedirname': cachedirname,
            'url': url,
            'downloaded_datetime': datetime_to_str(datetime.datetime.now()),
            'pkg_subdir': None,
            'provider_data': None
        }
        self.pkgcacheinfo['pkgcaches'][cachedirname] = d


    def get_pythonpath_for(self, url):
        """
        Fetch the package specified as the given `url` (provided as a string).
        """
        
        p = urlparse(url)

        if not p.scheme or p.scheme == 'file':
            # local filesystem directory
            return p.path

        for pkg_provider in self.pkg_providers:
            if pkg_provider.can_provide_from(p.scheme):
                fetcher = pkg_provider.get_fetcher(url)
                return self._pythonpath_for_url_via_provider(fetcher, url, p)

        raise UnknownPackageLocation(url)

    def _pythonpath_for_url_via_provider(self, fetcher, url, p):

        # see if we have this URL in cache already
        for cachedirname, pkgi in self.pkgcacheinfo['pkgcaches']:
            if pkgi.get('url', None) == url:
                if fetcher.check_cache_is_up_to_date(pkgi.get('provider_data', None)):
                    return self._pythonpath_for_cachedirname(cachedirname)
                # this cache is out of date, so we should remove it.
                self._rmcache(cachedirname)
                break

        # we need to fetch the package using this provider

        cachedirname = hashlib.md5(url + '\n' + str(datetime.datetime.now())).hexdigest()

        self._createcachedir(cachedirname, url)
        cachedir_created_ok = False
        try:
            pkg_subdir, provider_data = fetcher.fetch_to_dir(self._fullcachedir(cachedirname))
            
            # pkg_subdir must be a relative sub-dir with forward-slashes on all systems
            if pkg_subdir:
                assert pkg_subdir[0:1] != '/'
                for pdpart in pkg_subdir.split('/'):
                    assert rx_valid_subdirpart.match(pdpart)
            else:
                pkg_subdir = None

            self.pkgcacheinfo['pkgcaches'][cachedirname]['pkg_subdir'] = pkg_subdir
            self.pkgcacheinfo['pkgcaches'][cachedirname]['provider_data'] = provider_data

            cachedir_created_ok = True
        finally:
            if not cachedir_created_ok:
                self._rmcachedir(cachedirname)

        return self._pythonpath_for_cachedirname(cachedirname)

    def _pythonpath_for_cachedirname(cachedirname):
        pkgi = self.pkgcacheinfo['pkgcaches'][cachedirname]
        if pkgi.get('pkg_subdir', None):
            return os.path.join(self._fullcachedir(cachedirname),
                                *list(pkgi['pkg_subdir'].split('/')))
        return self._fullcachedir(cachedirname)

