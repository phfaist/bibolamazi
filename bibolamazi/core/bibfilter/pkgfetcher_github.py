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
#import datetime
#import shutil
from urllib.parse import urlparse
#import json
#import collections
import zipfile

import github
import requests

import bibolamazi.init
from bibolamazi.core.butils import BibolamaziError

logger = logging.getLogger(__name__)


# github URLs are of the form:
#
# github:phfaist/bib2enxml    (-> use default branch)
# github:phfaist/bib2enxml/<branch or tag or commit>
#
#
# TODO: ??
# githubgist:phfaist/gist_name



rx_github_path = re.compile(r'''
(?P<username>[a-zA-Z0-9_.-]+)
  / (?P<repo>[a-zA-Z0-9_.-]+)
  (?: / (?P<commit>[a-zA-Z0-9_.+-]+) )?
''', flags=re.VERBOSE)


class Fetcher:
    def __init__(self, auth_token, username, repo, commit=None):
        super().__init__()
        self.auth_token = auth_token
        self.username = username
        self.repo = repo
        self.commit = commit

        self.effective_commit = None
        self.sha = None
        self.G = None
        self.R = None
        self.C = None

        # do the access stuff now, but only raise any exceptions in
        # check_cache_is_up_to_date() so that old cache can still correctly be
        # used ...
        try:
            if self.auth_token:
                self.G = github.Github(self.auth_token)
            else:
                self.G = github.Github()
            self.R = self.G.get_repo(self.username + '/' + self.repo)

            if self.commit:
                self.effective_commit = self.commit
            else:
                self.effective_commit = self.R.default_branch

            self.C = self.R.get_commit(self.effective_commit)

            self.sha = self.C.sha

            self.access_error = None
        except Exception as e:
            self.access_error = e

        logger.debug("Preparing to inspect and/or fetch filter package %s/%s [%s] (sha=%s)",
                     self.username, self.repo, self.effective_commit, self.sha)


    def check_cache_is_up_to_date(self, provider_data):

        if self.access_error is not None:
            raise self.access_error

        cached_shacommit = provider_data['cached_shacommit']
        
        if cached_shacommit == self.sha:
            logger.debug("Previously downloaded package was sha=%r and is up to date.",
                         cached_shacommit)
            return True

        logger.debug("Previously downloaded package was sha=%r but the URL points to sha=%r; "
                     "we'll need to re-download.", cached_shacommit, self.sha)
        return False


    def fetch_to_dir(self, fullcachedir):

        if self.access_error is not None:
            raise self.access_error

        zip_url = self.R.get_archive_link('zipball', self.sha)

        logger.info("Fetching filter package %s/%s [%s]", self.username, self.repo, self.effective_commit)

        logger.longdebug("Downloading zipball at %r ...", zip_url)

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

        # if all files are within a subdir provided by the github api, then
        # rename the directory into the package name, and include that, too:
        xtract_contents_root = os.listdir(os.path.join(fullcachedir, pkg_subdir))
        if len(xtract_contents_root) == 1:
            onlydir = xtract_contents_root[0]
            os.rename(os.path.join(fullcachedir, pkg_subdir, onlydir),
                      os.path.join(fullcachedir, pkg_subdir, self.repo))
            pkg_subdir += '/' + self.repo

        pkgname = self.repo.replace('-', '_')
        if not os.path.exists(os.path.join(fullcachedir, pkg_subdir, '__init__.py')) and \
           os.path.isdir(os.path.join(fullcachedir, pkg_subdir, pkgname)):
            # no __init__.py as a root file in the repo, and there exists a
            # subdir of the same name. So point to that.
            pkg_subdir += '/' + pkgname

        provider_data = {
            'cached_shacommit': self.sha
        }

        logger.longdebug("pkg_subdir=%r, provider_data=%r", pkg_subdir, provider_data)

        return pkg_subdir, provider_data




class GithubPackageProvider:
    def __init__(self, auth_token=None):
        super().__init__()
        self.auth_token = auth_token

    def setAuthToken(self, token):
        self.auth_token = token

    def getAuthToken(self):
        return self.auth_token

    def can_provide_from(self, scheme):
        return (scheme == 'github')

    def get_fetcher(self, url):

        logger.longdebug("Creating github instance fetcher for URL = %r", url)
        
        p = urlparse(url)
        if p.scheme != 'github':
            raise ValueError("GithubUrlPkgProvider can only handle \"github:<...>\" urls")
        if p.hostname:
            raise ValueError("GithubUrlPkgProvider can only fetch repos on github.com "
                             "and you cannot provide a host name in the URL.")
        m = rx_github_path.match(p.path)
        if not m:
            raise BibolamaziError("Can't parse github pseudo-path: {}".format(p.path))
        
        try:
            return Fetcher(auth_token=self.auth_token, **m.groupdict())
        except (requests.ConnectionError,github.GithubException) as e:
            raise BibolamaziError("Cannot retrieve github package: {}".format(e))
