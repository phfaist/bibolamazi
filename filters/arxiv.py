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

from core import bibfilter
from core.bibfilter import BibFilter, BibFilterError
from core.blogger import logger
from core import butils

from .util import arxivutil



# --- help texts ---



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
    "strip"   -- remove the arxiv information completely. Note that arXiv URLs are left, use
                 the `url` filter if you want to strip those.
    "unpublished-note"  -- set the entry type to "unpublished", and add or append to the
                 note={} the string "arXiv:XXXX.YYYY". Any journal field is stripped.
    "unpublished-note-notitle"  -- Same as "unpublished-note", but additionally, strip the
                 `title' field (useful for revtex styles)
    "note"    -- just add or append to the note={} the string "arXiv:XXXX.YYYY". Don't change
                 the entry type. This mode is appropriate for entries that are published. 
                 The string "arXiv:XXXX.YYYY" can be changed by specifying the
                 -sNoteString="arXiv:%(arxivid)s" option [use `%(arxivid)s' to include the
                 arXiv ID].
    "eprint"  -- keep the entry type as "article", and adds the tags "archivePrefix",
                 "eprint" and "arxivid" set to the detected arXiv ID, as well as a tag
                 "primaryclass" set to the primary archive (e.g. "quant-ph") if that
                 information was detected. For unpublished articles, also set
                 journal={ArXiv e-prints} (or given arxiv journal name in filter options)

ArXiv information is determined by inspecting the fields 'arxivid', 'eprint', 'primaryclass',
and 'note'. The entry is determined as unpublished if it is of type "unpublished", or if it
has no journal name, or if the journal name contains "arxiv".

Missing information, if an arXiv ID was detected, is queried on the arxiv.org database using
the arxiv.org API (via the arxiv2bib module, Copyright (c) 2012, Nathan Grigg, New BSD License.
See the original copyright in the folder '3rdparty/arxiv2bib/' of this project)


