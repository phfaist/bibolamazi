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

import arxiv2bib
import re
from urllib2 import URLError, HTTPError
import logging
logger = logging.getLogger(__name__)

from bibolamazi.core.bibusercache import BibUserCacheAccessor, BibUserCacheError
from bibolamazi.core.bibusercache.tokencheckers import EntryFieldsTokenChecker 
from bibolamazi.core import butils


class BibArxivApiFetchError(BibUserCacheError):
    def __init__(self, msg):
        super(BibArxivApiFetchError).__init__('arxiv_fetched_api_info', msg)


# --- code to detect arXiv info ---

_RX_BEFORE = r'(?:\s*([;,]?\s*)|\b|\s+|^)'
_RX_AFTER = r'(?:\s*[;,]?\s*|$)'

_RX_PRIMARY_CLASS_PAT = r'[-a-zA-Z0-9\._]+'

_RX_ARXIVID_NUM_PAT = r'(?<!\d)(?:\d{4}\.\d{4,}|\d{7})(?:v\d+)?' # only the numerical arxiv ID (+possible version)
_RX_ARXIVID_NUM = r'(?P<arxivid>'+_RX_ARXIVID_NUM_PAT+r')' 
_RX_ARXIVID_TOL = r'(?P<arxivid>(?:'+_RX_PRIMARY_CLASS_PAT+r'/)?'+_RX_ARXIVID_NUM_PAT+r')' # allow primary-class/ etc.

def _mk_braced_pair_rx(mid):
    return [ re.compile(_RX_BEFORE + r'\{\s*' + mid + r'\s*\}' + _RX_AFTER, re.IGNORECASE) ,
             re.compile(_RX_BEFORE + mid + _RX_AFTER, re.IGNORECASE) ]

# a list of regexes that we will need often.
#
# The following are regexes we check for in url fields. Don't include all regexes, because
# some DOI or parts of URLs may contain sequences of chars which match the easier arXiv
# regexes.
_rxarxiv_in_url = (# not tuple, just a multiline expression
    []
    + _mk_braced_pair_rx(
        r'\\href\s*\{\s*(?:http://)?arxiv\.org/(?:abs|pdf)/' + _RX_ARXIVID_TOL + r'\s*\}\s*\{[^\{\}]*\}'
        )
    + _mk_braced_pair_rx(
        r'\\(?:url|href)\s*\{\s*(?:http://)?arxiv\.org/(?:abs|pdf)/' + _RX_ARXIVID_TOL + r's*\}'
        )
    + _mk_braced_pair_rx(
        r'(?:http://)?arxiv\.org/(?:abs|pdf)/' + _RX_ARXIVID_TOL + r's*'
        )
    )
# And these regexes are the most tolerant ones, we'll check for these more or less
# everywhere except in the URL fields.
_rxarxiv = _rxarxiv_in_url + (# not tuple, just a multiline expression
    _mk_braced_pair_rx(
        r'(?:http://)?arxiv\.org/(?:abs|pdf)/' + _RX_ARXIVID_TOL
        )
    + _mk_braced_pair_rx(
        r'(?:arXiv[-.:/\s]+)?((?P<primaryclass>' + _RX_PRIMARY_CLASS_PAT + r'/)?' + _RX_ARXIVID_NUM + r')'
        )
    )

# getting "pure" arxiv ID means the arxiv ID (with primary class for old IDs only), without version information.
_rx_purearxivid = re.compile(r'(?P<purearxivid>((\d{4}\.\d{4,})|'+
                             r'('+_RX_PRIMARY_CLASS_PAT+r'/\d{7}))(v\d+)?)', re.IGNORECASE)

_rx_aid_year = re.compile(r'(?P<year>\d{2})(?P<mon>\d{2})(?:\.\d{4,}|\d{3})')

#
# A list of fields which are inspected for arXiv information. This is useful for cache
# invalidation in various instances.
#
arxivinfo_from_bibtex_fields = [
    'journal', 'doi', 'eprint', 'arxivid', 'url',
    'note', 'annote', 'primaryclass',
    'archiveprefix', ]


