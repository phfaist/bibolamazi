
import re
#import shlex
#import argparse


from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

MODE_UNPUBLISHED_NOTE = 1;
MODE_EPRINT = 2;
MODE_STRIP = 3;


rxarxivinnote = re.compile(r'(\b|^)arXiv:(?:(?:([-a-zA-Z]+)/)?([0-9.]+))(\s|$)', re.IGNORECASE);

def getArXivInfo(entry):
    fields = entry.fields;

    d =  { 'primaryclass': None ,
           'arxivid': None ,
           'published': True ,
           };
    
    if (entry.type == u'unpublished'):
        d['published'] = False;

    if ('journal' in fields and re.search(r'arxiv', fields['journal'], re.IGNORECASE)):
        d['published'] = False;
        

    if ('eprint' in fields):
        # this gives the arxiv ID
        d['arxivid'] = fields['eprint'];
        m = re.match('^([-\w]+)/', d['arxivid']);
        if (m):
            d['primaryclass'] = m.group(1);

    if ('primaryclass' in fields):
        d['primaryclass'] = fields['primaryclass'];

    if ('note' in fields):
        m = rxarxivinnote.search(fields['note']);
        if m:
            if (not d['arxivid']):
                d['arxivid'] = m.group(2);
            if (not d['primaryclass']):
                d['primaryclass'] = m.group(1);

    if (d['arxivid'] is None):
        # no arXiv info.
        return None
    
    return d


class ArxivNormalizeFilter(BibFilter):
    
    def __init__(self, mode=MODE_EPRINT, unpublished_mode=None):
        BibFilter.__init__(self);

        self.mode = self._parse_mode(mode);
        self.unpublished_mode = (self._parse_mode(unpublished_mode) if unpublished_mode
                                 else self.mode);

        logger.debug('arxiv filter constructor: mode=%d; unpublished_mode=%d' % (self.mode, self.unpublished_mode));

    def _parse_mode(self, mode):
        if (mode == "unpublished-note"):
            return MODE_UNPUBLISHED_NOTE;
        elif (mode == "eprint"):
            return MODE_EPRINT;
        elif (mode == "strip"):
            return MODE_STRIP;

        return int(mode);
        

    def name(self):
        return "ArXiv clean-up"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        
        #import pdb;pdb.set_trace()

        arxivinfo = getArXivInfo(entry);

        if (arxivinfo is None):
            # no arxiv info--don't do anything
            return entry

        # start by stripping all arxiv info.
        entry.fields.pop('archiveprefix', None);
        entry.fields.pop('arxivid', None);
        entry.fields.pop('eprint', None);
        entry.fields.pop('primaryclass', None);
        # possibly remove it from the note={} entry
        if ('note' in entry.fields):
            entry.fields['note'] = rxarxivinnote.sub('', entry.fields['note']);
        if (entry.type == u'unpublished'):
            entry.type = u'article';

        mode = self.mode
        if (not arxivinfo['published']):
            #logger.debug('entry not published : %r' % entry);
            mode = self.unpublished_mode
            
        if (mode == MODE_STRIP):
            # directly return stripped entry.
            return entry

        if (mode == MODE_UNPUBLISHED_NOTE):
            # save arxiv information in the note={} field, and set type to unpublished
            entry.type = u'unpublished';
            note = "arXiv:"+arxivinfo['arxivid'];
            if ('note' in entry.fields and entry.fields['note'].strip()):
                # some other note already there
                entry.fields['note'] += ', '+note;
            else:
                entry.fields['note'] = note;
            
            return entry

        if (mode == MODE_EPRINT):
            entry.fields['arxivid'] = arxivinfo['arxivid'];
            entry.fields['eprint'] = arxivinfo['arxivid'];
            if (arxivinfo['primaryclass']):
                entry.fields['primaryclass'] = arxivinfo['primaryclass'];

            return entry
        
        raise BibFilterError('arxiv', "Unknown mode: %s" % mode );


## def parse_args(optionstring):
##     #logger.debug("optionstring = "+repr(optionstring));
##     a = argparse.ArgumentParser('bibclean: ArXiv normalize filter')
##     a.add_mutually_exclusive_group(required=False)
##     a.add_argument('--unpublished-note', dest='unpublished_note',
##                           action='store_true')
##     a.add_argument('--eprint', action='store_true')

##     args = a.parse_args(shlex.split(optionstring));

##     mode = -1;
##     if (args.unpublished_note):
##         mode = MODE_UNPUBLISHED_NOTE;
##     elif (args.eprint):
##         mode = MODE_EPRINT;

##     return { 'mode': mode };


def getclass():
    return ArxivNormalizeFilter;

