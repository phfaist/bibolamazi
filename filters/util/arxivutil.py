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

from core.blogger import logger



# --- code to detect arXiv info ---

_RX_BEFORE = r'(?:\s*([;,\{]?\s*)|\b|\s+|^)'
_RX_AFTER = r'(?:\s*[;,\}]?\s*|$)'

_RX_ARXIVID = r'(?P<arxivid>[0-9.]+)'

# a regex that we will need often
_rxarxivinnote = re.compile(
    _RX_BEFORE +
    r'arXiv[-\}\{.:/\s]+(((?P<primaryclass>[-a-zA-Z0-9./]+)/)?' + _RX_ARXIVID + r')' +
    _RX_AFTER,
    re.IGNORECASE
    );
_rxarxivurl    = re.compile(
    _RX_BEFORE +
    r'(?:http://)?arxiv\.org/(?:abs|pdf)/(?P<arxivid>[-a-zA-Z0-9./]+)' + # not quite same <arxivid>: allows '/'
    _RX_AFTER,
    re.IGNORECASE
    );


# extract arXiv info from an entry
def detectEntryArXivInfo(entry):
    """
    Extract arXiv information from a pybtex.database.Entry bibliographic entry.

    Returns upon success a dictionary of the form
        { 'primaryclass': <primary class, if available>,
          'arxivid': <the (minimal) arXiv ID (in format XXXX.XXXX  or  archive/XXXXXXX)
          'published': True/False <whether this entry was published in a journal other than arxiv>
        }

    If no arXiv information was detected, then this function returns None.
    """
    
    fields = entry.fields;

    d =  { 'primaryclass': None ,
           'arxivid': None ,
           'published': True ,
           };
    
    if (entry.type == u'unpublished' or entry.type == u'misc'):
        d['published'] = False
    elif ('journal' in fields and re.search(r'arxiv', fields['journal'], re.IGNORECASE)):
        # if journal is the arXiv, then it's not published.
        d['published'] = False
    elif (entry.type == u'inproceedings'):
        # in conference proceedings -- published
        d['published'] = True
    elif ('journal' not in fields or fields['journal'] == ""):
        # if there's no journal, it's the arxiv.
        d['published'] = False
    else:
        logger.longdebug('No decisive information about whether this entry is published: %s (type %s), '
                         'defaulting to True.', entry.key, entry.type);
        

    if ('eprint' in fields):
        # this gives the arxiv ID
        d['arxivid'] = fields['eprint'];
        m = re.match('^([-\w.]+)/', d['arxivid']);
        if (m):
            d['primaryclass'] = m.group(1);

    if ('primaryclass' in fields):
        d['primaryclass'] = fields['primaryclass'];

    def processNoteField(notefield, d):
        m = _rxarxivinnote.search(notefield);
        if m:
            if (not d['arxivid']):
                try:
                    d['arxivid'] = m.group('arxivid');
                except IndexError:
                    logger.longdebug("indexerror for 'arxivid' group in note=%r, m=%r", notefield, m)
                    pass
            if (not d['primaryclass']):
                try:
                    d['primaryclass'] = m.group('primaryclass');
                except IndexError:
                    logger.longdebug("indexerror for 'primaryclass' group in note=%r, m=%r", notefield, m)
                    pass
        m = _rxarxivurl.search(notefield);
        if m:
            if (not d['arxivid']):
                try:
                    d['arxivid'] = m.group('arxivid');
                except IndexError:
                    logger.longdebug("_rxarxivurl: indexerror for 'arxivid' group in note=%r, m=%r", notefield, m);
                    pass
                
    if ('note' in fields):
        processNoteField(fields['note'], d);

    if ('annote' in fields):
        processNoteField(fields['annote'], d);

    if ('url' in fields):
        processNoteField(fields['url'], d);

    if (d['arxivid'] is None):
        # no arXiv info.
        return None

    # FIX: if archive-ID is old style, and does not contain the primary class, add it as "quant-ph/XXXXXXX"
    if (re.match(r'^\d{7}$', d['arxivid']) and d['primaryclass'] and len(d['primaryclass']) > 0):
        d['arxivid'] = d['primaryclass']+'/'+d['arxivid']
    
    return d


def stripArXivInfoInNote(notestr):
    """Assumes that notestr is a string in a note={} field of a bibtex entry, and strips any arxiv identifier
    information found, e.g. of the form 'arxiv:XXXX.YYYY' (or similar).
    """

    newnotestr = _rxarxivinnote.sub('', _rxarxivurl.sub('', notestr));
    if (notestr != newnotestr):
        logger.longdebug("stripArXivInfoInNote: stripped %r to %r", notestr, newnotestr)
    return newnotestr






