# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2019 by Philippe Faist                                       #
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

#import re
import logging

#
# Transform "John Doe", "J. Doe", or possible variations thereof into a
# specified string or LaTeX command
#

from pybtex.database import Person #, Entry
from pybtex.utils import OrderedCaseInsensitiveDict

from bibolamazi.core.bibfilter import BibFilter
from bibolamazi.core.bibfilter.argtypes import enum_class

logger = logging.getLogger(__name__)


def normnamelist(xl):
    return [ x.strip(' \t\r\n.').upper() for x in xl ]

def getnameinitial(x):
    # x is the value returned from normnamelist([ first, names ])
    return x[0][0] if x else ''


# possible modes in which to operate
MATCHMODE_EXACT = 0
MATCHMODE_INITIAL = 1
MATCHMODE_PARTIAL = 2

# All these defs are useful for the GUI
MatchMode = enum_class(
    'MatchMode',
    [
        ('exact', MATCHMODE_EXACT),
        ('initial', MATCHMODE_INITIAL),
        ('partial', MATCHMODE_PARTIAL),
    ],
    default_value=MATCHMODE_INITIAL
)


HELP_AUTHOR = r"""
Philippe Faist, (C) 2019, GPL 3+
"""

HELP_DESC = r"""
Change an author name to a specified LaTeX string or macro.
"""

HELP_TEXT = r"""
This filter searches for the given author in all bibtex entries, and replaces
that author name by a given custom LaTeX string or macro. This way, one can
emphasize a specific author in an entire bibliography, which can be useful in
proposals or CVs.

The -sReplaceBy argument is the LaTeX string or macro that is inserted at the
place of all matches of the given author. (It is still parsed as a person for
technical reasons, so you might need to protect the content of this argument in
braces; e.g. "``Doe, John''" is better specified as "{``Doe, John''}" to avoid a
bib style rendering this as "John'' ``Doe".)

The -sMatchMode argument specifies how strictly the author name matching is
performed.  Three modes are possible:

  - 'exact': In this case, only authors with the exact first names are matched
             and replaced.

  - 'initial': Authors with an initial only which matches the given first
             name(s) also match; for instance "J. Doe" and "J Doe" are also
             matched and converted to the specified replacement string.

  - 'partial': A partial first name is also matched, e.g., "Al. Einstein" is
             also matched if we specify -sName="Albert Einstein".

In any case, middle names are disregarded, as are suffixes ("Jr") etc.
"""



class MarkAuthorFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, name, replace_by, match_mode=MATCHMODE_INITIAL):
        r"""
        Arguments:

          - name: The author name to match, specified as "Doe, John" or "John
                  Doe".

          - replace_by: The string to replace the given author by.  This can be
                  any LaTeX content, such as "\emph{John Doe}" or "\johndoe".

          - match_mode(MatchMode): Specify how to match the first name; may be
                 one of 'exact', 'initial' (the default), or 'partial'.
        """
        self.markname = name
        self.replace_by = replace_by
        self.matchmode = MatchMode(match_mode)

        self.person = Person(self.markname)

        self.last_names_normed = normnamelist(self.person.get_part('last'))
        self.first_names_normed = normnamelist(self.person.get_part('first'))
        self.first_names_normed_joined = " ".join(self.first_names_normed)
        self.first_initial = getnameinitial(self.first_names_normed)

        match_fns = { MATCHMODE_EXACT: self._match_name_exact,
                      MATCHMODE_INITIAL: self._match_name_initial,
                      MATCHMODE_PARTIAL: self._match_name_partial }

        self.match_fn = match_fns[self.matchmode.value]

        super().__init__()


    def _match_name_exact(self, p):
        return normnamelist(p.get_part('last')) == self.last_names_normed and \
            normnamelist(p.get_part('first')) == self.first_names_normed

    def _match_name_initial(self, p):
        return normnamelist(p.get_part('last')) == self.last_names_normed and (
            normnamelist(p.get_part('first')) == self.first_names_normed or
            "".join(normnamelist(p.get_part('first'))) == self.first_initial # exact initial given
        )

    def _match_name_partial(self, p):
        return normnamelist(p.get_part('last')) == self.last_names_normed and \
            self.first_names_normed_joined.startswith(" ".join(normnamelist(p.get_part('first'))))


    def _filter_person(self, p):
        if self.match_fn(p):
            # note, create a different Person instance for each
            # replacement. This is in case further filters change individual
            # entries again, to make sure that there aren't any weird side
            # effects
            return Person(self.replace_by)
        return p


    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY

    def filter_bibentry(self, entry):

        # write debug messages, which are seen in verbose mode
        logger.longdebug("markauthor filter: filtering entry %s", entry.key)

        # set the field field_name to the given value:
        for role, persons in OrderedCaseInsensitiveDict(entry.persons).items():
            entry.persons[role] = [ self._filter_person(p) for p in persons ]

        logger.longdebug("PhF filter: Done for %s", entry.key)


def bibolamazi_filter_class():
    return MarkAuthorFilter