"""



# --- arxiv info handling modes ---


# possible modes in which to operate
MODE_NONE = 0;
MODE_UNPUBLISHED_NOTE = 1;
MODE_UNPUBLISHED_NOTE_NOTITLE = 2;
MODE_NOTE = 3;
MODE_EPRINT = 4;
MODE_STRIP = 5;


# All these defs are useful for the GUI

_modes = [
    ('none', MODE_NONE),
    ('unpublished-note', MODE_UNPUBLISHED_NOTE),
    ('unpublished-note-notitle', MODE_UNPUBLISHED_NOTE_NOTITLE),
    ('note', MODE_NOTE),
    ('eprint', MODE_EPRINT),
    ('strip', MODE_STRIP),
    ];
#_modes_dict = dict(_modes)

Mode = bibfilter.enum_class('Mode', _modes, default_value=MODE_NONE, value_attr_name='mode')



# --- the filter object itself ---


class ArxivNormalizeFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT


    def __init__(self, mode="eprint", unpublished_mode=None, arxiv_journal_name="ArXiv e-prints",
                 note_string="{arXiv:%(arxivid)s}", no_archive_prefix=False,
                 default_archive_prefix="arXiv", no_primary_class_for_old_ids=False,
                 no_primary_class=False,
                 theses_count_as_published=False, warn_journal_ref=True):
        """
        Constructor method for ArxivNormalizeFilter

        Arguments:
          - mode(Mode):  the behavior to adopt for published articles which also have an arxiv ID
          - unpublished_mode(Mode): the behavior to adopt for unpublished articles who have an arxiv
                   ID (if None, use the same mode as `mode').
          - arxiv_journal_name: (in eprint mode): the string to set the journal={} entry to for
                   unpublished entries
          - note_string: the string to insert in the `note' field (for modes 'unpublished-note',
                   'note', and 'unpublished-note-notitle'). Use `%(arxivid)s' to include the ArXiv
                   ID itself in the string. Default: '{arXiv:%(arxivid)s}'. Possible substitutions
                   keys are 'arxivid','primaryclass','published','doi'.
          - no_archive_prefix(bool): If set, then removes the 'archiveprefix' key entirely.
          - default_archive_prefix: In `eprint' mode, entries which don't have an archive prefix are
                   given this one. Additionally, other entries whose archive prefix match this one
                   up to letter casing are adjusted to this one. (Default: "arXiv")
          - no_primary_class_for_old_ids(bool): if True, then in `eprint' mode no 'primaryclass' field
                   is set if the entry has an "old" arXiv ID identifier already containing the
                   primary-class, e.g. "quant-ph/YYYYZZZ".
          - no_primary_class(bool): if True, then the `primaryclass' field is always stripped.
          - theses_count_as_published(bool): if True, then entries of type @phdthesis and
                   @mastersthesis count as published entries, otherwise not (the default).
          - warn_journal_ref(bool): if True, then for all articles that look unpublished in our
                   database, but for which the arXiv.org API reports a published version, we produce
                   a warning (this is the default; set this option to false to suppress these
                   warnings).

        """
        
        BibFilter.__init__(self);

        self.mode = Mode(mode);
        self.unpublished_mode = (Mode(unpublished_mode) if unpublished_mode is not None
                                 else self.mode);
        self.arxiv_journal_name = arxiv_journal_name;
        self.note_string = note_string;
        self.no_archive_prefix = no_archive_prefix;
        self.default_archive_prefix = default_archive_prefix;
        self.no_primary_class_for_old_ids = butils.getbool(no_primary_class_for_old_ids);
        self.no_primary_class = butils.getbool(no_primary_class);
        self.theses_count_as_published = butils.getbool(theses_count_as_published);

        self.warn_journal_ref = butils.getbool(warn_journal_ref);

        logger.debug('arxiv filter constructor: mode=%s; unpublished_mode=%s' % (self.mode, self.unpublished_mode));


    def name(self):
        return "arxiv"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #
        
        #import pdb;pdb.set_trace()

        arxivinfo = arxivutil.get_arxiv_cache_access(self.bibolamaziFile()).getArXivInfo(entry.key);

        if (arxivinfo is None):
            # no arxiv info--don't do anything
            return entry

        logger.longdebug('Got entry arxiv info: %s (%s): %r', entry.key, entry.type, arxivinfo);

        we_are_published = None
        if (entry.type == 'phdthesis' or entry.type == 'mastersthesis'):
            we_are_published = self.theses_count_as_published
        elif (not arxivinfo['published']):
            #logger.longdebug('entry not published : %r' % entry);
            we_are_published = False
        else:
            we_are_published = True

        if (we_are_published):
            mode = self.mode
        else:
            mode = self.unpublished_mode

        if (self.warn_journal_ref and not we_are_published and arxivinfo['doi']):
            # we think we are not published but we actually are, as reported by arXiv.org API. This
            # could be because the authors published their paper in the meantime.
            logger.warning("arxiv: Entry `%s' refers to arXiv version of published entry with DOI %r",
                           entry.key, arxivinfo['doi'])

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
            entry.fields['note'] = arxivutil.stripArXivInfoInNote(entry.fields['note']);
            if (not len(entry.fields['note'])):
                del entry.fields['note'];
        if ('annote' in entry.fields):
            entry.fields['annote'] = arxivutil.stripArXivInfoInNote(entry.fields['annote']);
            if (not len(entry.fields['annote'])):
                del entry.fields['annote'];
        # keep arxiv URL. This should be stripped off in the url filter, if needed.
        #if ('url' in entry.fields):
        #    #entry.fields['url'] = arxivutil.stripArXivInfoInNote(entry.fields['url']);
        #    #if (not len(entry.fields['url'])):
        #    #    del entry.fields['url'];

        if (entry.type == u'unpublished' or entry.type == u'misc'):
            entry.type = u'article';
            
        if (mode == MODE_STRIP):
            # directly return stripped entry.
            return entry

        def add_note(entry, arxivinfo):
            note = self.note_string % arxivinfo;
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
                entry.fields['journal'] = self.arxiv_journal_name
                entry.fields.pop('pages','')

            if not self.no_archive_prefix:
                if (not arxivinfo.get('archiveprefix','') or
                    arxivinfo.get('archiveprefix','').lower() == self.default_archive_prefix.lower()):
                    # no given archiveprefix or already default, but possibly not capitalized the same
                    entry.fields['archiveprefix'] = self.default_archive_prefix
                else:
                    entry.fields['archiveprefix'] = arxivinfo['archiveprefix']
            entry.fields['arxivid'] = arxivinfo['arxivid']
            entry.fields['eprint'] = arxivinfo['arxivid']
            if (arxivinfo['primaryclass']):
                # see if we want to set the primary class
                ok = True
                if self.no_primary_class:
                    ok = False
                elif '/' in arxivinfo['arxivid'] and self.no_primary_class_for_old_ids:
                    # quant-ph/XXXZZZZ old id
                    ok = False
                # maybe set the primary class:
                if ok:
                    entry.fields['primaryclass'] = arxivinfo['primaryclass']

            return entry
        
        raise BibFilterError('arxiv', "Unknown mode: %s" % mode );



def bibolamazi_filter_class():
    return ArxivNormalizeFilter;



