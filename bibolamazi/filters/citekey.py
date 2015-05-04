################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2014 by Philippe Faist                                       #
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


import os
import os.path
import re
import codecs
import unicodedata
import string
import textwrap
import logging
logger = logging.getLogger(__name__)


from pybtex.database import BibliographyData, Entry;

from pylatexenc import latex2text

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList
from bibolamazi.core import butils

from .util import arxivutil

from .duplicates import normstr, fmtjournal, getlast, BORING_WORDS



# use lower case here.
BORING_TITLE_WORDS = [ x for x in BORING_WORDS ] + [
    'quantum',
    ]

# lower case
KNOWN_ABBREV = {
    'physics': 'Phys.',
    'physical': 'Phys.',
    'review': 'Rev.',
    'letters': 'Lett.',
    'international': 'Int.',
    'journal': 'J.',
    'optics': 'Opt.',
    'modern': 'Mod.',
    'history': 'Hist.',
    'philosophy': 'Phil.',
    'nature': 'Nat.',
    'communications': 'Comm.',
    'annalen': 'Ann.',
    'physik': 'Phys.',
    'electronic': 'El.',
    'electric': 'El.',
    'proceedings': 'Proc.',
    'computer': 'Comp.',
    'computing': 'Comp.',
    'applications': 'Appl.',
    'applied': 'Appl.',
    'theoretical': 'Theo.',
    'theory': 'Theo.',
    'statistical': 'Stat.',
    'probability': 'Prob.',
    'probabilistic': 'Prob.',
    }
NO_ABBREV = (
    'arxiv',
    )
KNOWN_JOURNALS = {
    'arxiv e-prints': 'arXiv',
    'science': 'Science',
    'nature': 'Nature',
    }




HELP_AUTHOR = u"""\
Cite-Key filter by Philippe Faist, (C) 2014, GPL 3+
"""

HELP_DESC = u"""\
Set the citation key of entries in a standard format
"""

HELP_TEXT = u"""
This filter replaces the bibtex citation key of all the concerned entries by a key
generated using a standard scheme.

Use the -sFormat="..." option to specify the standard citation key format. The format of
the citation key is specified with standard Python formatting placeholders, of the form
`%(<field name>)s`. Possible field names are:
  - `author`: the last name of the first author
  - `authors`: the last names of all authors, concatenated, truncated to 25 characters
  - `year`: four-digit year of publication (`year` field of the bibtex entry)
  - `year2`: same as `year`, but two-digit year instead (e.g. 88, 04)
  - `journal_abb`: very abbreviated journal name (e.g. PRL, NJP)
  - `journal`: somewhat shortened journal name (e.g. "Phys.Rev.Lett.")
  - `title_word`:  the first word of the title that is not 'a', 'the', 'and', ...
  - `doi`: the DOI digital identifier of the entry
  - `arxivid`: the arXiv ID of the entry, if available. Excludes the primary class, except
      for old-style IDs.
  - `primaryclass`: the arXiv primary category, if available.

If a field is given in the key but does not exist in the entry (e.g. `doi`, `arxivid`)
then the placeholder silently expands to an empty string.

Note that all the field values are strings (including year), so you'll never need the form
`%(..)d` or `%(..)<anything else>`

If the `-sFormat=...` option is not provided, then the default format
`%(author)s%(year)s%(journal_abb)s_%(title_word)s` is used.

Additionally, you can restrict which entries will be affected by this filter to a certain
sub-class of all entries using the `-dIfPublished=1/0` and `-sIfType=...` options.

If the `IfPublished` option is given, then the argument to the option (True or False)
determines whether only all published entries are affected or all unpublished entries are
affected. Entries with only arXiv identifiers and no journal information (see the `arXiv`
filter) are considered unpublished.

You can also set the `IfType` option to a comma-separated list of entry types that should
be affected. This can be any standard bibtex entry type, e.g. `article`, `book`,
`incollection`, etc.

The `IfPublished` and `IfType` options may be combined; in this case the entry will have
to satisfy both conditions in order to be affected.

NOTE: If two entries give the same citation key, then the second one will get a suffix to
differentiate it from the first. *WHICH ENTRY GETS THE SUFFIX IS UNDEFINED.* In this case,
it might be that the entries are duplicates. Consider then using the `duplicates` filter.
"""



class CiteKeyFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT


    def __init__(self, format="%(author)s%(year)s%(journal_abb)s_%(title_word)s", if_published=None, if_type=None):
        """
        CiteKeyFilter Constructor.

        Arguments:
         - format: Format of the citation key. Should contain placeholders %(author)s etc. 
             (See complete filter reference for details).
         - if_published(bool): If this option is specified, then only apply this filter to
             published or unpublished items, depending on the value given.
         - if_type(CommaStrList): You may specify a list of entry types to restrict the
             application of this filter to. By default, or if the list is empty, the filter
             applies to all entries.
        """

        BibFilter.__init__(self);

        self.fmt = format;
        self.if_published = None if (if_published is None or if_published == '') else butils.getbool(if_published);
        self.if_type = None if (if_type is None or if_type ==  '') else [x.strip() for x in if_type];

        logger.debug('citekey: fmt=%r', self.fmt)


    def getRunningMessage(self):
        return u"Generating standard citekeys"
    

    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE;


    def requested_cache_accessors(self):
        return [
            arxivutil.ArxivInfoCacheAccessor,
            arxivutil.ArxivFetchedAPIInfoCacheAccessor
            ]


    def filter_bibolamazifile(self, bibolamazifile):
        #
        # bibdata is a pybtex.database.BibliographyData object
        #
        bibdata = bibolamazifile.bibliographyData();

        arxivaccess = arxivutil.setup_and_get_arxiv_accessor(bibolamazifile)

        # first, find required fields and apply possible "filters"

        _rx_short_journal_known = re.compile(r'\b(?P<word>' + r'|'.join(KNOWN_ABBREV.keys()) + r')\b',
                                             re.IGNORECASE);
        def abbreviate(x):
            if x.lower() in NO_ABBREV:
                return x
            return x[0:3]+'.'

        def short_journal(x):
            if x.strip().lower() in KNOWN_JOURNALS:
                return KNOWN_JOURNALS[x.strip().lower()]
            x = _rx_short_journal_known.sub(lambda m: KNOWN_ABBREV[m.group('word').lower()], x);
            x = re.sub(r'\b(' + r'|'.join(BORING_WORDS) + r')\b(?!\s*($|[-:;\.]))', '', x, flags=re.IGNORECASE);
            x = re.sub(r'\b(?P<word>\w+)\b([^\.]|$)',
                       lambda m: abbreviate(m.group('word')), x);
            x = re.sub(r'[^\w.]+', '', x)
            if (len(x)>20):
                x = x[0:18]+'..'
            return x;

        def arxivInfo(entry, field):
            inf = arxivaccess.getArXivInfo(entry.key);
            if inf is None:
                return ''
            return inf[field]
        
        fld_fn = {
            'author': lambda entry: getlast(entry.persons['author'][0], lower=False)[0],
            'authors': lambda entry: "".join([getlast(a, lower=False)[0] for a in entry.persons['author']])[0:25],
            'year': lambda entry: entry.fields.get('year', ''),
            'year2': lambda entry: '%02d' % (int(entry.fields.get('year', '')) % 100),
            'journal_abb': lambda entry: fmtjournal(entry.fields.get('journal', '')),
            'journal': lambda entry: short_journal(normstr(delatex(entry.fields.get('journal', '')),lower=False)),
            'title_word': lambda entry: next(
                (word for word in re.sub(r'[^\w\s]', '', delatex(entry.fields.get('title', ''))).split()
                 if word.lower() not in BORING_TITLE_WORDS),
                ''
                 ),
            'doi': lambda entry: entry.fields.get('doi', ''),
            'arxivid': lambda entry: arxivInfo(entry, 'arxivid'),
            'primaryclass': lambda entry: arxivInfo(entry, 'primaryclass'),
            };
        # used fields
        fld = set([m.group('field') for m in re.finditer(r'(^|[^%])(%%)*%\((?P<field>\w+)\)', self.fmt)])
        # check all valid fields
        for f in fld:
            if f not in fld_fn:
                raise BibFilterError('citekey', "Invalid field `%s\' for citekey filter")

        logger.debug('Used fields are %r', fld)

        newbibdata = BibliographyData()
        
        class Jump: pass
        
        for (key, entry) in bibdata.entries.iteritems():

            keyorig = key
            
            try:
                ainfo = arxivaccess.getArXivInfo(key);
                if (self.if_published is not None):
                    if (not self.if_published and (ainfo is None or ainfo['published'])):
                        logger.longdebug('Skipping published entry %s (filter: unpublished)', key)
                        raise Jump
                    if (self.if_published and (ainfo is not None and not ainfo['published'])):
                        logger.longdebug('Skipping unpublished entry %s (filter: published)', key)
                        raise Jump
                if self.if_type is not None:
                    if entry.type not in self.if_type:
                        logger.longdebug('Skipping entry %s of different type %s (filter: %r)',
                                         key, entry.type, self.if_type)
                        raise Jump

                repldic = dict(zip(fld, [fld_fn[f](entry) for f in fld]));

                try:
                    key =  self.fmt % repldic;
                except ValueError as e:
                    raise BibFilterError('citekey', "Error replacing fields: %s" % (e))
                
            except Jump:
                pass
            finally:
                # avoid duplicate keys
                newkey = key
                count = 0
                while newkey in newbibdata.entries:
                    count += 1;
                    newkey = key + '.%d'%(count)
                if count:
                    logger.warning("`%s': Citation key `%s' already used: using `%s' instead.",
                                   keyorig, key, newkey)
                # add the entry
                newbibdata.add_entry(newkey, entry);

        bibolamazifile.setBibliographyData(newbibdata);

        return


def bibolamazi_filter_class():
    return CiteKeyFilter;





def delatex(s):
    if (not isinstance(s, unicode)):
        s = unicode(s.decode('utf-8'))
    return latex2text.latex2text(s);


