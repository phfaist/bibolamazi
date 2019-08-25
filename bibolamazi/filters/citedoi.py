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

import re
#import sys
#import os
#import os.path
import io
import warnings
import logging
logger = logging.getLogger(__name__)

import requests

#from pybtex.database import BibliographyData
import pybtex.database.input.bibtex as inputbibtex

from bibolamazi.core.bibfilter import BibFilter #, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList
from bibolamazi.core.bibusercache import BibUserCacheAccessor
#from bibolamazi.core.butils import getbool

from .util import auxfile



# ------------------------------------------------------------------------------
# Fetcher & cache manager
# ------------------------------------------------------------------------------



rx_doi = re.compile(r'^10\.[0-9a-zA-Z._+-]+/.+$')



class DoiOrgFetchedInfoCacheAccessor(BibUserCacheAccessor):
    """
    A `BibUserCacheAccessor` for fetching and accessing information obtained
    from doi.org.
    """
    def __init__(self, **kwargs):
        super().__init__(
            cache_name='doi_org_fetched_info',
            **kwargs
            )
        # we will parse & store keys, see parse_and_remember_key() below. The dictionary
        # key is the sanitized key, i.e. the key without the possible user's comment
        self.user_keys_parsed = {}

    def initialize(self, cache_obj, **kwargs):
        dic = self.cacheDic()
        dic.setdefault('fetched', {})

        logger.debug("doi_org_fetched_info: adding validation checker; time valid is %r",
                     cache_obj.cacheExpirationTokenChecker().time_valid)

        # validate each entry with an expiration checker. Do this per entry, rather than
        # globally on the full cache. (So don't use installCacheExpirationChecker())
        dic['fetched'].set_validation(cache_obj.cacheExpirationTokenChecker())

    def fetchDoiInfo(self, doilist):
        """
        This function performs a query to doi.org, to obtain a list of references
        described by `keyslist`.

        The argument `doilist` should be any iterable yielding DOIs.

        Only those requested entries which are not already in the cache are fetched.
        """

        cache_entrydic = self.cacheDic()['fetched']

        missing_keys = []
        for doi in doilist:
            if doi not in missing_keys and \
               (doi not in cache_entrydic or cache_entrydic.get(doi) is None):
                missing_keys.append(doi)

        if not missing_keys:
            logger.longdebug('nothing to fetch: no missing keys')
            # nothing to fetch
            return True

        logger.info("citedoi: Fetching missing information from doi.org ...")

        # use a Session() so that we keep the connection alive and reuse it multiple times
        # for the different requests
        with requests.Session() as reqsession:

            # Header: Accept: application/x-bibtex  -- to get the bibtex entry
            reqsession.headers.update({ 'Accept': 'application/x-bibtex; charset=utf-8' })

            logger.longdebug('fetching missing doi list %r', missing_keys)

            r = None
            for doi in missing_keys:
                # perform individual request
                logger.longdebug("requesting bibtex entry for doi %s", doi)
                for tries in range(5):
                    try:
                        exc = None
                        url = 'https://doi.org/' + doi

                        with warnings.catch_warnings():
                            # ignore ResourceWarning: unclosed <socket.socket ...>
                            warnings.simplefilter("ignore", ResourceWarning)

                            r = reqsession.get(url)

                    except Exception as e:
                        # meant to catch SSLError -- we can't rely on
                        #    ``from requests.packages.urllib3.exceptions import SSLError``
                        # because that doesn't always exist, depending on the `requests`
                        # version/edition/installation
                        logger.debug("Got exception in requests(), tries=%d: %s", tries, e)
                        exc = e
                        continue
                    break
                if exc is not None:
                    raise exc
                if r.status_code != 200:
                    logger.warning("Could not fetch reference information for key '%s' (HTTP %d):\n\t%s",
                                   doi, r.status_code, r.text)
                    continue

                bibtex = r.text.strip()
                if not bibtex:
                    logger.warning("Could not fetch reference for DOI '%s': no content returned", doi)
                    continue

                cache_entrydic[doi]['bibtex'] = bibtex

        logger.longdebug("citedoi info: Got all references. cacheDic() is now:  %r", self.cacheDic())
        logger.longdebug("... and cacheObject().cachedic is now:  %r", self.cacheObject().cachedic)

        return True


    def getDoiInfo(self, doi):
        """
        Returns a dictionary::

            {
              'bibtex': <bibtex string>
            }

        for the given DOI `doi` in the cache.  If the information is not in the
        cache, returns `None`.

        Don't forget to first call :py:meth:`fetchDoiInfo()` to retrieve the
        information in the first place.

        If the reference does not exist in the cache, `None` is returned.
        """
        return self.cacheDic()['fetched'].get(doi, None)




# ------------------------------------------------------------------------------




HELP_AUTHOR = r"""
Philippe Faist, (C) 2019, GPL 3+
"""

HELP_DESC = r"""
Automatically collect bibtex entries from DOIs for citations of the form
\cite{doi:10.1103/PhysRev.47.777}
"""

