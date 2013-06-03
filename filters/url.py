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

from core.butils import getbool;
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

# for the arxiv info parser tool
import arxiv;


HELP_AUTHOR = u"""\
URLs filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Remove or add URLs from entries according to given rules, e.g. whether DOI or ArXiv ID are present
"""

HELP_TEXT = """
This filter removes or adds URLs to/from entries according to certain given
rules. Please see the documentation for each option above for details about
what the rule performs. Each rule may be set or removed individually. By
default, performs the rules Strip, StripAllIfDoiOrArxiv, StripDoiUrl and
StripArxivUrl.
"""


class UrlNormalizeFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, Strip=True, StripAllIfDoiOrArxiv=True, StripDoiUrl=True, StripArxivUrl=True,
                 UrlFromDoi=False, UrlFromArxiv=False):
        """UrlNormalizeFilter constructor.

        *Strip: Removes all URLs from the entry. Maybe add URLs according to the other options.
        *StripAllIfDoiOrArxiv: Removes all URLs from the entry, but only if a DOI identifier or an ArXiv ID
                               is present.
        *StripDoiUrl: Remove any URL that is in fact a DOI lookup, i.e. of the form
                      http://dx.doi.org/<DOI>
        *StripArxivUrl: Remove any URL that looks like an arxiv lookup, i.e. of the
                        form http://arxiv.org/abs/<ID>
        *UrlFromDoi: If the entry has a DOI identifier, then add an explicit URL that is a DOI lookup,
                     i.e. http://dx.doi.org/<DOI>
        *UrlFromArxiv: If the entry has an ArXiv identifier, then add an explicit URL that links to the
                       arXiv page, i.e. http://arxiv.org/abs/<ARXIV-ID>
        """
        BibFilter.__init__(self);

        self.strip = getbool(Strip);
        self.stripallifdoiorarxiv = getbool(StripAllIfDoiOrArxiv);
        self.stripdoiurl = getbool(StripDoiUrl);
        self.striparxivurl = getbool(StripArxivUrl);
        self.urlfromdoi = getbool(UrlFromDoi);
        self.urlfromarxiv = getbool(UrlFromArxiv);

        logger.debug('url filter constructor')
        

    def name(self):
        return "URL clean-up"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        
        if (self.strip and 'url' in entry.fields):
            del entry.fields['url'];

        #logger.debug("Stripped 'url' entry from field=%r", entry.fields);

        arxivinfo = arxiv.getArXivInfo(entry);

        if ('url' in entry.fields):
            urls = entry.fields['url'].split();
        else:
            urls = [];

        if (self.stripallifdoiorarxiv):
            if ('doi' in entry.fields or arxivinfo is not None):
                entry.fields.pop('url', None)

        if (self.stripdoiurl):
            for url in urls:
                if re.match(r'^http://dx.doi.org/', url):
                    urls.remove(url);
            if (len(urls)):
                entry.fields['url'] = " ".join(urls);
            else:
                entry.fields.pop('url', None)

        if (self.striparxivurl):
            for url in urls:
                if re.match(r'^http://arxiv.org/abs/', url):
                    urls.remove(url);
            if (len(urls)):
                entry.fields['url'] = " ".join(urls);
            else:
                entry.fields.pop('url', None)

        if (self.urlfromdoi):
            if ('doi' in entry.fields):
                urls.append("http://dx.doi.org/"+entry.fields['doi']);
                entry.fields['url'] = " ".join(urls);

        if (self.urlfromarxiv):
            if (arxivinfo is not None):
                urls.append("http://arxiv.org/abs/"+arxivinfo['arxivid']);
                entry.fields['url'] = " ".join(urls);

        return entry


def get_class():
    return UrlNormalizeFilter;

