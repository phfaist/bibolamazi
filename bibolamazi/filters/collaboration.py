# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2020 by Philippe Faist                                       #
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

#from bibolamazi.core.butils import getbool
from bibolamazi.core.bibfilter import BibFilter #, BibFilterError
from bibolamazi.core.bibfilter.argtypes import enum_class, CommaStrList

from pybtex.database import Person

from bibolamazi.filters.fixes import remove_full_braces


HELP_AUTHOR = r"""
Collaboration filter by Philippe Faist, (C) 2020, GPL 3+
"""

HELP_DESC = r"""
Use collaboration names (e.g. "LIGO Collaboration") instead of long author lists
"""

HELP_TEXT = r"""
Detect and use collaboration names (e.g. "LIGO Collaboration").

You can choose one of the following operating modes:

  - 'set-as-author': the author list is replaced with the detected collaboration
    name(s)

  - 'set-as-author-if-long-list': the collaboration names are set as author
    names; if the original author names (not including collaboration names) is
    lower than a given threshold (by default 50, see the -sLongListThreshold=
    option), then the original author list is kept after that, otherwise it is
    cleared.

  - 'set-collaboration-field': the bibtex 'collaboration' field is set (it is
    nonstandard as far as I can tell) and the author list is retained (w/o any
    collaboration names in the list).

"""

# All these defs are useful for the GUI
_modes = [
    ('none', 0),
    ('set-as-author', 1),
    ('set-as-author-if-long-list', 2),
    ('set-collaboration-field', 3),
    ]

UseCollaborationMode = enum_class('UseCollaborationMode', _modes,
                                  default_value=1, value_attr_name='mode')



class CollaborationFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(
            self,
            use_mode=UseCollaborationMode('set-as-author'),
            long_list_threshold=50,
            detect_from_author=True,
            author_collaboration_regex=r'\bcollaboration\b'
    ):
        r"""
        Arguments:
        
          - use_mode(UseCollaborationMode): How to normalize the collaboration.
            This should be one of 'set-as-author' (replace author list by
            collaboration name), 'set-as-author-if-long-list' (replace
            author list by collaboration if the author list is long, otherwise
            have collaboration first followed by the author list), or
            'set-collaboration-field' (keep the author list removing
            collaboration names and set the bibtex field `collaboration=`).

          - long_list_threshold: how long the author list should be to be deemed
            "too long".

          - detect_from_author: For author lists that are long (see
            long_list_threshold), see if there is an author item whose "name"
            contains "collaboration".  If so, set that as the collaboration for
            that entry.
        
          - author_collaboration_regex: Regular expression that is used to
            detect collaboration names in author lists.
        """
        super().__init__()

        self.detect_from_author = detect_from_author

        self.use_mode = UseCollaborationMode(use_mode)

        self.long_list_threshold = int(long_list_threshold)

        self.author_collaboration_regex = re.compile(author_collaboration_regex, re.IGNORECASE)

        logger.debug('collaboration filter constructor done')
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY


    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        # is this entry a collaboration? if so populate collaboration_names
        collaboration_names = []
        collab_field = entry.fields.get('collaboration', None)
        if collab_field is not None and collab_field.strip():
            # collaboration= field is set, use it
            cn = remove_full_braces(collab_field)
            collaboration_names = [ '{'+cn+'}' ]
            del entry.fields['collaboration']
        elif self.detect_from_author:
            # check author list
            authors = entry.persons.get('author', [])
            remove_j = []
            for j, a in enumerate(authors):
                stra = str(a)
                if self.author_collaboration_regex.search(stra) is not None:
                    # match!
                    collaboration_names.append(stra)
                    remove_j.append(j)
            # remove these from author list. iterate in reverse order to delete
            # later occurrences first so that indexes don't change during
            # iteration
            for j in reversed(remove_j):
                del authors[j]

        # stop here if this isn't a collaboration
        if not collaboration_names:
            return

        def set_as_author(clear_authors=True):
            if clear_authors:
                del entry.persons['author'][:]
            # insert at the beginning of the author list, if we keep authors.
            # Insert in reverse order so we keep inserting at the top of the
            # list
            for cn in reversed(collaboration_names):
                entry.persons['author'].insert(0, Person(cn))

        if self.use_mode == UseCollaborationMode('set-as-author'):
            set_as_author()
            return

        if self.use_mode == UseCollaborationMode('set-as-author-if-long-list'):
            if len(entry.persons.get('author', [])) >= self.long_list_threshold:
                clear_authors = True
            else:
                clear_authors = False
            set_as_author(clear_authors=clear_authors)
            return

        if self.use_mode == UseCollaborationMode('set-collaboration-field'):
            entry.fields['collaboration'] = ', '.join(collaboration_names)
            return

        return



def bibolamazi_filter_class():
    return CollaborationFilter

