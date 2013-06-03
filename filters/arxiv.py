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


import re
#import shlex
#import argparse


from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;

HELPDESC = u"""
ArXiv clean-up filter: normalizes the way each biblographic entry refers to arXiv IDs.
"""

HELPTEXT = u"""
There are two common ways to include arXiv IDs in bib files:
    @unpublished{Key,
      authors = ...
      ...
      note = {arXiv:XXXX.YYYY}
    }
and
    @article{Key,
      ...
      journal = {ArXiv e-prints},
      ...
      arxivid = {XXXX.YYYY}
          OR
      eprint = {XXXX.YYYY}
    }

And of course, each bibtex style handles maybe one but not the other, and then they appear
differently, and so on. In addition, if you want to add an arXiv ID to published articles,
it may also appear either in the note={} or in the eprint={} tag.

THIS FILTER will detect the various ways of declaring arXiv information and extract it for
each entry. Then this information is reproduced in each entry using a single of the above
conventions, depending on the provided options. Entries with no arxiv information are left
untouched. Different behaviors can be set independently for published articles and
unpublished with arxiv IDs:
    "none"    -- don't do anything--a no-op. Useful to act e.g. only on unpublished articles.
    "strip"   -- remove the arxiv information completely.
    "unpublished-note"  -- set the entry type to "unpublished", add or append to the note={}
                 the string "arXiv:XXXX.YYYY" and set journal={ArXiv e-prints}
    "eprint"  -- keep the entry type as "article", and adds the tags "eprint" and "arxivid"
                 set to the detected arXiv ID, as well as a tag "primaryclass" set to the
                 primary archive (e.g. "quant-ph") if that information was detected.


"""




MODE_NONE = 0;
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

    # FIX: if archive-ID is old style, and does not contain the primary class, add it as "quant-ph/XXXXXXX"
    if (re.match(r'^\d{7}$', d['arxivid']) and len(d['primaryclass']) > 0):
        d['arxivid'] = d['primaryclass']+'/'+d['arxivid']
    
    return d


class ArxivNormalizeFilter(BibFilter):
    
    helpdescription = HELPDESC;
    helptext = HELPTEXT;

    def __init__(self, mode=MODE_EPRINT, unpublished_mode=None, arxiv_journal_name="ArXiv e-prints"):
        """
        Constructor method for ArxivNormalizeFilter
        
        *mode: the behavior to adopt for published articles which also have an arxiv ID
        *unpublished_mode: the behavior to adopt for unpublished articles who have an arxiv ID
        *arxiv_journal_name: (in eprint mode): the string to set the journal={} entry to for
                             unpublished entries
        """
        
        BibFilter.__init__(self);

        self.mode = self._parse_mode(mode);
        self.unpublished_mode = (self._parse_mode(unpublished_mode) if unpublished_mode
                                 else self.mode);
        self.arxiv_journal_name = arxiv_journal_name;

        logger.debug('arxiv filter constructor: mode=%d; unpublished_mode=%d' % (self.mode, self.unpublished_mode));

    def _parse_mode(self, mode):
        if (mode == "none" or mode is None):
            return MODE_NONE;
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

        mode = self.mode
        if (not arxivinfo['published']):
            #logger.debug('entry not published : %r' % entry);
            mode = self.unpublished_mode

        if (mode == MODE_NONE):
            # don't change the entry, return it as is.
            return entry;

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
            if (arxivinfo['published'] == False):
                # if the entry is unpublished, set the journal name to
                # "arXiv e-prints" (or whatever was specified by filter option)
                entry.fields['journal'] = self.arxiv_journal_name;
                entry.fields.pop('pages','');
                
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


def get_class():
    return ArxivNormalizeFilter;