# extract arXiv info from an entry
def detectEntryArXivInfo(entry):
    """
    Extract arXiv information from a `pybtex.database.Entry` bibliographic entry.

    Returns upon success a dictionary of the form::
    
        { 'primaryclass': <primary class, if available>,
          'arxivid': <the (minimal) arXiv ID (in format XXXX.XXXX  or  archive/XXXXXXX)>,
          'archiveprefix': value of the 'archiveprefix' field
          'published': True/False <whether this entry was published in a journal other than arxiv>,
          'doi': <DOI of entry if any, otherwise None>
          'year': <Year in preprint arXiv ID number. 4-digit, string type.>
          'isoldarxivid': <Whether the arXiv ID is of old style, i.e. 'primary-class/XXXXXXX'>
          'isnewarxivid': <Whether the arXiv ID is of new style, i.e. 'XXXX.XXXX+' (with 4 or more digits after dot)>
        }

    Note that 'published' is set to True for PhD and Master's thesis. Also, the arxiv.py
    filter handles this case separately and explicitly, the option there
    `-dThesesCountAsPublished=0` has no effect here.

    If no arXiv information was detected, then this function returns None.
    """
    
    fields = entry.fields;

    d =  { 'primaryclass': None ,
           'arxivid': None ,
           'published': True ,
           'archiveprefix': None,
           'doi': None,
           'year': None,
           'isoldarxivid': None,
           'isnewarxivid': None,
           };

    #
    # NOTE: If you add/change the fields that are used here, make sure you update the
    # EntryFieldsTokenChecker below!
    #
    
    if (entry.type == u'unpublished' or entry.type == u'misc'):
        d['published'] = False
    elif entry.type in (u'phdthesis', u'mastersthesis',):
        # by default, PhD theses and Master's thesis count as published (although this
        # case is handled specially in the arxiv filter)
        d['published'] = True
    elif entry.type in (u'book', u'booksection', u'inproceedings', u'incollection', u'conference',
                        u'inbook', u'proceedings',):
        # proceedings, books, etc. are published
        d['published'] = True
    elif ('journal' in fields and re.search(r'arxiv', fields['journal'], re.IGNORECASE)):
        # if journal is the arXiv, then it's not published.
        d['published'] = False
    elif ('journal' in fields and fields['journal'].strip()):
        # otherwise, if there is a journal, it's published
        d['published'] = True
    elif ('journal' not in fields or fields['journal'].strip() == ""):
        # if there's no journal for an article or an unknown publication type, it's the arxiv.
        d['published'] = False
    else:
        logger.longdebug('No decisive information about whether this entry is published: %s (type %s), '
                         'defaulting to True.', entry.key, entry.type);


    def extract_pure_id(x, primaryclass=None):
        m = _rx_purearxivid.search( (primaryclass+'/' if primaryclass else "") + x)
        if m is None:
            raise IndexError
        return m.group('purearxivid')


    if ('doi' in fields and fields['doi']):
        d['doi'] = fields['doi']

    if ('eprint' in fields):
        # this gives the arxiv ID
        try:
            d['arxivid'] = extract_pure_id(fields['eprint'], primaryclass=fields.get('primaryclass', None));
            m = re.match('^([-\w.]+)/', d['arxivid']);
            if (m):
                d['primaryclass'] = m.group(1);
        except IndexError as e:
            logger.longdebug("Indexerror: invalid arXiv ID [%r/]%r: %s",
                             fields.get('primaryclass',None), fields['eprint'], e)
            logger.warning("Entry `%s' has invalid arXiv ID %r", entry.key, fields['eprint'])

    if ('primaryclass' in fields):
        d['primaryclass'] = fields['primaryclass'];

    if ('archiveprefix' in fields):
        d['archiveprefix'] = fields['archiveprefix'];


    def processNoteField(notefield, d, isurl=False):

        if isurl:
            rxlist = _rxarxiv_in_url
        else:
            rxlist = _rxarxiv

        for rx in rxlist:
            m = rx.search(notefield);
            if m:
                if (not d['arxivid']):
                    try:
                        primaryclass = None
                        try: primaryclass = m.group('primaryclass')
                        except IndexError: pass

                        d['arxivid'] = extract_pure_id(m.group('arxivid'), primaryclass=primaryclass)
                    except IndexError as e:
                        logger.longdebug("indexerror while getting arxivid in note=%r, m=%r: %s", notefield, m, e)
                        pass
                if (not d['primaryclass']):
                    try:
                        d['primaryclass'] = m.group('primaryclass');
                    except IndexError:
                        pass
            if d['arxivid'] and d['primaryclass']:
                return
                
    if ('note' in fields):
        processNoteField(fields['note'], d);

    if ('annote' in fields):
        processNoteField(fields['annote'], d);

    if ('url' in fields):
        processNoteField(fields['url'], d, isurl=True);

    if (d['arxivid'] is None):
        # no arXiv info.
        return None

    # FIX: if archive-ID is old style, and does not contain the primary class, add it as "quant-ph/XXXXXXX"
    if (re.match(r'^\d{7}$', d['arxivid']) and d['primaryclass'] and len(d['primaryclass']) > 0):
        d['arxivid'] = d['primaryclass']+'/'+d['arxivid']

    # set whether old style or new style arXiv ID
    if re.match(r'^\d{4}\.\d{4,}(v\d+)?$', d['arxivid']):
        d['isoldarxivid'] = False
        d['isnewarxivid'] = True
    elif re.match(r'^'+_RX_PRIMARY_CLASS_PAT+r'/\d{7}(v\d+)?$', d['arxivid']):
        d['isoldarxivid'] = True
        d['isnewarxivid'] = False
    else:
        d['isoldarxivid'] = False # can't determine arxiv ID style ...
        d['isnewarxivid'] = False # can't determine arxiv ID style ...

        
    # get the year
    m = _rx_aid_year.search(d['arxivid'])
    if not m:
        logger.warning("Couldn't find the year in arXiv ID %r", d['arxivid'])
    else:
        # 91->1991, 89->2089 (arXiv started in 1991)
        d['year'] = str(1990 + (int(m.group('year')) - 90) % 100)
        
    return d


