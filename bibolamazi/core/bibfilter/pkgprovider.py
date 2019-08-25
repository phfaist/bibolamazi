# -*- coding: utf-8 -*-
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

import os
import os.path
import re
import logging
import datetime
import shutil
from urllib.parse import urlparse
import json
import hashlib

import appdirs


import bibolamazi.init
from bibolamazi.core.butils import BibolamaziError
# set up logger after bibolamazi.init
logger = logging.getLogger(__name__)


class UnknownPackageLocation(BibolamaziError):
    def __init__(self, url):
        super().__init__(
            "Unknown package location '{}'".format(url)
        )


max_cache_age = datetime.timedelta(days=365)
"""
A downloaded cache gets invalidated and removed after this amount of time.
"""

max_norecheck_age = datetime.timedelta(minutes=10)
"""
If we got a URL once, then don't re-check if it's good until this amount of
time has passed.  [Re-checking can be expensive and generate lots of requests to
a server for remote locations. We can especially run into the rate limits for
github API requests.]
"""


rx_valid_cachedirname = re.compile('^[-A-Za-z0-9_]+$')
rx_valid_subdirpart   = re.compile('^[-A-Za-z0-9_.]+$')


def default_pkg_providers():
    return [
        GithubUrlPkgProvider()
    ]


def datetime_to_str(dati):
    return dati.strftime('%Y-%m-%dT%H:%M:%S TZ=%z')

def datetime_from_str(s):
    if s is None:
        return datetime.datetime(2000,1,1)
    if ' ' in s:
        (sdt, stz) = s.split(' ')
    else:
        sdt = s
        stz = 'TZ='
    #
    if stz == 'TZ=': # empty time zone string
        return datetime.datetime.strptime(sdt, "%Y-%m-%dT%H:%M:%S")
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S TZ=%z")


class _FoundInCache(Exception):
    def __init__(self, cachedirname):
        self.cachedirname = cachedirname
        super().__init__('<found: {}>'.format(self.cachedirname))
        

