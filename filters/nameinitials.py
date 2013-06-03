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

from core.butils import getbool;
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

# for the arxiv info parser tool
import arxiv;


HELP_AUTHOR = u"""\
Name Initials filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""
Name Initials filter: Turn full first names into only initials for all entries.
"""

HELP_TEXT = u"""
In all entries, turn the first and middle names of people into initials.

This filter does not take any options. Any additional arguments given are interpreted
as roles to consider (see pybtex API), one or more among ['author', 'editor'] (WARNING:
EXPERIMENTAL), e.g.

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

    def __init__(self, *roles):
        BibFilter.__init__(self);

        self.roles = roles;
        if not self.roles:
            self.roles = ['author'];

        logger.debug('NameInitialsFilter constructor')
        

    def name(self):
        return "Name to Initials"

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
                pnew = Person('', " ".join(p.first(True)), " ".join(p.middle(True)), " ".join(p.prelast(True)),
                              " ".join(p.last()), " ".join(p.lineage()));
                entry.persons[role][k] = pnew
                #logger.debug("nameinitials: %r became %r" % (p, pnew));

        return entry


def get_class():
    return NameInitialsFilter;

