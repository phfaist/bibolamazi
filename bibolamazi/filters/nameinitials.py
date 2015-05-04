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

from pybtex.database import Person

from pylatexenc import latex2text;

from bibolamazi.core.butils import getbool;
from bibolamazi.core.bibfilter import BibFilter, BibFilterError;


HELP_AUTHOR = u"""\
Name Initials filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""
Name Initials filter: Turn full first names into only initials for all entries.
"""

HELP_TEXT = u"""
In all entries, turn the first and middle names of people into initials.

Warning: this filter only works well with the option -dNamesToUtf8, which is by
default. If you want LaTeX-formatted names, use the filter `fixes' AFTERWARDS
with the option -dEncodeUtf8ToLatex.

The additional positional arguments which may be provided are interpreted as
roles to consider (see pybtex API), one or more among ['author', 'editor']
(WARNING: EXPERIMENTAL), e.g.

  %% only process author fields
  nameinitials
  nameinitials author
  
  %% process author and editor fields
  nameinitials author editor
"""


class NameInitialsFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, only_single_letter_firsts=False, names_to_utf8=True, *roles, **kwargs):
        """
        Arguments:
          - only_single_letter_firsts(bool): Make proper initials (e.g. C. H. Bennett)
            only if the entry itself only has initials. This is useful if your entries
            don't contain the proper punctuation (e.g. C H Bennett). (default: False)
          - names_to_utf8(bool): Convert LaTeX escapes to UTF-8 characters in names in
            bib file. (default: True)
        """
        BibFilter.__init__(self);

        self.roles = roles;
        if not self.roles:
            self.roles = ['author'];

        self._names_to_utf8 = getbool(names_to_utf8)
        self._only_single_letter_firsts = getbool(only_single_letter_firsts)

        logger.debug('NameInitialsFilter constructor')
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        for role in self.roles:
            if role not in entry.persons:
                continue
            for k in range(len(entry.persons[role])):
                p = entry.persons[role][k];
                # de-latex the person first
                pstr = unicode(p);
                # BUG: FIXME: remove space after any macros
                pstr = re.sub(r'(\\[a-zA-Z]+)\s+', r'\1{}', pstr); # replace "blah\macro blah" by "blah\macro{}blah"
                if (self._names_to_utf8):
                    pstr = latex2text.latex2text(pstr)
                p = Person(pstr)
                if self._only_single_letter_firsts:
                    from pybtex.textutils import abbreviate
                    def getparts(p, x):
                        for part in p.get_part(x, False):
                            if len(part) == 1:
                                yield abbreviate(part)
                            else:
                                yield part
                    pnew = Person('', " ".join(getparts(p, 'first')), " ".join(getparts(p, 'middle')),
                                  " ".join(p.prelast()),
                                  " ".join(p.last()), " ".join(p.lineage()));
                else:
                    pnew = Person('', " ".join(p.first(True)), " ".join(p.middle(True)), " ".join(p.prelast()),
                                  " ".join(p.last()), " ".join(p.lineage()));
                entry.persons[role][k] = pnew
                #logger.debug("nameinitials: %r became %r" % (p, pnew));

        return


def bibolamazi_filter_class():
    return NameInitialsFilter;

