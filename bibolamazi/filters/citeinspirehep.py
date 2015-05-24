################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2015 by Philippe Faist & Romain Mueller                      #
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
import os
import os.path
import io
import logging
logger = logging.getLogger(__name__)

import requests
from bs4 import BeautifulSoup

from pybtex.database import BibliographyData
import pybtex.database.input.bibtex as inputbibtex
import arxiv2bib # arxiv id regex'es

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList
from bibolamazi.core.bibusercache import BibUserCacheAccessor
from bibolamazi.core.butils import getbool

from .util import auxfile



# ---- API info ------



class InspireHEPFetchedAPIInfoCacheAccessor(BibUserCacheAccessor):
    """
    A `BibUserCacheAccessor` for fetching and accessing information retrieved from the
    Inspire-HEP API.
    """
    def __init__(self, **kwargs):
        super(InspireHEPFetchedAPIInfoCacheAccessor, self).__init__(
            cache_name='inspirehep_fetched_api_info',
            **kwargs
            )
        # we will parse & store keys, see parse_and_remember_key() below. The dictionary
        # key is the sanitized key, i.e. the key without the possible user's comment
        self.user_keys_parsed = {}

    def initialize(self, cache_obj, **kwargs):
        dic = self.cacheDic()
        dic.setdefault('fetched', {})

        logger.debug("inspirehep_fetched_api_info: adding validation checker; time valid is %r",
                     cache_obj.cacheExpirationTokenChecker().time_valid)

        # validate each entry with an expiration checker. Do this per entry, rather than
        # globally on the full cache. (So don't use installCacheExpirationChecker())
        dic['fetched'].set_validation(cache_obj.cacheExpirationTokenChecker())
        

    def parse_and_store_key(self, userkey):
        """
        Parse the given user citation key: see if it is a valid citeinspirehep citation
        scheme, and remember the parsed information for later querying the online API
        information.

        Returns the \"sanitized\" key (without comment) if the `userkey` was successfully
        parsed as an InspireHEP request, or `None` if this is not the case.

        This does not store any information in the actual cache, just for this session.
        """

        def invenio_query(term, value):
            return term + ":" + value

        def remember_key(userkey, key, p):
            self.user_keys_parsed[key] = {
                'key': key,
                'userkey': userkey,
                'p_query': p,
                }

        # strip "--comment" from the user's citekey
        key = re.sub(r'--.*$', '', userkey)

        if key.startswith('inspire:'):
            key = key[len('inspire:'):].strip()
            # allow also single-quote `'` char for "'t Hooft"
            allowedchars = r"A-Za-z0-9_.'-"
            if re.match(r'[^'+allowedchars+r']', key):
                # Report error rather than removing the spaces and special characters,
                # otherwise the user might spend hours figuring out why "PhysRev 47 777"
                # doesn't work (because it would have been collapsed to "PhysRev47777")
                logger.warning("Key `%s' may not contain any characters other than `%s'", key, allowedchars)
                return None
            ref_type = None
            queryval = key

            # auto detect reference type
            if re.search(r'^.*\:\d{4}\w\w\w?$', key):
                ref_type = 'texkey'
                queryval = '"'+queryval+'"'
            elif re.search(arxiv2bib.OLD_STYLE, key):
                ref_type = 'eprint'
            elif re.search(arxiv2bib.NEW_STYLE, key):
                ref_type = 'eprint'
            elif re.search(r'^[.\w]+[+][.\w]+[+][.\w]+$', key):
                ref_type = 'j'
                # don't understand why this (was in code from inspire's
                # websubmit/Bibtex.py). Doesn't allow to encode e.g. "Phys.Rev.,47,777"
                #queryval = key.replace('.', ',') # --??
                # PhF: so the format now is simply to replace every `+` by a comma in the
                # inspire request.
                queryval = key.replace('+', ',')
            elif re.search(r'^ISBN-.*', key):
                ref_type = 'isbn'
                queryval = key[len('ISBN-'):]
            elif re.search(r'^10[.][0-9]{3,}(?:[.][0-9]+)*/.*', key):
                ref_type = 'doi'
            elif re.search(r'\w\-\w', key):
                # ### PhF: there doesn't seem to be any standard format for report
                # ### numbers. Let's keep this general regexp for now, and hope it doesn't
                # ### clash with anything else. Keep this elif: last before the else:.
                ref_type = 'r'
            else:
                logger.warning("Could not guess reference type for key `%s'", key)
                return None

            logger.longdebug("resolved %s to reftype=%r (queryval=%r)", key, ref_type, queryval)
            
            # NOTE: The returned `key` must identify uniquely the given entry. So it may
            # be different from the queryval.

            # all keys can be saved in the same way using INSPIRE
            remember_key(userkey, key=key, p=invenio_query(ref_type, queryval))
            return key

        return None

    def fetchInspireHEPApiInfo(self, keyslist):
        """
        This function performs a query on the inspirehep.net API, to obtain a list of
        references described by `keyslist`.

        The argument `keyslist` should be any iterable yielding strings with the format
        'some.sort.of.identifier.99' which serves to identify the specific reference. 
        (Sanitized keys)

        Only those requested entries which are not already in the cache are fetched.
        """

        cache_entrydic = self.cacheDic()['fetched']

        missing_keys = []
        for key in keyslist:
            if (key not in cache_entrydic or cache_entrydic.get(key) is None):
                missing_keys.append(key)

        if not missing_keys:
            logger.longdebug('nothing to fetch: no missing keys')
            # nothing to fetch
            return True

        logger.info("citeinspirehep: Fetching missing information from InspireHEP...")

        # use a Session() so that we keep the connection alive and reuse it multiple times
        # for the different requests
        reqsession = requests.Session()

        logger.longdebug('fetching missing id list %r' %(missing_keys))
        for key in missing_keys:
            pk = self.user_keys_parsed[key]
            qs = { 'p': pk['p_query'],
                   'em': 'B', # no surrounding HTML
                   'of': 'hx', # BibTeX output
                   'action_search': 'search',
                   }
            # perform individual request
            logger.longdebug("fetching for key=%s: %r", key, qs)
            for tries in range(5):
                try:
                    exc = None
                    r = reqsession.get('https://inspirehep.net/search', params=qs)
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
                logger.warning("Could not fetch reference information for key `%s' (HTTP %d):\n\t%s",
                               key, r.status_code, r.text)
                continue

            soup = BeautifulSoup(r.text)
            quicknotes = soup.find_all(class_='quicknote')
            if (quicknotes):
                logger.warning("Could not fetch reference for key `%s':\n\t%s", key,
                               "\n".join([x.get_text() for x in quicknotes]))
                continue

            # extract bibtex
            bibtex = "\n".join([x.get_text() for x in soup.find_all('pre')])
            if not bibtex:
                logger.warning("Could not fetch reference for key `%s': no content returned", key)
                continue
            
            cache_entrydic[key]['bibtex'] = bibtex

        logger.longdebug("inspirehep API info: Got all references. cacheDic() is now:  %r", self.cacheDic())
        logger.longdebug("... and cacheObject().cachedic is now:  %r", self.cacheObject().cachedic)

        return True


    def getInspireHEPInfo(self, key):
        """
        Returns a dictionary::

            {
              'bibtex': <bibtex string>
            }

        for the given InspireHEP key in the cache. If the information is not in the cache,
        returns `None`.

        Don't forget to first call :py:meth:`fetchInspireHEPApiInfo()` to retrieve the
        information in the first place.

        If the reference does not exist in the cache, `None` is returned.
        """
        return self.cacheDic()['fetched'].get(key, None)




