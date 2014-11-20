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



#
# NOTE: THIS WAS WRITTEN FOR THE OLD CACHE API !!!
#
# THIS WILL NOT WORK WITH THE NEW API!!!
#





import re
import datetime
import hashlib

from pybtex.database import Person, Entry

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
    def __init__(self, bibdata, **kwargs):
        self.bibdata = bibdata
        super(EntryTitleTokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        data = self.bibdata.entries.get(key,Entry('misc')).fields.get('title', '')
        return hashlib.md5(data.encode('utf-8')).hexdigest()


class EntryDOITokenChecker(bibusercache.TokenChecker):
    def __init__(self, bibdata, **kwargs):
        self.bibdata = bibdata
        super(EntryDOITokenChecker, self).__init__(**kwargs)

    def new_token(self, key, value, **kwargs):
        data = self.bibdata.entries.get(key,Entry('misc')).fields.get('doi', '')
        return hashlib.md5(data.encode('utf-8')).digest()


class TestCacheValidationFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self):
        """
        Constructor method for the test cache validation filter.
        """
        
        BibFilter.__init__(self)

        self.caches_prepared = False


    def _prepare_caches(self):
        if self.caches_prepared:
            return
        
        self.caches_prepared = True

        self.title_cache = self.cache_for('title_cache', dont_expire=True)
        self.title_cache.set_validation(EntryTitleTokenChecker(self.bibolamaziFile().bibliographydata()))

        self.expiring_cache = self.cache_for('expiring_cache')

        self.comb_cache = self.cache_for('comb_cache', dont_expire=True)

        self.comb_cache.set_validation(bibusercache.TokenCheckerCombine(
            EntryDOITokenChecker(self.bibolamaziFile().bibliographydata()),
            EntryTitleTokenChecker(self.bibolamaziFile().bibliographydata()),
            bibusercache.TokenCheckerDate()
            ))
        


    def name(self):
        return "testcachevalidation"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        self._prepare_caches()

        print "Filtering entry `%s'"%(entry.key)

        title_cache = self.title_cache

        key = entry.key
        if key in title_cache:
            print "\ttitle_cache: `", key, "' is in cache, w/ value=", title_cache[key]['title']
            newtitle = title_cache[key]['title']
        else:
            newtitle = entry.fields.get('title', '').upper()
            title_cache[key]['title'] = newtitle
            print "\ttitle_cache: `", key, "' is NOT in cache, recalculated its value & set it."

        entry.fields['uppertitle'] = newtitle


        #
        # example: simple expiring cache
        #

        expiring_cache = self.expiring_cache

        if 'data' in expiring_cache:
            print "\texpiring_cache: we have 'data' in cache, w/ value=", expiring_cache['data']
        else:
            expiring_cache['data'] = ('Random data generated on %r'%(datetime.datetime.now()))
            print "\texpiring_cache: we DON'T have 'data' in cache, set value=", expiring_cache['data']
        entry.fields['annote'] = expiring_cache['data']


        #
        # an example with combination of caches:
        #

        comb_cache = self.comb_cache

        if key in comb_cache:
            print "\tcomb_cache: we have '", key, "' in cache, w/ value=", repr(comb_cache[key])
        else:
            comb_cache[key] = ('DOI='+entry.fields.get('url','????') + '; title='+entry.fields.get('title','')
                               +';; generated on %r'%(datetime.datetime.now()))
            print "\tcomb_cache: we DON'T have '", key, "' in cache, set value=", repr(comb_cache[key])

        entry.fields['note'] = comb_cache[key]

        
        return entry;


    

def bibolamazi_filter_class():
    return TestCacheValidationFilter;