def stripArXivInfoInNote(notestr):
    """Assumes that notestr is a string in a note={} field of a bibtex entry, and strips any arxiv identifier
    information found, e.g. of the form 'arxiv:XXXX.YYYY' (or similar).
    """

    newnotestr = notestr
    for rx in _rxarxiv:
        # replace all occurences of rx's in _rxarxiv with nothing.
        newnotestr = rx.sub('', newnotestr)

    if (notestr != newnotestr):
        logger.longdebug("stripArXivInfoInNote: stripped %r to %r", notestr, newnotestr)
    return newnotestr






# ---- API info ------



class ArxivFetchedAPIInfoCacheAccessor(BibUserCacheAccessor):
    """
    A `BibUserCacheAccessor` for fetching and accessing information retrieved from the
    arXiv API.
    """
    def __init__(self, **kwargs):
        super(ArxivFetchedAPIInfoCacheAccessor, self).__init__(
            cache_name='arxiv_fetched_api_info',
            **kwargs
            )

    def initialize(self, cache_obj, **kwargs):
        dic = self.cacheDic()
        dic.setdefault('fetched', {})
        #logger.longdebug("dic is %r\n"
        #                 "id(dic['fetched'])=%r", dic, id(dic['fetched']))

        logger.debug("arxiv_fetched_api_info: adding validation checker; time valid is %r",
                     cache_obj.cacheExpirationTokenChecker().time_valid)

        # validate each entry with an expiration checker. Do this per entry, rather than
        # globally on the full cache. (So don't use installCacheExpirationChecker())
        dic['fetched'].set_validation(cache_obj.cacheExpirationTokenChecker())
        


    def fetchArxivApiInfo(self, idlist):
        """
        Populates the given cache with information about the arXiv entries given in
        `idlist`. This must be, yes you guessed right, a list of arXiv identifiers that we
        should fetch.

        This function performs a query on the arXiv.org API, using the arxiv2bib library. 
        Please note that you should avoid making rapid fire requests in a row (this should
        normally not happen anyway thanks to our cache mechanism). However, beware that if
        we get a ``403 Forbidden`` HTTP answer, we should not continue or else arXiv.org
        might interpret our requests as a DOS attack. If a ``403 Forbidden`` HTTP answer
        is received this function raises :py:exc:`BibArxivApiFetchError` with a meaningful
        error text.

        Only those entries in `idlist` which are not already in the cache are fetched.

        `idlist` can be any iterable.
        """

        cache_entrydic = self.cacheDic()['fetched']
        logger.longdebug("fetchArxivApiInfo(): "
                         "id(dic['fetched'])=%r, \nid(self.cacheObject().cachedic['arxiv_fetched_api_info']=%r\n"
                         "len(dic['fetched'])=%d",
                         id(cache_entrydic), id(self.cacheObject().cachedic['arxiv_fetched_api_info']),
                         len(cache_entrydic))

        logger.longdebug("fetchArxivApiInfo(): in the cache, we have keys %r",
                         cache_entrydic.keys())

        missing_ids = []
        #debug_allids = []
        for aid in idlist:
            #debug_allids.append(aid)
            if (aid not in cache_entrydic  or
                cache_entrydic.get(aid) is None  or
                isinstance(cache_entrydic.get(aid), arxiv2bib.ReferenceErrorInfo)):
                missing_ids.append(aid)

        #logger.longdebug("fetchArxivApiInfo(): debug_allids=%r, missing_ids=%r", debug_allids, missing_ids)

        if not missing_ids:
            logger.longdebug('nothing to fetch: no missing ids')
            # nothing to fetch
            return True

        logger.info("Fetching missing information from the arXiv API...")
        logger.debug('fetching missing id list %r' %(missing_ids))
        try:
            arxivdict = arxiv2bib.arxiv2bib_dict(missing_ids)
            logger.longdebug('got entries %r: %r' %(arxivdict.keys(), arxivdict))
        except URLError as error:
            if isinstance(error, HTTPError) and error.getcode() == 403:
                raise BibArxivApiFetchError(
                    textwrap.dedent("""\
                    Error fetching ArXiv API Info: ** 403 Forbidden **

                    This usually happens when you make many rapid fire requests in a
                    row. If you continue to do this, arXiv.org may interpret your requests
                    as a denial of service attack.

                    For more information, see http://arxiv.org/help/robots.
                    """))
            else:
                msg = (("%d: %s" %(error.code, error.reason)) if isinstance(error, HTTPError)
                       else error.reason)
                logger.warning("HTTP Connection Error: %s.", msg)
                logger.warning("ArXiv API information will not be retreived, and your bibliography "
                               "might be incomplete.")
                return False
                #
                # Don't raise an error, in case the guy is running bibolamazi on his laptop on the
                # train. In that case he might prefer some missing entries rather than a critical failure.
                #
                #            raise BibFilterError(
                #                filtname,
                #                "HTTP Connection Error: {0}".format(error.getcode())
                #                )

        for (k,ref) in arxivdict.iteritems():
            logger.longdebug("Got reference object for id %s: %r" %(k, ref.__dict__))
            cache_entrydic[k]['reference'] = ref
            bibtex = ref.bibtex()
            cache_entrydic[k]['bibtex'] = bibtex


        logger.longdebug("arxiv api info: Got all references. cacheDic() is now:  %r", self.cacheDic())
        logger.longdebug("... and cacheObject().cachedic is now:  %r", self.cacheObject().cachedic)

        return True


    def getArxivApiInfo(self, arxivid):
        """
        Returns a dictionary::

            {
              'reference':  <arxiv2bib.Reference>,
              'bibtex': <bibtex string>
            }

        for the given arXiv id in the cache. If the information is not in the cache,
        returns `None`.

        Don't forget to first call :py:meth:`fetchArxivApiInfo()` to retrieve the
        information in the first place.

        Note the reference part may be a :py:class:`arxiv2bib.ReferenceErrorInfo`, if
        there was an error retreiving the reference.
        """
        return self.cacheDic()['fetched'].get(arxivid, None)