# ---- API info ------



def reference_doi(ref):
    try:
        doi = ref._field_text('doi', namespace=arxiv2bib.ARXIV)
    except:
        return None
    if (doi):
        return doi
    return None

def reference_category(ref):
    try:
        return ref.category;
    except AttributeError:
        # happens for ReferenceErrorInfo, for example
        return None


def fetch_arxiv_api_info(idlist, cache_entrydic, filterobj=None):
    """
    Populates the given cache with information about the arXiv entries given in `idlist`.

    cache_entrydic is expected to be the cache
    `[filter/bibolamazifile].cache_for('arxiv_fetched_api_info')['fetched']`
    """

    missing_ids = [ aid for aid in idlist
                    if (aid not in cache_entrydic or
                        isinstance(cache_entrydic.get(aid), arxiv2bib.ReferenceErrorInfo)) ]
    
    if not missing_ids:
        logger.longdebug('nothing to fetch: no missing ids')
        # nothing to fetch
        return True

    logger.longdebug('fetching missing id list %r' %(missing_ids))
    try:
        arxivdict = arxiv2bib.arxiv2bib_dict(missing_ids)
        logger.longdebug('got entries %r: %r' %(arxivdict.keys(), arxivdict))
    except URLError as error:
        filtname = filterobj.name() if filterobj else None;
        if isinstance(error, HTTPError) and error.getcode() == 403:
            raise BibFilterError(
                filtname,
                textwrap.dedent("""\
                403 Forbidden error. This usually happens when you make many
                rapid fire requests in a row. If you continue to do this, arXiv.org may
                interpret your requests as a denial of service attack.
                
                For more information, see http://arxiv.org/help/robots.
                """))
        else:
            msg = (("%d: %s" %(error.code, error.reason)) if isinstance(error, HTTPError)
                   else error.reason);
            logger.warning("HTTP Connection Error: %s. ArXiv API information will not be "
                           "retreived, and your bibliography might be incomplete."
                           %(msg))
            return False
            #
            # Don't raise an error, in case the guy is running bibolamazi on his laptop in the
            # train. In that case he might prefer some missing entries rather than a huge complaint.
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

    return True








# --- the cache mechanism ---

class ArxivInfoCacheAccess:
    def __init__(self, entrydic, bibolamazifile):
        self.entrydic = entrydic;
        self.bibolamazifile = bibolamazifile;

    def rebuild_cache(self):
        self.entrydic.clear()
        self.complete_cache()

    def complete_cache(self):
        bibdata = self.bibolamazifile.bibliographydata()

        needs_to_be_completed = []
        for k,v in bibdata.entries.iteritems():
            if (k in self.entrydic):
                continue
            arinfo = detectEntryArXivInfo(v);
            self.entrydic[k] = arinfo;
            logger.longdebug("got arXiv information for `%s': %r.", k, arinfo)
            
            if (self.entrydic[k] is not None):
                needs_to_be_completed.append( (k, arinfo['arxivid'],) )

        # complete the entry arXiv info using fetched info from the arXiv API.
        fetched_api_cache = self.bibolamazifile.cache_for('arxiv_fetched_api_info')['fetched'];
        fetch_arxiv_api_info( (x[1] for x in needs_to_be_completed),
                             fetched_api_cache)

        for (k,aid) in needs_to_be_completed:
            api_info = fetched_api_cache.get(aid)
            if (api_info is None):
                logger.warning("Failed to fetch arXiv information for %s", aid);
                continue
            
            self.entrydic[k]['primaryclass'] = reference_category(api_info['reference'])
            self.entrydic[k]['doi'] = reference_doi(api_info['reference']);
    

    def getArXivInfo(self, entrykey):
        if (entrykey not in self.entrydic):
            self.complete_cache()

        return self.entrydic.get(entrykey, None)
            

def get_arxiv_cache_access(bibolamazifile):
    arxiv_info_cache = bibolamazifile.cache_for('arxiv_info')

    #logger.longdebug("ArXiv cache state is: %r" %(arxiv_info_cache))

    arxivaccess = ArxivInfoCacheAccess(arxiv_info_cache['entries'], bibolamazifile);
    
    if not arxiv_info_cache['cache_built']:
        arxivaccess.rebuild_cache()
        arxiv_info_cache['cache_built'] = True

    return arxivaccess

