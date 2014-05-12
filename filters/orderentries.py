
import os
import os.path
import re
import codecs
import datetime
import calendar

from pybtex.database import BibliographyData;


from core import bibfilter
from core import butils
from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;


HELP_AUTHOR = u"""\
Order entries filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Order bibliographic entries in bibtex file
"""

HELP_TEXT = u"""
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


OrderMode = bibfilter.enum_class('OrderMode', [('raw', ORDER_RAW),
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
          - order(OrderMode): The strategy according to which to order all the entries. Possible
                values: see below.
          - reverse(bool): Reverse the sorting order. Has no effect with 'raw' order mode.
        """
        BibFilter.__init__(self);

        self.order = OrderMode(order)
        self.reverse = butils.getbool(reverse)

        logger.debug('orderentries: self.order=%r' % self.order);

    def name(self):
        return "orderentries"

    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE;

    def getRunningMessage(self):
        return "%s: Processing %d entries" %(self.name(), len(self.bibolamaziFile().bibliographydata().entries))

    def filter_bibolamazifile(self, bibolamazifile):
        #
        # bibdata is a pybtex.database.BibliographyData object
        #

        logger.debug("ordering entries according to mode=%r." %(self.order));

        if (self.order == ORDER_CITATION_KEY_ALPHA):
            
            bibdata = bibolamazifile.bibliographydata();

            #newentries = sorted(bibdata.entries.iteritems(), key=lambda x: x[0].lower())
            entries = bibdata.entries;

            # bibdata.entries is of type pybtex.util.OrderedCaseInsensitiveDict, which has
            # an attribute `order`, which is a list of keys in the relevant order. So use
            # list.sort(), which is slightly more efficient.
            bibdata.entries.order.sort(reverse=self.reverse)

            #newbibdata = BibliographyData(entries=newentries);
            #bibolamazifile.setBibliographyData(newbibdata);

        elif (self.order == ORDER_DATE):

            bibdata = bibolamazifile.bibliographydata();

            entries = bibdata.entries;

            def getpubdate(key):
                entry = entries.get(key)
                if entry is None:
                    return datetime.today()
                fields = entry.fields
                year = datetime.MAXYEAR
                month = 12
                if 'year' in fields:
                    try:
                        year = int(fields['year'])
                    except ValueError:
                        pass

                if 'month' in fields:
                    mon_s = re.sub('[^a-z]', '', fields['month'].lower())
                    month = next( (1+k for k in range(len(_month_regexps))
                                   if (_month_regexps[k].match(mon_s)) ), 12 )

                day = calendar.monthrange(year, month)[1];
                if 'day' in fields:
                    try:
                        day = int(fields['day'])
                    except ValueError:
                        pass

                try:
                    return datetime.date(year, month, day)
                except ValueError as e:
                    logger.warning("Can't parse date for entry %s: %s", key, e)
                    return datetime.date.today()

            # see above. Note the "not reverse" because the date key will sort
            # increasingly, whereas we want the default sort order to be newest first.
            bibdata.entries.order.sort(key=getpubdate, reverse=(not self.reverse));

        elif (self.order == ORDER_RAW):
            # natural order mode. don't do anything.
            pass
        else:
            raise BibFilterError(self.name(), "Bad order mode: %r !" %(self.order));
            
        logger.debug("ordered entries as wished.");

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



def bibolamazi_filter_class():
    return OrderEntriesFilter;