HELP_AUTHOR = u"""\
Cite Inspire-HEP References filter by Philippe Faist & Romain M\u00FCller, (C) 2015, GPL 3+
"""

HELP_DESC = u"""\
Filter that fills BibTeX files with relevant entries to cite with e.g. 
\cite{inspire:PhysRev.47.777--EPR+paper}
"""

HELP_TEXT = u"""\
This filter scans a LaTeX document for citations of the form
\cite{inspire:some-form-of-identifier.99} or \cite{inspire:some-form-of-identifier.99--some-comment} and
adds the corresponding bibtex items in the combined bibtex database. The bibtex entry is
generated by querying the INSPIRE-HEP API information; you of course need internet access
for this.

The general form of the identifiers is: 

    'inspire:<id>'

where the possible identifiers <id> are:

    - hep-th/0001001 or 1408.4546 or any eprint number / arXiv ID which is known to
      INSPIRE-HEP (the `archive/' prefix may be omitted for new-style arXiv ids)

    - PHRVA+D66+010001 or any journal reference in INSPIRE' citation form (Note the 
      periods separating the pieces!)

    - Phys.Rev.+47+777 or any journal reference using typical abbreviations for 
      the journal name

    - Hagiwara:2002fs or any INSPIRE LaTeX/bibtex key for the paper

Journal references of the form `<Journal.Abbrev.>+<volume>+<page>' are translated to the
inspire.hep request `j:<Journal.Abbrev.>,<volume>,<page>'.

The optional '--some-comment' may help you remember which reference you meant, e.g. 
'PhysRev.47.777--EPR-paper'. If, in addition, you use the 'duplicates' filter, then you
don't even need to worry about different ways to refer to the same paper.

You should provide the base file name of the LaTeX document, e.g. if your document is
named `mydoc.tex', then you should specify the option `-sJobname=mydoc'. Note that the AUX
file (`mydoc.aux') is actually scanned, and not the LaTeX document itself; this means that
you need to run (Pdf)LaTeX *before* running bibolamazi. This also means that your document
may be spread across several latex source files; you only have to specify the master
document name.

If the `mydoc.aux' file is in a different directory than the bibolamazi file, you may
specify where to look for the aux file with the option `-sSearchDirs=...'.

Example of recognized citations:

    \cite{inspire:10.1103/PhysRev.47.777}
    \cite{inspire:10.1103/PhysRev.47.777--EPR-paper}
    \cite{inspire:1408.4546}
    \cite{inspire:1305.1258--WWgg}
    \cite{inspire:Nakamura:2010zzi}

"""



class CiteInspireHEPFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, jobname, search_dirs=[]):
        """CiteInspireHEPFilter constructor.

        Arguments:
          - jobname: the base name of the latex file. Will search for jobname.aux and look
              for `\citation{..}' commands as they are generated by latex.
          - search_dirs(CommaStrList): the .aux file will be searched for in this list of
              directories; separate directories with commas e.g. 'path/to/dir1,path/to/dir2'
              (escape commas and backslashes with a backslash)
        """

        BibFilter.__init__(self);

        self.jobname = jobname
        self.search_dirs = CommaStrList(search_dirs)

        if (not self.search_dirs):
            self.search_dirs = ['.', '_cleanlatexfiles'] # also for my cleanlatex utility :)

        logger.debug('citeinspirehep: jobname=%r' % (jobname,));


    def getRunningMessage(self):
        return u"citeinspirehep: parsing & fetching relevant InspireHEP citations ..."


    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE;

    def requested_cache_accessors(self):
        return [
            InspireHEPFetchedAPIInfoCacheAccessor
            ]

    def filter_bibolamazifile(self, bibolamazifile):

        cache_accessor = self.cacheAccessor(InspireHEPFetchedAPIInfoCacheAccessor)

        # dictionary of { userkey: key }
        used_keys_dic = {}

        #
        # find and analyze jobname.aux. Look for \citation{...}'s and collect them.
        #

        def add_to_cite_list(userkey):
            key = cache_accessor.parse_and_store_key(userkey)
            if key is None:
                # didn't recognize citation, skip.
                return

            used_keys_dic[userkey] = key
            return
                
        auxfile.get_all_auxfile_citations(self.jobname, bibolamazifile,
                                          filtername=self.name(),
                                          search_dirs=self.search_dirs,
                                          return_set=False,
                                          callback=add_to_cite_list,
                                          )
        
        #
        # Now, fetch all bib entries that we need.
        #
        if used_keys_dic:
            cache_accessor.fetchInspireHEPApiInfo(used_keys_dic.values())

        #
        # Now, include all the entries in used_keys_dic
        #
        # Variable thebibdata is a pybtex.database.BibliographyData object
        #
        thebibdata = bibolamazifile.bibliographyData();

        for (userkey, key) in used_keys_dic.iteritems():
            # get the bibtex data
            dat = cache_accessor.getInspireHEPInfo(key)

            # parse bibtex
            parser = inputbibtex.Parser()
            new_bib_data = None
            with io.StringIO(unicode(dat['bibtex'])) as stream:
                new_bib_data = parser.parse_stream(stream);
            
            # and add them to the main list
            if (len(new_bib_data.entries.keys()) != 1):
                logger.warning("Got either none or more than one bibtex entry when retreiving `%s'!", userkey)

            for val in new_bib_data.entries.values():
                thebibdata.add_entry(userkey, val);

        #
        # yay, done!
        #
        
        return


def bibolamazi_filter_class():
    return CiteInspireHEPFilter;

