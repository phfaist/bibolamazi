################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2018 by Philippe Faist                                       #
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

from bibolamazi.core.butils import getbool
from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList

from pybtex.database import Person


HELP_AUTHOR = u"""\
Shorten-authors-etal filter by Philippe Faist, (C) 2018, GPL 3+
"""

HELP_DESC = u"""\
Shorten author list to a custom length and add "et al.", for standard BibTeX styles
"""

HELP_TEXT = """
This filter shortens long author lists (you can specify max length with
-sMaxNumAuthors=5) by instead "First author et al.".

While normally this should be handled by the bibtex style, standard bibtex
styles understand the author name "others" to be replaced by "et al.".  This
filter replaces long author lists (as determined by MaxNumAuthors) by "First
Author and others", which is then formatted as "First Author et al.".
"""


class ShortenAuthorsEtalFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, max_num_authors=5, num_keep_authors=1, apply_to_roles='author'):
        r"""

        Arguments:
        
          - max_num_authors(int): Maximum number of authors in list
            before "etal-ization".

          - num_keep_authors(int): If an author list is "etal-ized",
            then we keep this many authors before "et al.".  For example,
            if num_keep_authors=2, then the result for long author lists is
            "First Author, Second Author, et al."  (Note MaxNumAuthors
            still controls when the "etal-ization" occurs.)

          - apply_to_roles(CommaStrList): either "author", "editor" or
            "author,editor" to apply the "etal-ization" to author lists,
            editor lists, or to both.
        """
        super(ShortenAuthorsEtalFilter, self).__init__()

        self.max_num_authors = int(max_num_authors)
        self.num_keep_authors = int(num_keep_authors)
        self.apply_to_roles = CommaStrList(apply_to_roles)

        logger.debug('shorten_authors_etal filter constructor done')
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY


    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        for role in self.apply_to_roles:
            if not role in entry.persons:
                continue # no author/editor list
            if len(entry.persons[role]) > self.max_num_authors:
                # apply etal-ization
                entry.persons[role] = entry.persons[role][:self.num_keep_authors] + [Person('others')]

        return



def bibolamazi_filter_class():
    return ShortenAuthorsEtalFilter

