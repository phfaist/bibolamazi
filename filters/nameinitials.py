

import re

from pybtex.database import Person

from core.butils import getbool;
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

# for the arxiv info parser tool
import arxiv;



class NameInitialsFilter(BibFilter):
    
    helptext = "";

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


def getclass():
    return NameInitialsFilter;

