# -*- coding: utf-8 -*-
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


#import os
#import os.path
import re
import datetime
import calendar
import logging
logger = logging.getLogger(__name__)

#from pybtex.database import BibliographyData


from bibolamazi.core import butils
from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import enum_class

from .util import arxivutil


HELP_AUTHOR = r"""
Order entries filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = r"""
Order bibliographic entries in bibtex file
"""

HELP_TEXT = r"""
This filter orders the entries in the bibtex file.

Possible ordering modes are:

  - 'raw'
    doesn't change the ordering--leaves the natural order.
  
  - 'alphabetical'
    Orders all the entries in the bibtex file alphabetically according to the citation key.

  - 'date'
    Orders all the entries in the bibtex file by publication date, most recent first.


Note the '-dReverse' option which flips the ordering for 'alphabetical' or 'date' ordering
mode. This option has no effect for 'raw' mode.

This is particularly useful for keeping the bibtex file in a VCS (git, svn etc.)
and getting relevant diffs between different revisions.
"""





# modes
ORDER_RAW = 0
ORDER_CITATION_KEY_ALPHA = 1
ORDER_DATE = 2


OrderMode = enum_class('OrderMode', [('raw', ORDER_RAW),
                                     ('alphabetical', ORDER_CITATION_KEY_ALPHA),
                                     ('date', ORDER_DATE),
                                     ],
                       default_value='alphabetical',
                       value_attr_name='ordermode')



class OrderEntriesFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT
    
    
    def __init__(self, order=None, reverse=False):
        """
        Arguments:

          - order(OrderMode): The strategy according to which to order all the
                entries.  Possible values: see below.

          - reverse(bool): Reverse the sorting order. Has no effect with 'raw'
                order mode.

        """
        super().__init__()

        self.order = OrderMode(order)
        self.reverse = butils.getbool(reverse)

        logger.debug('orderentries: self.order=%r' % self.order)

    
    def requested_cache_accessors(self):
        return [
            arxivutil.ArxivInfoCacheAccessor,
            arxivutil.ArxivFetchedAPIInfoCacheAccessor
            ]

    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE

    def getRunningMessage(self):
        return "{}: Processing {} entries".format(
            self.name(),
            len(self.bibolamaziFile().bibliographyData().entries)
        )

    def filter_bibolamazifile(self, bibolamazifile):
        #
        # bibdata is a pybtex.database.BibliographyData object
        #

        logger.debug("ordering entries according to mode=%r." %(self.order))

        if (self.order == ORDER_CITATION_KEY_ALPHA):
            
            bibdata = bibolamazifile.bibliographyData()

            sort_entries(bibdata.entries, reverse=self.reverse)

        elif (self.order == ORDER_DATE):

            bibdata = bibolamazifile.bibliographyData()

            entries = bibdata.entries

            arxivaccessor = arxivutil.setup_and_get_arxiv_accessor(self.bibolamaziFile())

            def getpubdate(key):
                def mkdkey(date, articleid):
                    return (date, articleid,)

                entry = entries.get(key)
                if entry is None:
                    return mkdkey(datetime.today(), 0)
                fields = entry.fields

                arxivinfo = arxivaccessor.getArXivInfo(key)
                if arxivinfo is not None and not arxivinfo['published']:
                    # use arxiv ID information only if entry is not published--otherwise,
                    # try to get actual publication date.
                    m = re.match(
                        r'^([\w_.-]/)?(?P<year>\d\d)(?P<month>\d\d)(?P<articleid>\d{3}|\.\d{4,})$',
                        arxivinfo['arxivid']
                    )
                    if m is not None:
                        try:
                            year =  ( int(m.group('year')) - 1990 ) % 100  +  1990
                            month = int(m.group('month'))
                            articleid = m.group('articleid')
                            articleid = articleid[1:] if articleid[0] == '.' else articleid
                            return mkdkey(datetime.date(year, month, 1), int(articleid))
                        except ValueError:
                            pass
                
                year = None
                if 'year' in fields:
                    try:
                        year = int(fields['year'])
                    except ValueError:
                        pass
                if year is None:
                    year = datetime.date.today().year

                month = None
                if 'month' in fields:
                    mon_s = re.sub('[^a-z]', '', fields['month'].lower())
                    month = next( (1+k for k in range(len(_month_regexps))
                                   if (_month_regexps[k].match(mon_s)) ), None )
                    logger.longdebug("%s: Got month = %r", key, month)
                if month is None:
                    month = 12

                day = None
                if 'day' in fields:
                    try:
                        day = int(fields['day'])
                    except ValueError:
                        pass
                if day is None:
                    day = calendar.monthrange(year, month)[1]

                try:
                    return mkdkey(datetime.date(year, month, day), 0)
                except ValueError as e:
                    logger.warning("Can't parse date for entry %s: %s", key, e)
                    return mkdkey(datetime.date.today(), 0)

            def getentrysortkey(key):
                # use tuple with key to always keep consistent sorting order
                # between entries with same detected publication date (happens
                # often if only month/year detected)
                return (getpubdate(key), key)

            # Note the "not reverse" because the date key will sort
            # increasingly, whereas we want the default sort order to be newest
            # first.
            sort_entries(bibdata.entries, key=getentrysortkey, reverse=(not self.reverse))


        elif (self.order == ORDER_RAW):

            # natural order mode. don't do anything.
            pass

        else:

            raise BibFilterError(self.name(), "Bad order mode: %r !" %(self.order))
            
        logger.debug("ordered entries as wished.")

        return


_month_regexps = (
    re.compile('^jan'),
    re.compile('^feb'),
    re.compile('^mar'),
    re.compile('^apr'),
    re.compile('^may'),
    re.compile('^jun'),
    re.compile('^jul'),
    re.compile('^aug'),
    re.compile('^sep'),
    re.compile('^oct'),
    re.compile('^nov'),
    re.compile('^dec'),
    )



def sort_entries(bibdata_entries, key=lambda x: x, reverse=False):
     new_dic = sorted(bibdata_entries.items(), key=lambda x: key(x[0]), reverse=reverse)
     bibdata_entries.clear()
     bibdata_entries.update(new_dic)




def bibolamazi_filter_class():
    return OrderEntriesFilter
