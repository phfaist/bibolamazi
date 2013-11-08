
import arxiv2bib
import re
from urllib2 import HTTPError

from core.blogger import logger



# --- code to detect arXiv info ---


# a regex that we will need often
_rxarxivinnote = re.compile(
    r'(([;,\{]?\s+)?|\b|^\s*)'+
    r'arXiv[-\}\{.:/\s]+(((?P<primaryclass>[-a-zA-Z]+)/)?(?P<arxivid>[0-9.]+))'+
    r'(\s*[;,\}]?\s*|$)',
    re.IGNORECASE
    );
_rxarxivurl    = re.compile(
    r'(([;,\{]?\s+)?|\b|^\s*)(?:http://)?arxiv\.org/(?:abs|pdf)/(?P<arxivid>[-a-zA-Z0-9./]+)\s*',
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

    # if journal is the arXiv, it's not published.
    if ('journal' in fields and re.search(r'arxiv', fields['journal'], re.IGNORECASE)):
        d['published'] = False

    # if there's no journal, it's the arxiv.
    if ('journal' not in fields or fields['journal'] == ""):
        d['published'] = False
        

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

    return _rxarxivurl.sub('', _rxarxivinnote.sub('', notestr));






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

    missing_ids = [ aid for aid in idlist if aid not in cache_entrydic ]
    
    logger.longdebug('fetching missing id list %r' %(missing_ids))
    try:
        arxivdict = arxiv2bib.arxiv2bib_dict(missing_ids)
        logger.longdebug('got entries %r: %r' %(arxivdict.keys(), arxivdict))
    except HTTPError as error:
        filtname = filterobj.name() if filterobj else None;
        if error.getcode() == 403:
            raise BibFilterError(
                filtname,
                textwrap.dedent("""\
                403 Forbidden error. This usually happens when you make many
                rapid fire requests in a row. If you continue to do this, arXiv.org may
                interpret your requests as a denial of service attack.
                
                For more information, see http://arxiv.org/help/robots.
                """))
        else:
            logger.warning("HTTP Connection Error: %d: %s. ArXiv API information will not be "
                           "retreived, and your bibliography might be incomplete."
                           %(error.code, error.reason))
            return False
            #
            # Don't raise an error, in case the guy is running bibolamazi on his laptop in the
            # train. In that case he might prefer some missing entries rather than a huge complaint.
            #
            #            raise BibFilterError(
            #                filtname,
            #                "HTTP Connection Error: {0}".format(error.getcode())
            #                )

    for (k,v) in arxivdict.iteritems():
        cache_entrydic[k]['reference'] = v;
        bibtex = v.bibtex();
        cache_entrydic[k]['bibtex'] = bibtex;

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
            logger.longdebug('got arXiv information for `%s'': %r.' %(k, arinfo))
            
            if (self.entrydic[k] is not None):
                needs_to_be_completed.append(k)

        # complete the entry arXiv info using fetched info from the arXiv API.
        fetched_api_cache = self.bibolamazifile.cache_for('arxiv_fetched_api_info')['fetched'];
        fetch_arxiv_api_info(needs_to_be_completed,
                             fetched_api_cache)

        for aid in needs_to_be_completed:
            api_info = fetched_api_cache.get(aid)
            self.entrydic[aid]['primaryclass'] = reference_category(api_info['reference'])
            self.entrydic[aid]['doi'] = reference_doi(api_info['reference']);
    

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

