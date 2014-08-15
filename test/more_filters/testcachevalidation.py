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
import hashlib

from pybtex.database import Person

from core.bibfilter import BibFilter, BibFilterError
from core.blogger import logger
from core import butils
from core.pylatexenc import latexencode
from core.pylatexenc import latex2text
from core import bibusercache


HELP_AUTHOR = u"""\
Extra test validation cache filter by Philippe Faist, (C) 2014, GPL 3+
"""

HELP_DESC = u"""\
Test cache validation.... creates cache objects and (in)validates them ...
"""

HELP_TEXT = u"""
"""



class EntryTitleTokenChecker(bibusercache.TokenChecker):
    def __init__(self, **kwargs):
        super(EntryTokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value):
        data = value.fields.get('title', '')
        return hashlib.md5(data).hexdigest()


class TestCacheValidationFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self):
        """
        Constructor method for the test cache validation filter.
        """
        
        BibFilter.__init__(self);


    def name(self):
        return "testcachevalidation"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        title_cache = self.cache_for('title_cache', dont_expire=True)

        if key in title_cache:
            newtitle = title_cache[key]['title']
        else:
            newtitle = entry.fields.get('title', '').upper()
            title_cache[key]['title'] = newtitle

        entry.fields['title'] = newtitle


        #
        # an example with combination of caches:
        #
        
        return entry;
    

def bibolamazi_filter_class():
    return TestCacheValidationFilter;

