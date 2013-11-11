
import os
import os.path
import re
import codecs

from pybtex.database import BibliographyData;


from core import bibfilter
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;


HELP_AUTHOR = u"""\
Order entries filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Order bibliographic entries in bibtex file
"""

HELP_TEXT = u"""
This filter orders the entries in the bibtex file.

Possible ordering modes are:

  - 'raw'
    doesn't change the ordering--leaves the natural order.
  
  - 'alphabetical'
    Orders all the entries in the bibtex file alphabetically according to the citation key.


This is particularly useful for keeping the bibtex file in a VCS (git, svn etc.)
and getting relevant diffs between different revisions.
"""


# modes
ORDER_RAW = 0
ORDER_CITATION_KEY_ALPHA = 1


OrderMode = bibfilter.enum_class('OrderMode', [('raw', ORDER_RAW),
                                               ('alphabetical', ORDER_CITATION_KEY_ALPHA)],
                                 default_value='alphabetical',
                                 value_attr_name='ordermode')



class OrderEntriesFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT
    
    
    def __init__(self, order=None):
        """
        Arguments:
          - order(OrderMode): The strategy according to which to order all the entries. Possible
                values: see below.
        """
        BibFilter.__init__(self);

        self.order = OrderMode(order)

        logger.debug('orderentries: self.order=%r' % self.order);

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

        logger.debug("ordering entries according to mode=%r." %(self.order));

        if (self.order == ORDER_CITATION_KEY_ALPHA):
            
            bibdata = bibolamazifile.bibliographydata();

            #newentries = sorted(bibdata.entries.iteritems(), key=lambda x: x[0].lower())
            entries = bibdata.entries;

            # bibdata.entries is of type pybtex.util.OrderedCaseInsensitiveDict, which has
            # an attribute `order`, which is a list of keys in the relevant order. So use
            # list.sort(), which is slightly more efficient.
            bibdata.entries.order.sort()

            #newbibdata = BibliographyData(entries=newentries);
            #bibolamazifile.setBibliographyData(newbibdata);

        elif (self.order == ORDER_RAW):
            # natural order mode. don't do anything.
            pass
        else:
            raise BibFilterError(self.name(), "Bad order mode: %r !" %(self.order));
            
        logger.debug("ordered entries as wished.");

        return


def bibolamazi_filter_class():
    return OrderEntriesFilter;

