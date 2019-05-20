#
# bibolamazi filter example
#

from __future__ import print_function, absolute_imports, unicode_literals

import random # for example purposes

# use this for logging output
import logging
logger = logging.getLogger(__name__)

# core filter classes
from bibolamazi.core.bibfilter import BibFilter, BibFilterError
# types for passing arguments to the filter
from bibolamazi.core.bibfilter.argtypes import CommaStrList, enum_class
# utility to parse boolean values
from bibolamazi.core.butils import getbool


# --- help texts ---

HELP_AUTHOR = r"""
Test Filter by Philippe Faist, (C) 2014, GPL 3+
"""

HELP_DESC = r"""
Test Filter: adds a 'testFilter' field to all entries, with various values.
"""

HELP_TEXT = r"""
There are three possible operating modes:

    "empty"  -- add an empty field 'testField' to all entries.

    "random" -- the content of the 'testField' field which we add to all
                entries is completely random.

    "fixed"  -- the content of the 'testField' field which we add to all
                entries is a hard-coded, fixed string. Surprise!

Specify which operating mode you prefer with the option '-sMode=...'. By
default, "random" mode is assumed.
"""

# --- operating modes ---

# Here we define a custom enumeration type for passing as argument to
# our constructor. By doing it this way, instead of simply accepting a
# string, allows the filter factory mechanism to help us report errors
# and provide more helpful help messages. Also, in the graphical
# interface the relevant option is presented as a drop-down list
# instead of a text field.

# numerical values -- numerical values just have to be different
MODE_EMPTY = 0
MODE_RANDOM = 1
MODE_FIXED = 2

# symbolic names and to which values they correspond
_modes = [
    ('empty', MODE_EMPTY),
    ('random', MODE_RANDOM),
    ('fixed', MODE_FIXED),
    ]

# our Mode type. See `bibolamazi.core.bibfilter.argtypes`
Mode = enum_class('Mode', _modes, default_value=MODE_NONE,
                  value_attr_name='mode')


# --- the filter object itself ---

class MyTestFilter(BibFilter):

    # import help texts above here
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, mode="random", use_uppercase_text=False):
        r"""
        Constructor method for TestFilter.

        Note that this part of the constructor docstring itself isn't
        that useful, but the argument list below is parsed and used by
        the default automatic option parser for filter arguments. So
        document your arguments! If your filter accepts `**kwargs`,
        you may add more arguments below than you explicitly declare
        in your constructor prototype.

        If this function accepts `*args`, then additional positional
        arguments on the filter line will be passed to those
        args. (And not to the declared arguments.)

        Arguments:

          - mode(Mode): the operating mode to adopt

          - use_uppercase_text(bool): if set to True, then transform
            our added text to uppercase characters.
        """
        
        BibFilter.__init__(self)

        self.mode = Mode(mode)
        self.use_uppercase_text = getbool(use_uppercase_text)

        # debug log messages are seen by the user in verbose output mode
        logger.debug('my filter constructor: mode=%s, uppercase=%s',
                     self.mode, self.use_uppercase_text)

    def action(self):
        # Here, we want the filter to operate entry-by-entry (so the
        # function `self.filter_bibentry()` will be called). If we had
        # preferred to operate on the whole bibliography database in
        # one go (as, e.g., for the `duplicates` filter), then we
        # would have to return `BibFilter.BIB_FILTER_BIBOLAMAZIFILE`
        # here, and provide a `filter_bibolamazifile()` method.
        #
        return BibFilter.BIB_FILTER_SINGLE_ENTRY

    def requested_cache_accessors(self):
        # return the requested cache accessors here if you are using
        # the cache mechanism.  This also applies if you are using the
        # `arxivutil` utilities.
        return [ ]

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        
        if self.mode == MODE_EMPTY:
            entry.fields['testField'] = ''

        elif self.mode == MODE_RANDOM:
            entry.fields['testField'] = random.randint(0, 999999)

        elif self.mode == MODE_FIXED:
            entry.fields['testField'] = (
                "On d\u00E9daigne volontiers un but qu'on n'a pas "
                "r\u00E9ussi \u00E0 atteindre, ou qu'on a atteint "
                "d\u00E9finitivement. (Proust)"
                )
        else:
            #
            # Errors can be reported by raising exceptions
            #
            raise BibFilterError('testfilter',
                                 "Unknown operating mode: {}".format(mode))

        if self.use_uppercase_text:
            entry.fields['testField'] = entry.fields['testField'].toupper()

        return

#
# Every Python module which defines a filter (except for "easy-style"
# filters) should have the following method.  This returns the filter
# class type, which is expected to be a `BibFilter` subclass.
#
def bibolamazi_filter_class():
    return MyTestFilter

