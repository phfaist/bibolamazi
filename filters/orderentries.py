
import os
import os.path
import re
import codecs

from pybtex.database import BibliographyData;


from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;


HELP_AUTHOR = u"""\
Order entries filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Order bibliographic entries in bibtex file
"""

HELP_TEXT = u"""
This filter orders the entries in the bibtex file, alphabetically according to
citation key.

This is particularly useful for keeping the bibtex file in a VCS (git, svn etc.)
and getting relevant diffs.
"""


# modes
ORDER_RAW = 0
ORDER_CITATION_KEY_ALPHA = 1


class OrderEntriesFilter(BibFilter):

    helpauthor = HELP_AUTHOR
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
        return "orderentries"

    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE;

    def getRunningMessage(self):
        return "%s: Processing %d entries" %(self.name(), len(self.bibolamaziFile().bibliographydata().entries))

    def filter_bibolamazifile(self, bibolamazifile):
        #
        # bibdata is a pybtex.database.BibliographyData object
        #

        logger.debug("ordering entries according to mode=%r." %(self.ordermode));

        if (self.ordermode == ORDER_CITATION_KEY_ALPHA):
            
            bibdata = bibolamazifile.bibliographydata();

            #newentries = sorted(bibdata.entries.iteritems(), key=lambda x: x[0].lower())
            entries = bibdata.entries;

            # bibdata.entries is of type pybtex.util.OrderedCaseInsensitiveDict, which has
            # an attribute `order`, which is a list of keys in the relevant order. So use
            # list.sort(), which is more efficient.
            bibdata.entries.order.sort()

            #newbibdata = BibliographyData(entries=newentries);
            #bibolamazifile.setBibliographyData(newbibdata);

        else:
            if (self.ordermode != ORDER_RAW):
                logger.error("Bad order mode: %r !" %(self.ordermode));
                
            # don't do anything: natural order.
            
        logger.debug("ordered entries as wished.");

        return


def bibolamazi_filter_class():
    return OrderEntriesFilter;

