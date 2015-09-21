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
import logging
logger = logging.getLogger(__name__)

from pybtex.utils import CaseInsensitiveDict

from bibolamazi.core import bibfilter
from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList, enum_class
from bibolamazi.core import butils

from .util import arxivutil
from .util import entryfmt



class TolerantReplacer:
    def __init__(self, dic):
        self._dic = dic;
        logger.longdebug("TolerantReplacer: dic is %r", dic)

    def __getitem__(self, key):
        return self._dic.get(key, "")



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


NOTE FIELD FORMATTING (-sNoteStringFmt):

This is based on Python's new string formatting mini-language. Include fields with the syntax
`{format-str}':

    -sNoteStringFmt="arXiv:{arxiv.arxivid} [{arxiv.primaryclass}]"

The available fields and subfields are:

    'p.firstauthor' =>  first author (Person object)
    'p.authors' =>  list of bibtex entry authors (list of Person objects)
    'p.editors' =>  list of bibtex entry editors (list of Person objects)
    'p.persons' =>  dictionary with keys 'authors' and 'editors'
    'f' =>  object with all entry's bibtex fields (access as 'f.<FIELD>')
    'arxiv' =>  object with properties: (access as 'arxiv.<FIELD>')
        'primaryclass' =>  primary class, if available
        'arxivid' =>  the (minimal) arXiv ID (in format XXXX.XXXX  or  archive/XXXXXXX)
        'archiveprefix' =>  value of the 'archiveprefix' field
        'published' =>  True/False <whether this entry was published in a journal other than arxiv
        'doi' =>  DOI of entry if any, otherwise None
        'year' =>  Year in preprint arXiv ID number. 4-digit, string type.
        'isoldarxivid' =>  boolean which is True if the arXiv id is of the format 'archive/XXXXXXX'


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

Mode = enum_class('Mode', _modes, default_value=MODE_NONE, value_attr_name='mode')



# --- the filter object itself ---


class ArxivNormalizeFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT


    def __init__(self,
                 mode="eprint",
                 unpublished_mode=None,
                 arxiv_journal_name="ArXiv e-prints",
                 strip_unpublished_fields=[],
                 note_string="",
                 note_string_fmt="",
                 no_archive_prefix=False,
                 default_archive_prefix="arXiv",
                 no_primary_class_for_old_ids=False,
                 no_primary_class=False,
                 theses_count_as_published=False,
                 warn_journal_ref=True):
        """
        Constructor method for ArxivNormalizeFilter

        Arguments:
          - mode(Mode):  the behavior to adopt for published articles which also have an arxiv ID
          - unpublished_mode(Mode): the behavior to adopt for unpublished articles who have an arxiv
                   ID (if None, use the same mode as `mode').
          - strip_unpublished_fields(CommaStrList): (all modes): a list of bibtex fields to remove
                   from all unpublished entries.
          - arxiv_journal_name: (in eprint mode): the string to set the journal={} entry to for
                   unpublished entries
          - note_string: (obsolete, prefer -sNoteStringFmt) the string to insert in the `note' field
                   (for modes 'unpublished-note', 'note', and 'unpublished-note-notitle'). Use
                   `%(arxivid)s' to include the ArXiv ID itself in the string. Default:
                   '{arXiv:%(arxivid)s}'. Possible substitutions keys are
                   'arxivid','primaryclass','published','doi'. You can't specify both (-sNoteString
                   and -sNoteStringFmt).
          - note_string_fmt: the string to insert in the `note' field for modes 'unpublished-note',
                   'note' and 'unpublished-note-notitle'. This field uses Python's new advanced
                   formatting mini-language (see `string.Formatter`). The available fields and
                   formats are documented below in the filter documentation.
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
        self.strip_unpublished_fields = CommaStrList(strip_unpublished_fields)
        self.arxiv_journal_name = arxiv_journal_name;
        self.note_string = note_string;
        self.note_string_fmt = note_string_fmt;
        if (self.note_string and self.note_string_fmt):
            raise BibFilterError('arXiv', "Can't give both -sNoteString and -sNoteStringFmt !")
        if not self.note_string and not self.note_string_fmt:
            # nothing given, defaults to:
            self.note_string_fmt = "{{arXiv:{arxiv.arxivid}{if:(arxiv.isnewarxivid)( [{arxiv.primaryclass}])}}"
        self.no_archive_prefix = no_archive_prefix;
        self.default_archive_prefix = default_archive_prefix;
        self.no_primary_class_for_old_ids = butils.getbool(no_primary_class_for_old_ids);
        self.no_primary_class = butils.getbool(no_primary_class);
        self.theses_count_as_published = butils.getbool(theses_count_as_published);

        self.warn_journal_ref = butils.getbool(warn_journal_ref);

        logger.debug('arxiv filter constructor: mode=%s; unpublished_mode=%s' % (self.mode, self.unpublished_mode));


    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def requested_cache_accessors(self):
        return [
            arxivutil.ArxivInfoCacheAccessor,
            arxivutil.ArxivFetchedAPIInfoCacheAccessor
            ]

    def prerun(self, bibolamazifile):
        #
        # Make sure all entries are in the cache.
        #
        arxivutil.setup_and_get_arxiv_accessor(bibolamazifile)
        #
        # NEEDED TO PREVENT PERVERT BUG: make sure the arxiv information is
        # up-to-date. For example, if the duplicates filter aliased two entries, one WITH
        # arxiv info and one without, then make sure that if we query the key with the one
        # without that we still DO get the arxiv info.
        #
        logger.debug("arxiv prerun(): re-validating arxiv info cache")
        bibolamazifile.cacheAccessor(arxivutil.ArxivInfoCacheAccessor).revalidate(bibolamazifile)


    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        logger.longdebug('arxiv: processing entry %s', entry.key)

        arxivinfoaccessor = self.cacheAccessor(arxivutil.ArxivInfoCacheAccessor)
        arxivinfo = arxivinfoaccessor.getArXivInfo(entry.key)

        if (arxivinfo is None):
            logger.longdebug("    -> couldn't find any arxivinfo [from cache].")
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

        logger.longdebug("arXiv: entry %s: published=%r, mode=%r", entry.key, we_are_published, mode)

        if (mode == MODE_NONE):
            # don't change the entry, leave it as is.
            return

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

        if entry.type in (u'unpublished', u'misc',):
            entry.type = u'article';
            
        if (mode == MODE_STRIP):
            # directly leave entry stripped.
            return

        origentryfields = CaseInsensitiveDict(entry.fields.iteritems())

        def add_note(entry, arxivinfo):
            if (self.note_string):
                d = CaseInsensitiveDict(origentryfields.iteritems())
                d.update(arxivinfo)
                note = self.note_string % TolerantReplacer(d);
            elif (self.note_string_fmt):
                note = entryfmt.EntryFormatter(self.bibolamaziFile(), entry,
                                               arxivinfo=arxivinfo).format(self.note_string_fmt)

            if ('note' in entry.fields and entry.fields['note'].strip()):
                # some other note already there
                entry.fields['note'] += ', '+note;
            else:
                entry.fields['note'] = note;

        if not arxivinfo['published'] and self.strip_unpublished_fields:
            for field in self.strip_unpublished_fields:
                entry.fields.pop(field,'')

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

            logger.longdebug('Entry %s is now %r', entry.key, entry)

            return entry

        if (mode == MODE_NOTE):
            # save arxiv information in the note={} field, without changing entry type
            add_note(entry, arxivinfo)
            
            return

        if (mode == MODE_EPRINT):
            if (arxivinfo['published'] == False):
                # if the entry is unpublished, set the journal name to
                # "arXiv e-prints" (or whatever was specified by filter option)
                if self.arxiv_journal_name and entry.type in (u'article', u'unpublished',):
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

            return
        
        raise BibFilterError('arxiv', "Unknown mode: %s" % mode );



def bibolamazi_filter_class():
    return ArxivNormalizeFilter;



