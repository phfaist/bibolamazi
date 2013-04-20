
import re


from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;
from core import butils;


HELPDESC = u"""
Fixes filter: perform some various known fixes for bibtex entries
"""

HELPTEXT = u"""
Perform some various fixes for bibtex entries.

For now, the only implemented fix is
  -dFixSwedishA
that changes "\\AA berg" to "\\AA{}berg" to prevent revtex from inserting a blank after the "\\AA".

"""



class FixesFilter(BibFilter):
    
    helpdescription = HELPDESC;
    helptext = HELPTEXT;

    def __init__(self, fix_swedish_a=False):
        """
        Constructor method for FixesFilter
        
        *fix_swedish_a: transform `\\AA berg' into `\\AA{}berg' (the former is generated e.g. by Mendeley
                        automatically); revtex tends to insert a blank after the `\\AA' otherwise.
        """
        
        BibFilter.__init__(self);

        self.fix_swedish_a = butils.getbool(fix_swedish_a);

        logger.debug('fixes filter: fix_swedish_a=%r' % (self.fix_swedish_a));
        

    def name(self):
        return "Fixes filter"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        # ### BUG: perform substitution in persons, too!!!
        
        for (k,v) in entry.fields.iteritems():
            entry.fields[k] = re.sub(r'\\AA\s+', r'\AA{}', v);

        return entry;
    

def getclass():
    return FixesFilter;

