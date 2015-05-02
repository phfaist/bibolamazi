################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2013 by Philippe Faist                                       #
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
import logging
logger = logging.getLogger(__name__)

from bibolamazi.core.butils import getbool;
from bibolamazi.core.bibfilter import BibFilter, BibFilterError;

# for the arxiv info parser tool
from .util import arxivutil


HELP_AUTHOR = u"""\
URLs filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Remove or add URLs from entries according to given rules, e.g. whether DOI or ArXiv ID are present
"""

HELP_TEXT = """
This filter removes or adds URLs to/from entries according to certain given
rules. Please see the documentation for each option above for details about
what the rule performs. Each rule may be set or removed individually.
"""


class UrlNormalizeFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, Strip=False, StripAllIfDoiOrArxiv=False, StripDoiUrl=True, StripArxivUrl=True,
                 UrlFromDoi=False, UrlFromArxiv=False, KeepFirstUrlOnly=False, StripForTypes=None):
        """UrlNormalizeFilter constructor.

        Arguments:
          - Strip(bool): Removes all URLs from the entry. Maybe add URLs according to the other options.
                         [default: False]
          - StripAllIfDoiOrArxiv(bool): Removes all URLs from the entry, but only if a DOI identifier or
                         an ArXiv ID is present. [default: False]
          - StripDoiUrl(bool): Remove any URL that is in fact a DOI lookup, i.e. of the form
                         `http://dx.doi.org/<DOI>`  [default: True]
          - StripArxivUrl(bool): Remove any URL that looks like an arxiv lookup, i.e. of the
                         form `http://arxiv.org/abs/<ID>`  [default: True]
          - UrlFromDoi(bool): If the entry has a DOI identifier, then add an explicit URL that is a DOI
                         lookup, i.e. `http://dx.doi.org/<DOI>`  [default: False]
          - UrlFromArxiv(bool): If the entry has an ArXiv identifier, then add an explicit URL that links
                         to the arXiv page, i.e. `http://arxiv.org/abs/<ARXIV-ID>`  [default: False]
          - KeepFirstUrlOnly(bool): If the entry has several URLs, then after applying all the other
                         stripping rules, keep only the first remaining URL, if any.  [default: False]
          - StripForTypes: strip all URLs specified for entries among the given list of types. Common
                         types to strip would be e.g. 'book' or 'phdthesis'.
        """
        BibFilter.__init__(self);

        self.strip = getbool(Strip);
        self.stripallifdoiorarxiv = getbool(StripAllIfDoiOrArxiv);
        self.stripdoiurl = getbool(StripDoiUrl);
        self.striparxivurl = getbool(StripArxivUrl);
        self.urlfromdoi = getbool(UrlFromDoi);
        self.urlfromarxiv = getbool(UrlFromArxiv);
        self.keepfirsturlonly = getbool(KeepFirstUrlOnly);
        self.stripfortypes = None;
        if (StripForTypes is not None):
            self.stripfortypes = [ x.strip()  for x in StripForTypes.split(',') ];

        logger.debug('url filter constructor')
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def prerun(self, bibolamazifile):
        arxivutil.setup_and_get_arxiv_accessor(self.bibolamaziFile())

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        arxivinfo = self.cacheAccessor(arxivutil.ArxivInfoCacheAccessor).getArXivInfo(entry.key);

        # --- prepare urls[] list ---
        if ('url' in entry.fields):
            urls = entry.fields['url'].split();
        else:
            urls = [];

        logger.longdebug("%s: Urls is initially %r; arxivinfo=%r", entry.key, urls, arxivinfo)

        # --- filter the urls[] list ---
        
        if (self.strip):
            urls = []

        if (self.stripfortypes is not None and entry.type in self.stripfortypes):
            urls = []

        #logger.longdebug("%s: urls is now  %r", entry.key, urls)

        if (self.stripallifdoiorarxiv):
            if ('doi' in entry.fields or arxivinfo is not None):
                #entry.fields.pop('url', None)
                urls = []

        #logger.longdebug("%s: urls is now  %r", entry.key, urls)

        if (self.stripdoiurl):
            for url in urls:
                if re.match(r'^http://dx.doi.org/', url):
                    urls.remove(url);

        #logger.longdebug("%s: urls is now  %r", entry.key, urls)

        if (self.striparxivurl):
            for url in urls:
                if re.match(r'^http://arxiv.org/abs/', url):
                    urls.remove(url);

        #logger.longdebug("%s: urls is now  %r", entry.key, urls)

        if (self.urlfromdoi):
            if ('doi' in entry.fields):
                urls.append("http://dx.doi.org/"+entry.fields['doi']);

        #logger.longdebug("%s: urls is now  %r", entry.key, urls)

        if (self.urlfromarxiv):
            if (arxivinfo is not None):
                urls.append("http://arxiv.org/abs/"+arxivinfo['arxivid']);

        #logger.longdebug("%s: urls is now  %r", entry.key, urls)

        if (self.keepfirsturlonly):
            if (urls):
                urls[1:] = []
                
        logger.longdebug("%s: Urls is now %r", entry.key, urls)

        # --- reformat the entry as needed, according to the modified urls[] list, and return it ---

        if (urls):
            entry.fields['url'] = " ".join(urls);
        else:
            entry.fields.pop('url', None)

        return


def bibolamazi_filter_class():
    return UrlNormalizeFilter;