class ArxivInfoCacheAccessor(BibUserCacheAccessor):
    """
    Cache accessor for detected arXiv information about bibliography entries.
    """
    def __init__(self, **kwargs):
        super(ArxivInfoCacheAccessor, self).__init__(
            cache_name='arxiv_info',
            **kwargs
            )

    def initialize(self, cache_obj, **kwargs):
        cache_dic = self.cacheDic()
        cache_dic['entries'].set_validation(
            EntryFieldsTokenChecker(self.bibolamaziFile().bibliographyData(),
                                    store_type=True,
                                    fields=arxivinfo_from_bibtex_fields)
            )
        cache_dic.setdefault('cache_built', False)


    def rebuild_cache(self, bibdata, arxiv_api_accessor):
        """
        Clear and rebuild the entry cache completely.
        """
        entrydic = self.cacheDic()['entries']
        entrydic.clear()
        self.complete_cache(bibdata, arxiv_api_accessor)


    def revalidate(self, bibolamazifile):
        """
        Re-validates the cache (with validate()), and calls again complete_cache()
        to fetch all missing or out-of-date entries.
        """
        self.cacheDic()['entries'].validate()
        self.complete_cache(
            bibolamazifile.bibliographyData(),
            bibolamazifile.cacheAccessor(ArxivFetchedAPIInfoCacheAccessor)
        )

    def complete_cache(self, bibdata, arxiv_api_accessor):
        """
        Makes sure the cache is complete for all items in `bibdata`.
        """

        entrydic = self.cacheDic()['entries']

        # A list if pairs (citekey, arxiv-id) of entries that still need to be completed
        # with info from the arXiv API.
        needs_to_be_completed = []

        #
        # Do a first scan through all the bibdata entries, and detect the API information
        # using only what we have. We'll do a query to the arXiv API in a second step
        # below.
        #
        for k,v in bibdata.entries.iteritems():
            if (k in entrydic):
                continue
            arinfo = detectEntryArXivInfo(v);
            entrydic[k] = arinfo;
            logger.longdebug("got arXiv information for `%s': %r.", k, arinfo)
            
            if (entrydic[k] is not None):
                needs_to_be_completed.append( (k, arinfo['arxivid'],) )

        logger.longdebug("complete_cache(): needs_to_be_completed=%r\nentrydic=%r\n",
                         needs_to_be_completed,
                         entrydic)

        #
        # Complete the entry arXiv info using fetched info from the arXiv API.
        #
        arxiv_api_accessor.fetchArxivApiInfo( (x[1] for x in needs_to_be_completed), )

        for (k,aid) in needs_to_be_completed:
            api_info = arxiv_api_accessor.getArxivApiInfo(aid)
            if (api_info is None):
                logger.warning("Failed to fetch arXiv information for %s", aid);
                continue
            
            entrydic[k]['primaryclass'] = self._reference_category(api_info['reference'])
            entrydic[k]['doi'] = self._reference_doi(api_info['reference']);


    def getArXivInfo(self, entrykey):
        """
        Get the arXiv information corresponding to entry citekey `entrykey`. If the entry
        is not in the cache, returns `None`. Call `complete_cache()` first!
        """
        logger.longdebug("Getting arxiv info for key %r from cache.", entrykey)

        entrydic = self.cacheDic()['entries']

        if (entrykey not in entrydic):
            logger.longdebug("    --> not found :(")
            return None

        return entrydic.get(entrykey, None)


    def _reference_doi(self, ref):
        try:
            doi = ref._field_text('doi', namespace=arxiv2bib.ARXIV)
        except:
            return None
        if (doi):
            return doi
        return None

    def _reference_category(self, ref):
        try:
            return ref.category;
        except AttributeError:
            # happens for ReferenceErrorInfo, for example
            return None





def setup_and_get_arxiv_accessor(bibolamazifile):
    arxivinfoaccessor = bibolamazifile.cacheAccessor(ArxivInfoCacheAccessor)
    arxivinfoaccessor.complete_cache(
        bibolamazifile.bibliographyData(),
        bibolamazifile.cacheAccessor(ArxivFetchedAPIInfoCacheAccessor)
        )
    return arxivinfoaccessor



# deprecated:
def get_arxiv_cache_access(bibolamazifile):
    butils.warn_deprecated(None, "get_arxiv_cache_access()", "setup_and_get_arxiv_accessor()",
                           modulename="arxivutil.py",
                           explanation="We now use the new cache mechanism; your filter should "
                           "also explicitly request the cache accessors ArxivInfoCacheAccessor "
                           "and ArxivFetchedAPIInfoCacheAccessor so that the cache is correctly "
                           "set up.")
    return setup_and_get_arxiv_accessor(bibolamazifile)