HELP_TEXT = r"""

This filter scans a LaTeX document for citations of the form '\cite{doi:<DOI>}'
and adds the corresponding bibtex items in the combined bibtex database. The
bibtex entry is generated by querying doi.org; you of course need internet
access for this.

The citations are searched for in LaTeX document with the same base name as the
bibolamazi file.  For instance, if the bibolamazi file is called
"mydocument.bibolamazi.bib", we expect the LaTeX document to be in the same
directory and called "mydocument.tex".  If you would like to scan the citations
of a document that is named differently, you should provide the jobname (file
base name) of the LaTeX document using the -sJobname= option.

Note that the AUX file ("mydocument.aux") is actually scanned, and not the LaTeX
document itself; this means that you need to run (Pdf)LaTeX *before* running
bibolamazi.

If the "mydocument.aux" file is in a different directory than the bibolamazi
file, you may specify where to look for the aux file with the option
`-sSearchDirs=...'.

"""


class CiteDoiFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, jobname, search_dirs=[], prefix="doi"):
        r"""
        CiteDoiFilter constructor.

        Arguments:

          - jobname: the base name of the latex file whose citations we should
              analyze. Will search for jobname.aux and look for '\citation{..}'
              commands as they are generated by latex.  The corresponding AUX
              file is searched for and analyzed.  If -sJobname is not specified,
              then the LaTeX file name is guessed from the bibolamazi file name,
              as for the only_used filter and the duplicates filter.

          - search_dirs(CommaStrList): the .aux file will be searched for in
              this list of directories; separate directories with commas
              e.g. 'path/to/dir1,path/to/dir2'.  Paths are absolute or relative
              to bibolamazi file.

          - prefix: Specify custom prefix for citations key, citations should be
              in the the form '\cite{<prefix>:<DOI>}' (default: 'doi')
        """

        super().__init__()

        self.jobname = jobname
        self.search_dirs = CommaStrList(search_dirs)
        self.prefix = prefix

        if not self.search_dirs:
            self.search_dirs = ['.', '_cleanlatexfiles'] # also for my cleanlatex utility :)

        logger.debug('citearxiv: jobname=%r', jobname)


    def getRunningMessage(self):
        return "citedoi: parsing & fetching relevant DOI citations ..."

    
    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE

    def requested_cache_accessors(self):
        return [
            DoiOrgFetchedInfoCacheAccessor
            ]

    def filter_bibolamazifile(self, bibolamazifile):

        doiorg_accessor = self.cacheAccessor(DoiOrgFetchedInfoCacheAccessor)

        #
        # find and analyze jobname.aux. Look for \citation{...}'s and collect them.
        #

        doi_uselist = []

        def add_to_cite_list(citekey):

            citekeyorig = citekey

            # ignore any key that does not have the correct prefix
            if self.prefix:
                if not citekey.startswith(self.prefix+":"):
                    return
                citekey = citekey[len(self.prefix)+1:]

            # strip "--comment" from the user's citekey
            citekey = re.sub(r'--.*$', '', citekey)

            if not rx_doi.match(citekey):
                # this is not a DOI
                if self.prefix:
                    # but it was given with a prefix, like doi:, so raise a warning:
                    logger.warning("Key '%s' does not look like a DOI", citekeyorig)
                return

            # citekey is a DOI
            doi = citekey
            if doi not in doi_uselist:
                doi_uselist.append( (citekeyorig, doi) )

            
        jobname = auxfile.get_action_jobname(self.jobname, bibolamazifile)

        auxfile.get_all_auxfile_citations(jobname, bibolamazifile,
                                          filtername=self.name(),
                                          search_dirs=self.search_dirs,
                                          return_set=False,
                                          callback=add_to_cite_list,
                                          )
        
        #
        # Now, fetch all bib entries that we need.
        #

        # if there are missing ids, fetch them
        if doi_uselist:
            doiorg_accessor.fetchDoiInfo( (doi for citekey, doi in doi_uselist) )

        #
        # Now, include all the entries in citearxiv_uselist
        #
        # Variable bibdata is a pybtex.database.BibliographyData object
        #

        thebibdata = bibolamazifile.bibliographyData()

        citekeys_done = []

        for citekey, doi in doi_uselist:

            if citekey in citekeys_done:
                continue

            info = doiorg_accessor.getDoiInfo(doi)
            logger.debug("Parsing info for %r (-> %r)", citekey, doi)

            # parse bibtex
            parser = inputbibtex.Parser()
            new_bib_data = None
            with io.StringIO(str(info['bibtex'])) as stream:
                new_bib_data = parser.parse_stream(stream)
            
            # and add them to the main list
            thelen = len(new_bib_data.entries.keys())
            if thelen != 1:
                logger.warning("Got %d!=1 bibtex entry(ies) when retreiving DOI '%s'!", thelen, doi)

            _, entry = list(new_bib_data.entries.items())[0]
            thebibdata.add_entry(citekey, entry)

            citekeys_done.append(citekey)

        #
        # yay, done!
        #
        
        return


def bibolamazi_filter_class():
    return CiteDoiFilter

