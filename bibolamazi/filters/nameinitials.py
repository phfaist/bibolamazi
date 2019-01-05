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

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr


import re
import logging
logger = logging.getLogger(__name__)

from pybtex.database import Person
from pybtex.textutils import abbreviate
from pybtex.bibtex.utils import split_tex_string

from pylatexenc import latexwalker
from pylatexenc.latex2text import LatexNodes2Text

from bibolamazi.core.butils import getbool
from bibolamazi.core.bibfilter import BibFilter, BibFilterError


HELP_AUTHOR = u"""\
Name Initials filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""
Name Initials filter: Turn full first names into only initials for all entries.
"""

HELP_TEXT = u"""
In all entries, turn the first and middle names of people into initials.

Warning: this filter only works well with the option -dNamesToUtf8, which is by
default. If you want LaTeX-formatted names, use the filter `fixes' again
afterwards with the option -dEncodeUtf8ToLatex.

The additional positional arguments which may be provided are interpreted as
roles to consider, one or more among ['author', 'editor']. E.g.:

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

    def __init__(self, only_single_letter_firsts=False, names_to_utf8=True,
                 only_one_initial=False, strip_first_names=False, *roles):
        """
        Arguments:

          - only_single_letter_firsts(bool): Make proper initials (e.g. C. H. Bennett)
            only if the entry itself only has initials. This is useful if your entries
            don't contain the proper punctuation (e.g. C H Bennett). (default: False)

          - names_to_utf8(bool): Convert LaTeX escapes to UTF-8 characters in names in
            bib file. (default: True)

          - only_one_initial(bool): Keep only the first initial, removing any
            middle names.  For instance, "P. A. M. Dirac" ->
            "P. Dirac". (default: False)

          - strip_first_names(bool): Only keep last names and strip first/middle
            names entirely.

        """
        BibFilter.__init__(self)

        self.roles = roles
        if not self.roles:
            self.roles = ['author']

        self._names_to_utf8 = getbool(names_to_utf8)
        self._only_single_letter_firsts = getbool(only_single_letter_firsts)
        self._only_one_initial = getbool(only_one_initial)
        self._strip_first_names = getbool(strip_first_names)

        logger.debug('NameInitialsFilter constructor')
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        for role in self.roles:
            if role not in entry.persons:
                continue

            for k in range(len(entry.persons[role])):

                p = entry.persons[role][k]

                ### NO: this kills any protection, e.g., with braces, etc.
                #
                # # de-latex the person first
                # pstr = unicodestr(p)
                # # BUG: FIXME: remove space after any macros
                # pstr = re.sub(r'(\\[a-zA-Z]+)\s+', r'\1{}', pstr) # replace "blah\macro blah" by "blah\macro{}blah"
                #if (self._names_to_utf8):
                #    pstr = latex2text.latex2text(pstr)
                #
                #p = Person(pstr)

                if self._names_to_utf8:
                    # delatex everything to UTF-8, but honor names protected by braces and keep those
                    rxmacrospace = re.compile(r'(\\[a-zA-Z]+)\s+')
                    l2t = LatexNodes2Text(keep_braced_groups=True, strict_latex_spaces=True)
                    protected_detex_fn = lambda x: l2t.latex_to_text(rxmacrospace.sub(r'\1{}', x)).strip()

                    # join name again to correctly treat accents like "Fran\c cois" or "\AA berg"
                    p = Person(protected_detex_fn(unicodestr(p)))

                    # do_detex = lambda lst: [ protected_detex(x) for x in lst ]
                    # p.first_names = do_detex(p.first_names)
                    # p.middle_names = do_detex(p.middle_names)
                    # p.prelast_names = do_detex(p.prelast_names)
                    # p.last_names = do_detex(p.last_names)
                    # p.lineage = do_detex(p.lineage_names)


                if self._only_single_letter_firsts:
                    do_abbrev = lambda x: abbreviate(x) if len(x) == 1 else x
                else:
                    do_abbrev = abbreviate

                first_names = p.first_names
                middle_names = p.middle_names
                if self._only_one_initial:
                    first_names = first_names[0:1]
                    middle_names = []
                if self._strip_first_names:
                    first_names = []
                    middle_names = []

                pnew = Person(string='',
                              first=" ".join([do_abbrev(x)  for x in first_names]),
                              middle=" ".join([do_abbrev(x)  for x in middle_names]),
                              prelast=" ".join(p.prelast_names),
                              last=" ".join(p.last_names),
                              lineage=" ".join(p.lineage_names))

                entry.persons[role][k] = pnew
                #logger.debug("nameinitials: %r became %r" % (p, pnew))

        return


def bibolamazi_filter_class():
    return NameInitialsFilter

