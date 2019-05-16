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
import collections
import zipfile

import github
import requests

import bibolamazi.init
import bibolamazi.pkgfetcher as pkgfetcher

logger = logging.getLogger(__name__)


# github URLs are of the form:
#
# github:phfaist/bib2enxml  (default branch)
# github:phfaist/bib2enxml/<branch or tag or commit>
#
#
# TODO:
# githubgist:phfaist/gist_name



rx_github_path = re.compile(r'''
(?P<username>[a-zA-Z0-9_.-]+)
  / (?P<repo>[a-zA-Z0-9_.-]+)
  (?: / (?P<commit>[a-zA-Z0-9_.+-]+) )?
''' flags=re.VERBOSE)


class Fetcher(object):
    def __init__(self, username, repo, commit=None):
        super(Fetcher, self).__init__()
        self.username = username
        self.repo = repo
        self.commit = commit

        self.G = github.Github()
        self.R = self.G.get_repo(self.username + '/' + self.repo)
        
        if self.commit:
            self.effective_commit = self.commit
        else:
            self.effective_commit = self.R.default_branch

        self.C = self.R.get_commit(self.effective_commit)

        self.sha = self.C.sha


    def check_cache_is_up_to_date(self, provider_data):

        cached_shacommit = provider_data['cached_shacommit']
        
        return cached_shacommit == self.sha


    def fetch_to_dir(self, fullcachedir):

        zip_url = self.R.get_archive_link('zipball', self.sha)

        # this should also work for private repositories as the URL should
        # include necessary tokens apparently
        # (https://developer.github.com/v3/repos/contents/#get-archive-link)
        r = requests.get(zip_url, allow_redirects=True)
        
        dnlzipfile = os.path.join(fullcachedir, self.sha+'.zip')
        with open(dnlzipfile, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

        # extract zip file
        xtractdir = os.path.join(fullcachedir, self.sha)
        with zipfile.ZipFile(dnlzipfile, "r") as zip_ref:
            zip_ref.extractall(xtractdir)

        pkg_subdir = self.sha

        # if all files are within a subdir provided by the github api, include that, too:
        xtract_contents_root = os.listdir(os.path.join(fullcachedir, pkg_subdir))
        if len(xtract_contents_root) == 1:
            pkg_subdir += '/' + xtract_contents_root[0]
            

        if os.path.isdir(os.path.join(fullcachedir, pkg_subdir, self.repo)):
            pkg_subdir += '/' + self.repo

        provider_data = {
            'cached_shacommit': self.sha
        }

        return pkg_subdir, provder_data




class GithubUrlPkgProvider(object):
    def __init__(self):
        super(GithubUrlPkgProvider, self).__init__()

    def can_provide_from(self, scheme):
        return (scheme == 'github')

    def get_fetcher(self, url):
        
        p = urlparse(url)
        if p.scheme != 'github':
            raise ValueError("GithubUrlPkgProvider can only handle \"github:<...>\" urls")
        if p.host:
            raise ValueError("GithubUrlPkgProvider can only fetch repos on github.com "
                             "and you cannot provide a host name in the URL.")
        m = rx_github_path.match(p.path)
        if not m:
            raise ValueError("Can't parse github pseudo-path: {}".format(p.path))
        
        return Fetcher(**m.groupdict())
