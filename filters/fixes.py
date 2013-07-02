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

from pybtex.database import Person

from core.bibfilter import BibFilter, BibFilterError
from core.blogger import logger
from core import butils
from core import latexencode


HELP_AUTHOR = u"""\
Fixes filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Fixes filter: perform some various known fixes for bibtex entries
"""

HELP_TEXT = u"""
Perform some various fixes for bibtex entries.

For now, the implemented fixes are:

  -dFixSwedishA
    Changes "\\AA berg" to "\\AA{}berg" to prevent revtex from inserting a
    blank after the "\\AA". (This fix is needed for, e.g., the bibtex that
    Mendeley generates)

  -dEncodeUtf8ToLatex
    Encodes non-ascii special characters, e.g. accented characters, into LaTeX
    equivalents. This affects ALL fields of the bibliographic entry.
"""



class FixesFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, fix_swedish_a=False, encode_utf8_to_latex=False):
        """
        Constructor method for FixesFilter
        
        *fix_swedish_a: transform `\\AA berg' into `\\AA{}berg' (the former is generated e.g. by Mendeley
                        automatically); revtex tends to insert a blank after the `\\AA' otherwise.
        *encode_utf8_to_latex: encode all non-ascii characters into latex escape sequences.
        """
        
        BibFilter.__init__(self);

        self.fix_swedish_a = butils.getbool(fix_swedish_a);
        self.encode_utf8_to_latex = butils.getbool(encode_utf8_to_latex);

        logger.debug('fixes filter: fix_swedish_a=%r; encode_utf8_to_latex=%r'
                     % (self.fix_swedish_a, self.encode_utf8_to_latex));
        

    def name(self):
        return "Fixes filter"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #


        def thefilter(x):
            if (self.fix_swedish_a):
                x = re.sub(r'\\AA\s+', r'\AA{}', x);
            if (self.encode_utf8_to_latex):
                x = latexencode.utf8tolatex(x, non_ascii_only=True);
            return x

        def filter_person(p):
            return Person(string=thefilter(unicode(p)));
            # does not work this way because of the way Person() splits at spaces:
            #parts = {}
            #for typ in ['first', 'middle', 'prelast', 'last', 'lineage']:
            #    parts[typ] = thefilter(u" ".join(p.get_part(typ)));
            #return Person(**parts);

        for (role,perslist) in entry.persons.iteritems():
            for k in range(len(perslist)):
                entry.persons[role][k] = filter_person(perslist[k]);
        
        for (k,v) in entry.fields.iteritems():
            entry.fields[k] = thefilter(v);

        return entry;
    

def get_class():
    return FixesFilter;

