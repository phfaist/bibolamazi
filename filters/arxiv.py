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

from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;
from core import butils;


# possible modes in which to operate
MODE_NONE = 0;
MODE_UNPUBLISHED_NOTE = 1;
MODE_UNPUBLISHED_NOTE_NOTITLE = 2;
MODE_NOTE = 3;
MODE_EPRINT = 4;
MODE_STRIP = 5;

# a regex that we will need often
rxarxivinnote = re.compile(r'(([;,]\s+)?|\b|^)arXiv[-.:/\s]+(((?P<primaryclass>[-a-zA-Z]+)/)?(?P<arxivid>[0-9.]+))(\s*[;,]\s*|\s+|$)',
                           re.IGNORECASE);
rxarxivurl = re.compile(r'(([;,]\s+)?|\b|^)(?:http://)?arxiv\.org/(?:abs|pdf)/(?P<arxivid>[-a-zA-Z0-9./]+)\s*',
                        re.IGNORECASE);

# extract arXiv info from an entry
def getArXivInfo(entry):
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
        m = rxarxivinnote.search(notefield);
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
        m = rxarxivurl.search(notefield);
        if m:
            if (not d['arxivid']):
                try:
                    d['arxivid'] = m.group('arxivid');
                except IndexError:
                    logger.longdebug("rxarxivurl: indexerror for 'arxivid' group in note=%r, m=%r", notefield, m);
                    pass
                
    if ('note' in fields):
        processNoteField(fields['note'], d);

    if ('annote' in fields):
        processNoteField(fields['annote'], d);


    if (d['arxivid'] is None):
        # no arXiv info.
        return None

    # FIX: if archive-ID is old style, and does not contain the primary class, add it as "quant-ph/XXXXXXX"
    if (re.match(r'^\d{7}$', d['arxivid']) and len(d['primaryclass']) > 0):
        d['arxivid'] = d['primaryclass']+'/'+d['arxivid']
    
    logger.longdebug("got arXiv information: %r." %(d));
    return d


def stripArXivInfoInNote(notestr):
    """Assumes that notestr is a string in a note={} field of a bibtex entry, and strips any arxiv identifier
    information found, e.g. of the form 'arxiv:XXXX.YYYY' (or similar).
    """

    return rxarxivurl.sub('', rxarxivinnote.sub('', notestr));
    


HELP_AUTHOR = u"""\
ArXiv clean-up filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
ArXiv clean-up filter: normalizes the way each biblographic entry refers to arXiv IDs.
"""

HELP_TEXT = u"""
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
unpublished with arxiv IDs, specified as operating modes.

MODES:
    "none"    -- don't do anything--a no-op. Useful to act e.g. only on unpublished articles.
    "strip"   -- remove the arxiv information completely.
    "unpublished-note"  -- set the entry type to "unpublished", and add or append to the
                 note={} the string "arXiv:XXXX.YYYY". Any journal field is stripped.
    "unpublished-note-notitle"  -- Same as "unpublished-note", but additionally, strip the
                 `title' field (useful for revtex styles)
    "note"    -- just add or append to the note={} the string "arXiv:XXXX.YYYY". Don't change
                 the entry type. This mode is appropriate for entries that are published.
    "eprint"  -- keep the entry type as "article", and adds the tags "eprint" and "arxivid"
                 set to the detected arXiv ID, as well as a tag "primaryclass" set to the
                 primary archive (e.g. "quant-ph") if that information was detected. For
                 unpublished articles, also set journal={ArXiv e-prints} (or given arxiv
                 journal name in filter options)

ArXiv information is determined by inspecting the fields 'arxivid', 'eprint', 'primaryclass',
and 'note'. The entry is determined as unpublished if it is of type "unpublished", or if it
has no journal name, or if the journal name contains "arxiv".

"""


# the filter itself
class ArxivNormalizeFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT


    def __init__(self, mode="eprint", unpublished_mode=None, arxiv_journal_name="ArXiv e-prints",
                 theses_count_as_published=False):
        """
        Constructor method for ArxivNormalizeFilter
        
        *mode:  the behavior to adopt for published articles which also have an arxiv ID
        *unpublished_mode: the behavior to adopt for unpublished articles who have an arxiv
                ID (if None, use the same mode as `mode').
        *arxiv_journal_name: (in eprint mode): the string to set the journal={} entry to for
                unpublished entries
        *theses_count_as_published: if True, then entries of type @phdthesis and
                @mastersthesis count as published entries, otherwise not (the default).
        """
        
        BibFilter.__init__(self);

        self.mode = self._parse_mode(mode);
        self.unpublished_mode = (self._parse_mode(unpublished_mode) if unpublished_mode
                                 else self.mode);
        self.arxiv_journal_name = arxiv_journal_name;
        self.theses_count_as_published = butils.getbool(theses_count_as_published);

        logger.debug('arxiv filter constructor: mode=%d; unpublished_mode=%d' % (self.mode, self.unpublished_mode));

    def _parse_mode(self, mode):
        if (mode == "none" or mode is None):
            return MODE_NONE
        elif (mode == "unpublished-note"):
            return MODE_UNPUBLISHED_NOTE
        elif (mode == "unpublished-note-notitle"):
            return MODE_UNPUBLISHED_NOTE_NOTITLE
        elif (mode == "note"):
            return MODE_NOTE
        elif (mode == "eprint"):
            return MODE_EPRINT
        elif (mode == "strip"):
            return MODE_STRIP

        try:
            return int(mode)
        except ValueError:
            raise Exception("Invalid mode: %r" %(mode))


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

        if (entry.type == 'phdthesis' or entry.type == 'mastersthesis'):
            mode = (self.mode  if  self.theses_count_as_published  else  self.unpublished_mode)
        elif (not arxivinfo['published']):
            #logger.longdebug('entry not published : %r' % entry);
            mode = self.unpublished_mode
        else:
            mode = self.mode


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
            entry.fields['note'] = stripArXivInfoInNote(entry.fields['note']);
            if (not len(entry.fields['note'])):
                del entry.fields['note'];
        if ('annote' in entry.fields):
            entry.fields['annote'] = stripArXivInfoInNote(entry.fields['annote']);
            if (not len(entry.fields['annote'])):
                del entry.fields['annote'];

        if (entry.type == u'unpublished' or entry.type == u'misc'):
            entry.type = u'article';
            
        if (mode == MODE_STRIP):
            # directly return stripped entry.
            return entry

        def add_note(entry, arxivinfo):
            note = "{arXiv:"+arxivinfo['arxivid']+"}";
            if ('note' in entry.fields and entry.fields['note'].strip()):
                # some other note already there
                entry.fields['note'] += ', '+note;
            else:
                entry.fields['note'] = note;
            

        if (mode == MODE_UNPUBLISHED_NOTE or mode == MODE_UNPUBLISHED_NOTE_NOTITLE):
            # save arxiv information in the note={} field, and set type to unpublished if article
            if (entry.type == u'article'):
                # make sure we don't change, e.g, theses to "unpublished" !
                entry.type = u'unpublished'
            
            # 'unpublished' type should not have journal field set.
            if ('journal' in entry.fields):
                del entry.fields['journal']
            
            if (mode == MODE_UNPUBLISHED_NOTE_NOTITLE and 'title' in entry.fields):
                del entry.fields['title']

            add_note(entry, arxivinfo)

            return entry

        if (mode == MODE_NOTE):
            # save arxiv information in the note={} field, without changing entry type
            add_note(entry, arxivinfo)
            
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



def get_class():
    return ArxivNormalizeFilter;