class PackageProviderManager:
    def __init__(self, user_cache_dir=None):
        super().__init__()
        if user_cache_dir is None:
            user_cache_dir = appdirs.user_cache_dir("bibolamazi")
        self.user_cache_dir = user_cache_dir

        self.pkg_providers = []

        self.allow_remote = False

        # ensure the user cache directory itself exists
        if not os.path.isdir(self.user_cache_dir):
            os.makedirs(self.user_cache_dir, exist_ok=True)

        self.pkgcacheinfo = {
            #
            # self.pkgcacheinfo['pkgcaches'][cachedirname] is a dictionary with entries:
            #
            #     'cachedirname': cachedirname itself. this is the name (hex
            #     digits) of the directory in the user cache dir
            #
            #     'url': <str object>, the URL itself
            #
            #     'downloaded_datetime': <datetime.datetime str>, date/time of download
            #
            #     'lastchecked_datetime': <datetime.datetime str>, date/time of
            #     last time we checked that the download was up-to-date
            #
            #     'pkg_subdir': <str>, the relative path from inside this cache
            #     dir to the python package directory itself, i.e., in which the
            #     __init__.py file is found.  The filter package name is the
            #     basename of this path.
            #
            #     'provider_data': <any JSON object>, any data that the
            #     PackageProvider might which to associate with this cache dir
            #
            'pkgcaches': {}
        }

        self._load_pkgcacheinfo()

        #
        # Perform some start-up checks
        #
        pkgs_to_remove = [] # (cachedirname, also-delete-cache-dir)
        for cachedirname, pkgi in self.pkgcacheinfo['pkgcaches'].items():
            #
            # check that the cache directory still exists (!!) [Maybe removed by
            # user directly?]
            #
            if not os.path.isdir(self._fullcachedir(cachedirname)):
                # directory no longer exists.  Remove from cache-info.
                pkgs_to_remove.append( (cachedirname, False) )
                continue

            #
            # check to see if this caches is very old
            #
            pkgi_datetime = datetime_from_str(pkgi.get('downloaded_datetime', None))
            if (datetime.datetime.now() - pkgi_datetime) > max_cache_age:
                logger.debug("Removing cached package %s which was downloaded on %s",
                             cachedirname, pkgi_datetime)
                # don't remove right away, we're still iterating over the pkg info dict
                pkgs_to_remove.append( (cachedirname, True) )

        for (cachedirname, also_remove_dir) in pkgs_to_remove:
            if also_remove_dir:
                self._rmcachedir(cachedirname)
            else:
                del self.pkgcacheinfo['pkgcaches'][cachedirname]
                self._save_pkgcacheinfo()
        
    def registerPackageProvider(self, pkg_provider):
        self.pkg_providers.append(pkg_provider)

    def remoteAllowed(self):
        return self.allow_remote

    def allowRemote(self, on):
        self.allow_remote = on
    
    def _pkgcacheinfofile(self):
        return os.path.join(self.user_cache_dir, "pkgcacheinfo.json")

    def _load_pkgcacheinfo(self):
        pkgcacheinfofile = self._pkgcacheinfofile()
        if os.path.exists(pkgcacheinfofile):
            try:
                with open(pkgcacheinfofile) as f:
                    self.pkgcacheinfo = json.load(f)
            except (OSError,json.JSONDecodeError):
                logger.debug("Couldn't read pkg cache info JSON file, ignoring it...")

    def _save_pkgcacheinfo(self):
        pkgcacheinfofile = self._pkgcacheinfofile()
        with open(pkgcacheinfofile, 'w') as f:
            json.dump(self.pkgcacheinfo, f, indent=4)


    def _fullcachedir(self, cachedirname):
        return os.path.join(self.user_cache_dir, cachedirname)

    def _rmcachedir(self, cachedirname):
        logger.longdebug("_rmcachedir(%r)", cachedirname)
        assert self.user_cache_dir and os.path.isdir(self.user_cache_dir)
        assert rx_valid_cachedirname.match(cachedirname)
        assert cachedirname in self.pkgcacheinfo['pkgcaches']

        fullcachedir = self._fullcachedir(cachedirname)
        logger.debug("Removing pkg cache directory %s", fullcachedir)

        shutil.rmtree(fullcachedir)

        del self.pkgcacheinfo['pkgcaches'][cachedirname]
        self._save_pkgcacheinfo()

    def _createcachedir(self, cachedirname, url):
        logger.longdebug("_createcachedir(%r)", cachedirname)
        assert self.user_cache_dir and os.path.isdir(self.user_cache_dir)
        assert rx_valid_cachedirname.match(cachedirname)
        fullcachedir = self._fullcachedir(cachedirname)
        assert not os.path.exists(fullcachedir)

        os.mkdir(fullcachedir)
        
        str_now = datetime_to_str(datetime.datetime.now())
        d = {
            'cachedirname': cachedirname,
            'url': url,
            'downloaded_datetime': str_now,
            'lastchecked_datetime': str_now,
            'pkg_subdir': None,
            'provider_data': None,
        }
        self.pkgcacheinfo['pkgcaches'][cachedirname] = d
        self._save_pkgcacheinfo()


    def provide_for_url(self, url):
        """
        Find and fetch the package specified as the given `url` (provided as a
        string).

        Return a tuple (fpname, fpdir).
        """
        
        logger.debug("provide_for_url, url=%r", url)

        p = urlparse(url)

        if not p.scheme or p.scheme == 'file':
            # local filesystem directory
            fpname = os.path.basename(p.path)
            fpdir = os.path.dirname(p.path)
            return fpname, fpdir

        if not self.remoteAllowed():
            raise BibolamaziError("Remote filter packages were not explicitly allowed: {}".format(url))

        # do we have a recently-checked item in the cache already?
        try:
            for cachedirname, pkgi in self.pkgcacheinfo['pkgcaches'].items():
                if pkgi.get('url', None) == url:
                    lastcheck = datetime_from_str(pkgi.get('lastchecked_datetime', None))
                    if (datetime.datetime.now() - lastcheck) < max_norecheck_age:
                        logger.debug("Cached download %s was recently checked, using it.", cachedirname)
                        raise _FoundInCache(cachedirname)
        except _FoundInCache as f:
            # we have the cache directly, no need to go via a pkg-provider
            return self._filterpackagespec_for_cachedirname(f.cachedirname)

        logger.debug("Looking for providers for %s...", url)

        for pkg_provider in self.pkg_providers:
            if pkg_provider.can_provide_from(p.scheme):
                logger.debug("Using provider %s", pkg_provider.__class__.__name__)
                fetcher = pkg_provider.get_fetcher(url)
                return self._get_filterpackagespec_via_provider(fetcher, url, p)

        raise UnknownPackageLocation(url)

    def _get_filterpackagespec_via_provider(self, fetcher, url, p):

        # see if we have this URL in cache already
        try:
            for cachedirname, pkgi in self.pkgcacheinfo['pkgcaches'].items():
                if pkgi.get('url', None) == url:

                    try:
                        logger.debug("Checking whether or not existing cache for %s is up-to-date ...", url)
                        
                        if fetcher.check_cache_is_up_to_date(pkgi.get('provider_data', None)):

                            # if it's confirmed still up-to-date, then use it and
                            # record the fact that we checked now
                            str_now = datetime_to_str(datetime.datetime.now())
                            self.pkgcacheinfo['pkgcaches'][cachedirname]['lastchecked_datetime'] = str_now
                            self._save_pkgcacheinfo()

                            raise _FoundInCache(cachedirname)

                    except _FoundInCache:
                        raise

                    except Exception as e:
                        logger.warning("Unable to check whether or not cache for %s is up-to-date: %s",
                                       url, str(e))
                        raise _FoundInCache(cachedirname)

                    # this cache is out of date, so we should remove it.
                    self._rmcachedir(cachedirname)
                    break

        except _FoundInCache as f:
            return self._filterpackagespec_for_cachedirname(f.cachedirname)

        # we need to fetch the package using this provider

        digest = hashlib.md5(url.encode('utf-8') + b'\n' +
                             str(datetime.datetime.now()).encode('ascii')).hexdigest()
        cachedirname = 'pkg-' + digest[-16:]

        logger.longdebug("using cachedirname=%s", cachedirname)

        self._createcachedir(cachedirname, url)
        cachedir_created_ok = False
        try:
            pkg_subdir, provider_data = \
                fetcher.fetch_to_dir(self._fullcachedir(cachedirname))
            
            # pkg_subdir must be a relative sub-dir with forward-slashes on all
            # systems.  The basename of pkg_subdir is the filterpackage name.
            assert len(pkg_subdir) > 0
            assert pkg_subdir[0:1] != '/'
            for pdpart in pkg_subdir.split('/'):
                assert rx_valid_subdirpart.match(pdpart)

            self.pkgcacheinfo['pkgcaches'][cachedirname].update(
                pkg_subdir=pkg_subdir,
                provider_data=provider_data,
            )

            self._save_pkgcacheinfo()

            cachedir_created_ok = True
        finally:
            if not cachedir_created_ok:
                self._rmcachedir(cachedirname)

        return self._filterpackagespec_for_cachedirname(cachedirname)


    def _filterpackagespec_for_cachedirname(self, cachedirname):

        pkg_subdir = self.pkgcacheinfo['pkgcaches'][cachedirname]['pkg_subdir']

        path = os.path.join(self._fullcachedir(cachedirname),
                            *list(pkg_subdir.split('/')))

        fpname = os.path.basename(path)
        fpdir = os.path.dirname(path)

        return fpname, fpdir
