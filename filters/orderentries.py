
import os
import os.path
import re
import codecs

from pybtex.database import BibliographyData;


from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;


HELP_DESC = """\
Order bibliographic entries in bibtex file
"""

HELP_TEXT = """

This filter orders the entries in the bibtex file, alphabetically according to
citation key.

This is particularly useful for keeping the bibtex file in a VCS (git, svn etc.)
and getting relevant diffs.
"""


# modes
ORDER_RAW = 0
ORDER_CITATION_KEY_ALPHA = 1


class OrderEntriesFilter(BibFilter):

    helpdescription = HELP_DESC
    helptext = HELP_TEXT
    
    
    def __init__(self, citation_key_alpha=None):
        BibFilter.__init__(self);

        if (citation_key_alpha is None):
            citation_key_alpha = True

        if (citation_key_alpha):
            self.ordermode = ORDER_CITATION_KEY_ALPHA
        else:
            self.ordermode = ORDER_RAW

        logger.debug('orderentries: self.ordermode=%r' % self.ordermode);

    def name(self):
        return "order bibtex entries"

    def action(self):
        return BibFilter.BIB_FILTER_BIBFILTERFILE;


    def filter_bibfilterfile(self, bibfilterfile):
        #
        # bibdata is a pybtex.database.BibliographyData object
        #

        bibdata = bibfilterfile.bibliographydata();

        logger.debug("ordering entries according to mode=%r." %(self.ordermode));

        if (self.ordermode == ORDER_CITATION_KEY_ALPHA):
            newentries = sorted(bibdata.entries.iteritems(), key=lambda x: x[0].lower())

        else:
            if (self.ordermode != ORDER_RAW):
                logger.error("Bad order mode: %r !" %(self.ordermode));
                
            newentries = bibdata.entries.iteritems();
            

        newbibdata = BibliographyData(entries=newentries);

        logger.debug("ordered entries as wished.");

        bibfilterfile.setBibliographyData(newbibdata);

        return


def get_class():
    return OrderEntriesFilter;

