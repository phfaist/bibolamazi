################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2014 by Philippe Faist                                       #
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
from core.pylatexenc import latexencode
from core.pylatexenc import latex2text


HELP_AUTHOR = u"""\
Extra useless test filter by Philippe Faist, (C) 2014, GPL 3+
"""

HELP_DESC = u"""\
Be decorative. And do nothing special.
"""

HELP_TEXT = u"""
No help available for dummy filter :)
"""



class UselessFixesFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, fix_swedish_a=False, encode_utf8_to_latex=False, encode_latex_to_utf8=False,
                 remove_type_from_phd=False, remove_full_braces=False, protect_names=None,
                 remove_file_field=False):
        """
        Constructor method for a useless filter.
        """
        
        BibFilter.__init__(self);

        self.fix_swedish_a = butils.getbool(fix_swedish_a);

        self.encode_utf8_to_latex = butils.getbool(encode_utf8_to_latex);
        self.encode_latex_to_utf8 = butils.getbool(encode_latex_to_utf8);

        if (self.encode_utf8_to_latex and self.encode_latex_to_utf8):
            raise FilterError("Conflicting options: `encode_utf8_to_latex' and `encode_latex_to_utf8'.");

        self.remove_type_from_phd = butils.getbool(remove_type_from_phd);

        try:
            self.remove_full_braces = butils.getbool(remove_full_braces);
            self.remove_full_braces_fieldlist = None; # all fields
        except ValueError:
            # not boolean, we have provided a field list.
            self.remove_full_braces = True;
            self.remove_full_braces_fieldlist = [ x.strip().lower() for x in remove_full_braces.split(',') ];

        if protect_names is not None:
            self.protect_names = dict([ (x.strip(), re.compile(r'\b'+x.strip()+r'\b', re.IGNORECASE))
                                        for x in protect_names.split(',') ]);
        else:
            self.protect_names = None;

        self.remove_file_field = butils.getbool(remove_file_field);


        logger.debug('useless test filter: fix_swedish_a=%r; encode_utf8_to_latex=%r; encode_latex_to_utf8=%r; '
                     'remove_type_from_phd=%r; '
                     'remove_full_braces=%r [fieldlist=%r], protect_names=%r, remove_file_field=%r'
                     % (self.fix_swedish_a, self.encode_utf8_to_latex, self.encode_latex_to_utf8,
                        self.remove_type_from_phd,
                        self.remove_full_braces, self.remove_full_braces_fieldlist, self.protect_names,
                        self.remove_file_field));
        

    def name(self):
        return "extrafilter"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        # first apply filters that are applied to all fields of the entry

        def thefilter(x):
            if (self.fix_swedish_a):
                x = re.sub(r'\\AA\s+', r'\AA{}', x);
            if (self.encode_utf8_to_latex):
                x = latexencode.utf8tolatex(x, non_ascii_only=True);
            if (self.encode_latex_to_utf8):
                x = latex2text.latex2text(x);
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


        # additionally:

        def filter_entry_remove_type_from_phd(entry):
            if (entry.type != 'phdthesis' or 'type' not in entry.fields):
                return
            if ('phd' in re.sub(r'[^a-z]', '', entry.fields['type'].lower())):
                # entry is phd type, so remove explicit type={}
                del entry.fields['type'];
            
        if (self.remove_type_from_phd):
            filter_entry_remove_type_from_phd(entry);


        def filter_entry_remove_full_braces(entry, fieldlist):
            for k,v in entry.fields.iteritems():
                if (fieldlist is None or k in fieldlist):
                    val = v.strip();
                    if (len(val) and val[0] == '{' and val[-1] == '}'):
                        # remove the extra braces.
                        entry.fields[k] = val[1:-1];

        if (self.remove_full_braces):
            filter_entry_remove_full_braces(entry, self.remove_full_braces_fieldlist);


        def filter_protect_names(entry):
            for key, val in entry.fields.iteritems():
                if key in ('url', 'file'):
                    continue
                newval = val;
                for n,r in self.protect_names.iteritems():
                    newval = r.sub('{'+n+'}', newval);
                if (newval != val):
                    entry.fields[key] = newval;

        if (self.protect_names):
            filter_protect_names(entry);


        if (self.remove_file_field):
            if ('file' in entry.fields):
                del entry.fields['file'];

        return entry;
    

def bibolamazi_filter_class():
    return UselessFixesFilter;

