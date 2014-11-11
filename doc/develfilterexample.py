
import random # for example purposes

# core filter classes
from core.bibfilter import BibFilter, BibFilterError
# types for passing arguments to the filter
from core.bibfilter.argtypes import CommaStrList, enum_class
# use this for logging output
from core.blogger import logger
# utility to parse boolean values
from core.butils import getbool


# --- help texts ---

HELP_AUTHOR = u"""\
Test Filter by Philippe Faist, (C) 2014, GPL 3+
"""

HELP_DESC = u"""\
Test Filter: adds a 'testFilter' field to all entries, with various values.
"""

HELP_TEXT = u"""
There are three possible operating modes:

    "empty"  -- add an empty field 'testField' to all entries.
    "random" -- the content of the 'testField' field which we add to all entries is
                completely random.
    "fixed"  -- the content of the 'testField' field which we add to all entries is
                a hard-coded, fixed string. Surprise!

Specify which operating mode you prefer with the option '-sMode=...'. By default,
"random" mode is assumed.
"""

# --- operating modes ---

MODE_EMPTY = 0
MODE_RANDOM = 1
MODE_FIXED = 2

# All these defs are useful for the GUI
_modes = [
    ('empty', MODE_EMPTY),
    ('random', MODE_RANDOM),
    ('fixed', MODE_FIXED),
    ]

# our Mode type
Mode = enum_class('Mode', _modes, default_value=MODE_NONE, value_attr_name='mode')

# --- the filter object itself ---

class MyTestFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, mode="random"):
        """
        Constructor method for TestFilter. Note that this part of the constructor
        docstring itself isn't that useful, but the argument list below is parsed and used
        by the default automatic option parser for filter arguments. So document your
        arguments! If your filter accepts **kwargs, you may add more arguments below than
        you explicitly declare in your constructor prototype.

        Arguments:
          - mode(Mode): the operating mode to adopt
        """
        
        BibFilter.__init__(self);

        self.mode = Mode(mode);

        logger.debug('test filter constructor: mode=%s', self.mode)

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def requested_cache_accessors(self):
        # return the requested cache accessors here if you are using the cache mechanism. 
        # This also applies if you are using the `arxivutil` utilities.
        return [ ]

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        
        if self.mode == MODE_EMPTY:
            entry.fields['testField'] = ''
            return

        if self.mode == MODE_RANDOM:
            entry.fields['testField'] = random.randint(0, 999999)
            return

        if self.mode == MODE_FIXED:
            entry.fields['testField'] = (
                u"On d\u00E9daigne volontiers un but qu'on n'a pas r\u00E9ussi "
                u"\u00E0 atteindre, ou qu'on a atteint d\u00E9finitivement. (Proust)"
                )
        
        raise BibFilterError('testfilter', "Unknown operating mode: %s" % mode );



def bibolamazi_filter_class():
    return MyTestFilter;



