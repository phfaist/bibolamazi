

import re

from pybtex.database import Person

from core.butils import getbool;
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

# for the arxiv info parser tool
import arxiv;


HELP_TEXT = """

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

    helpdescription = "Name Initials filter: Turn full first names into initials only in all entries."
    helptext = HELP_TEXT;

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

