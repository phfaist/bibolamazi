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


import os
import os.path
import re
import codecs
import unicodedata
import string
import textwrap


from pybtex.database import BibliographyData, Entry;


from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;
from core.pylatexenc import latex2text
from core import butils

from .util import arxivutil

### DON'T CHANGE THIS STRING. IT IS THE STRING THAT IS SEARCHED FOR IN AN EXISTING
### DUPFILE TO PREVENT OVERWRITING OF WRONG FILES.
### SERIOUSLY. IT DOESN'T NEED TO CHANGE.
BIBALIAS_WARNING_HEADER = """\
% NOTE: THIS FILE WAS AUTOMATICALLY GENERATED BY bibolamazi SCRIPT!
%       ANY CHANGES WILL BE LOST!
"""

BIBALIAS_HEADER = ur"""
%
####BIBALIAS_WARNING_HEADER####
%
% File automatically generated by bibolamazi's `duplicates` filter.
%
% You should include this file in your main LaTeX file with the command
%
%   \input{####DUP_FILE_NAME####}
%
% in your document preamble.
%

""".replace('####BIBALIAS_WARNING_HEADER####\n', BIBALIAS_WARNING_HEADER)

BIBALIAS_LATEX_DEFINITIONS = ur"""

%
% The following will define the command \bibalias{<alias>}{<source>}, which will make
% the command \cite[..]{<alias>} the same as doing \cite[..]{<source>}.
%
% This code has been copied and adapted from
%    http://tex.stackexchange.com/questions/37233/
%

\makeatletter
% \bibalias{<alias>}{<source>} makes \cite{<alias>} equivalent to \cite{<source>}
\newcommand\bibalias[2]{%
  \@namedef{bibali@#1}{#2}%
}


%
% Note: The `\cite` command provided here does not accept spaces in/between its
% arguments. This might be tricky, since revTeX does accept those spaces. You
% can work around by using LaTeX comments which automatically remove the
% following space after newline, in the following way:
%
%    \cite{key1,%
%          key2,%
%          key3%
%    }
%
% Make sure you don't add space between the comma and the percent sign.
%

\newtoks\biba@toks
\let\bibalias@oldcite\cite
\def\cite{%
  \@ifnextchar[{%
    \biba@cite@optarg%
  }{%
    \biba@cite{}%
  }%
}
\newcommand\biba@cite@optarg[2][]{%
  \biba@cite{[#1]}{#2}%
}
\newcommand\biba@cite[2]{%
  \biba@toks{\bibalias@oldcite#1}%
  \def\biba@comma{}%
  \def\biba@all{}%
  \@for\biba@one:=#2\do{%
    \@ifundefined{bibali@\biba@one}{%
      \edef\biba@all{\biba@all\biba@comma\biba@one}%
    }{%
      \PackageInfo{bibalias}{%
        Replacing citation `\biba@one' with `\@nameuse{bibali@\biba@one}'
      }%
      \edef\biba@all{\biba@all\biba@comma\@nameuse{bibali@\biba@one}}%
    }%
    \def\biba@comma{,}%
  }%
  \edef\biba@tmp{\the\biba@toks{\biba@all}}%
  \biba@tmp
}
\makeatother


%
% Now, declare all the alias keys.
%

"""



DUPL_WARN_TOP = """

    DUPLICATE ENTRIES WARNING
    -------------------------

"""

DUPL_WARN_ENTRY = """\
    %(alias)-20s   ** duplicate of **  %(orig)s
"""
DUPL_WARN_ENTRY_MIDCOL=4+20+3+len('** duplicate of **  ') + 2; # column no. to start text of "original"
DUPL_WARN_ENTRY_BEGCOL=6; # column no. to start text of "alias"
DUPL_WARN_ENTRY_COLSEP = 4
DUPL_WARN_ENTRY_COLWIDTH = DUPL_WARN_ENTRY_MIDCOL - DUPL_WARN_ENTRY_COLSEP - DUPL_WARN_ENTRY_BEGCOL

DUPL_WARN_BOTTOM = """\
    There were %(num_dupl)d duplicates.
    -------------------------

"""



# --------------------------------------------------


# some utilities


# these words will get stripped from journal names when forming abbreviations
BORING_WORDS = (
    "a",
    "of",
    "the",
    "in",
    "on",
    "and",
    "its",
    "de",
    "et",
    "der",
    "und",
    )


def normstr(x, lower=True):
    if not isinstance(x, unicode):
        x = unicode(x.decode('utf-8'))

    x2 = unicodedata.normalize('NFKD', x).strip();
    if lower:
        x2 = x2.lower();
    # remove any unicode compositions (accents, etc.)
    x2 = re.sub(r'[^\x00-\x7f]', '', x2.encode('utf-8')).decode('utf-8')
    ## additionally, remove any special LaTeX chars which may be written differently.
    #x2 = re.sub(r'\\([a-zA-Z]+|.)', '', x2);
    x2 = re.sub(r'''[\{\}\|\.\+\?\*\,\'\"\\]''', '', x2);
    x2 = re.sub(r'-+', '-', x2);
    logger.longdebug("Normalized string: %r -> %r", x, x2)
    return x2

def getlast(pers, lower=True):
    # join last names
    last = normstr(unicode(delatex(" ".join(pers.prelast()+pers.last())).split()[-1]), lower=lower)
    initial = re.sub('[^a-z]', '', normstr(u"".join(pers.first(True)),lower=lower),
                     flags=re.IGNORECASE)[0:1] # only first initial [a-z]
    return (last, initial);

def fmtjournal(x):
    if not isinstance(x, unicode):
        x = unicode(x.decode('utf-8'))
        
    x2 = normstr(x, lower=False)

    # drop "a", "the", "on", "of"
    # -- HACK to keep the `A' in ``Physics Review A'': Trick it into thinking as
    #    ``Physics Review Aaaa'', and then only capital letters are kept anyway
    x2 = re.sub(r'\s+(a)\s*([.:,]|$)', ' Aaaaaa', x2, flags=re.IGNORECASE)
    # --
    x2 = re.sub(r'\b(' + r'|'.join(BORING_WORDS) + r')\b', '', x2, flags=re.IGNORECASE)
    #logger.longdebug('fmtjournal TEMP: %r', x2)

    x2 = re.sub(r'\b([a-z])', lambda m: m.group().capitalize(), x2)
    x2 = re.sub(r'[^A-Z]', '', x2)
    #logger.longdebug('fmtjournal TEMP final: %r', x2)
    return x2







# --------------------------------------------------








HELP_AUTHOR = u"""\
Duplicates filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Filter that detects duplicate entries and produces rules to make one entry an alias of the other.
"""

HELP_TEXT = ur"""
This filter works by writing a LaTeX file to a specified location (via the
`dupfile' option) which contains the commands needed to define the bibtex
aliases.

Note that the dupfile option is mandatory in order to create the file with
duplicate definitions. You need to specify a file to write to. You may do this
with `--dupfile=dupfile.tex' or with `-sDupfile=dupfile.tex'.

In your main LaTeX document, you need to add the following command in the
preamble:

  \input{yourdupfile.tex}

where of couse yourdupfile.tex is the file that you specified to this filter.

Alternatively, if you just set the warn flag on, then a duplicate file is not
created (unless the dupfile option is given), and a warning is displayed for
each duplicate found.

The dupfile will be by default self-contained, i.e. will contain all the
definitions necessary so that you can use the different cite keys
transparently with the `\cite` LaTeX command. However the implementation of the
`\cite' command is a bit minimal. For example, no spaces are allowed between
its arguments, and other commands such as `\citep' are not supported.

If you specify the `-dCustomBibalias' option, then the dupfile will only contain
a list of duplicate definitions of the form

    \bibalias{<alias>}{<original>}

without any definition of the `\bibalias' command itself. It is thus up to the
user to provide a usable `\bibalias' command, before the `\input{<dupfile>}'
invocation. Use this option to get most flexibly on how you want to treat your
aliases, but this will require more work from your side.
"""


class DuplicatesFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT


    def __init__(self, dupfile=None, warn=False, custom_bibalias=False):
        r"""DuplicatesFilter constructor.

        *dupfile: the name of a file to write latex code for defining duplicates to. This file
                  will be overwritten!!
        *warn(bool): if this flag is set, dupfile is not mandatory, and a warning is issued
               for every duplicate entry found in the database.
        *custom_bibalias(bool): if set to TRUE, then no latex definitions will be generated
               in the file given in `dupfile', and will rely on a user-defined implementation
               of `\bibalias`.
        """

        BibFilter.__init__(self);

        self.dupfile = dupfile
        self.warn = butils.getbool(warn)
        self.custom_bibalias = butils.getbool(custom_bibalias)

        if (not self.dupfile and not self.warn):
            logger.warning("bibolamazi duplicates filter: no action will be taken as neither -sDupfile or"+
                           " -dWarn are given!")

        logger.debug('duplicates: dupfile=%r, warn=%r' % (dupfile, warn));


    def name(self):
        return "duplicates"

    def getRunningMessage(self):
        if (self.dupfile):
            return (u"processing duplicate entries. Don't forget to insert `\\input{%s}' in "
                    "your LaTeX file!" %(self.dupfile) );
        return u"processing duplicate entries (warning will be generated only)"
    

    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE;


    def prepare_entry_cache(self, a, cache_a, arxivaccess):

        cache_a['pers'] = [ getlast(pers) for pers in a.persons.get('author',[]) ]

        cache_a['arxivinfo'] = arxivaccess.getArXivInfo(a.key)

        note = a.fields.get('note', '')
        cache_a['note_cleaned'] = (arxivutil.stripArXivInfoInNote(note) if note else "")
        
        cache_a['j_abbrev'] = fmtjournal(a.fields.get('journal', ''))

        def cleantitle(title):
            title = unicodedata.normalize('NFKD', unicode(delatex(title).lower()))
            # remove any unicode compositions (accents, etc.)
            title = re.sub(r'[^\x00-\x7f]', '', title.encode('utf-8')).decode('utf-8')
            # remove any unusual characters
            title = re.sub(r'[^a-zA-Z0-9 ]', '', title)
            # remove any inline math
            title = re.sub(r'$[^$]+$', '', title)
            # clean up whitespace
            title = re.sub(r'\s+', ' ', title)
            return title.strip()

        cache_a['title_clean'] = cleantitle(a.fields.get('title', ''))


    def compare_entries_same(self, a, b, cache_a, cache_b):

        # compare author list first

        logger.longdebug('Comparing entries %s and %s', a.key, b.key)

        apers = cache_a['pers']
        bpers = cache_b['pers']

        if (len(apers) != len(bpers)):
            logger.longdebug("  Author list lengths %d and %d differ", len(apers), len(bpers))
            return False

        for k in range(len(apers)):
            (lasta, ina) = apers[k]
            (lastb, inb) = bpers[k]
            # use Levenshtein distance to detect possible typos or alternative spellings
            # (e.g. Koenig vs Konig). Allow one such typo per 8 characters.
            if (levenshtein(lasta, lastb) > (1+int(len(lasta)/8)) or (ina and inb and ina != inb)):
                logger.longdebug("  Authors %r and %r differ", (lasta, ina), (lastb, inb))
                return False

        #print "Author list matches! %r and %r "%(apers,bpers);

        def compare_neq_fld(x, y, fld, filt=lambda x: x):
            xval = x.get(fld, None);
            yval = y.get(fld, None);
            try:
                xval = xval.strip();
            except AttributeError:
                pass
            try:
                yval = yval.strip();
            except AttributeError:
                pass

            return xval is not None and yval is not None and filt(xval) != filt(yval) ;

        # authors are the same. check year
        if (compare_neq_fld(a.fields, b.fields, 'year')):
            logger.longdebug("  Years %r and %r differ", a.fields.get('year', None), b.fields.get('year', None))
            return False

        if (compare_neq_fld(a.fields, b.fields, 'month')):
            logger.longdebug("  Months %r and %r differ", a.fields.get('month', None), b.fields.get('month', None))
            return False

        doi_a = a.fields.get('doi')
        doi_b = b.fields.get('doi')
        if (doi_a and doi_b and doi_a != doi_b):
            logger.longdebug("  DOI's %r and %r differ", doi_a, doi_b)
            return False
        if (doi_a and doi_a == doi_b):
            logger.longdebug("  DOI's %r and %r are the same --> DUPLICATES", doi_a, doi_b)
            return True

        arxiv_a = cache_a['arxivinfo']
        arxiv_b = cache_b['arxivinfo']

        #logger.longdebug("  arxiv_a=%r, arxiv_b=%r", arxiv_a, arxiv_b)
        
        if (arxiv_a and arxiv_b and
            'arxivid' in arxiv_a and 'arxivid' in arxiv_b and
            arxiv_a['arxivid'] != arxiv_b['arxivid']):
            logger.longdebug("  arXiv IDS %r and %r differ", arxiv_a['arxivid'], arxiv_b['arxivid'])
            return False
        if (arxiv_a and arxiv_b and
            'arxivid' in arxiv_a and 'arxivid' in arxiv_b and
            arxiv_a['arxivid'] == arxiv_b['arxivid']):
            logger.longdebug("  arXiv IDS %r and %r same --> DUPLICATES", arxiv_a['arxivid'], arxiv_b['arxivid'])
            return True


        # if they have different notes, then they're different entries
        note_cl_a = cache_a['note_cleaned']
        note_cl_b = cache_b['note_cleaned']
        if (note_cl_a and note_cl_b and note_cl_a != note_cl_b):
            logger.longdebug("  Notes (cleaned up) %r and %r differ", note_cl_a, note_cl_b)
            return False

        # create abbreviations of the journals by keeping only the uppercase letters
        j_abbrev_a = cache_a['j_abbrev']
        j_abbrev_b = cache_b['j_abbrev']
        if (j_abbrev_a and j_abbrev_b and j_abbrev_a != j_abbrev_b):
            logger.longdebug("  Journal (parsed & simplified) %r and %r differ", j_abbrev_a, j_abbrev_b)
            return False

        if ( compare_neq_fld(a.fields, b.fields, 'volume') ):
            logger.longdebug("  Volumes %r and %r differ", a.fields.get('volume', None), b.fields.get('volume', None))
            return False

        if ( compare_neq_fld(a.fields, b.fields, 'number') ):
            logger.longdebug("  Numbers %r and %r differ", a.fields.get('numbers', None), b.fields.get('numbers', None))
            return False

        titlea = cache_a['title_clean']
        titleb = cache_b['title_clean']

        if (titlea and titleb and titlea != titleb):
            logger.longdebug("  Titles %r and %r differ.", titlea, titleb)
            return False

        # ### Unreliable. Bad for arxiv entries and had some other bugs. (E.g. "123--5" vs "123--125" vs "123")
        #
        #if ( compare_neq_fld(a.fields, b.fields, 'pages') ):
        #    print "pages differ!"
        #    import pdb; pdb.set_trace()
        #    return False

        #print "entries match!"
        logger.longdebug("  Entries %s and %s match.", a.key, b.key)

        # well at this point the publications are pretty much duplicates
        return True
        

    def update_entry_with_duplicate(self, origkey, origentry, duplkey, duplentry):
        """
        Merges definitions present in the duplicate entry, which are not present in the
        original. A very simple update-if-not-present mechanism is done, and no full-blown
        merge is performed. Simply entries which are not already present in the original
        are updated.
        """
        for (fk, fval) in duplentry.fields.iteritems():
            if (fk not in origentry.fields or not origentry.fields[fk].strip()):
                origentry.fields[fk] = fval


    def filter_bibolamazifile(self, bibolamazifile):
        #
        # bibdata is a pybtex.database.BibliographyData object
        #

        bibdata = bibolamazifile.bibliographydata();

        duplicates = [];

        newbibdata = BibliographyData();

        arxivaccess = arxivutil.get_arxiv_cache_access(bibolamazifile)

        # In a future version, we could imagine using the bibolamazi cache, and not recalculating
        # these values if they are already in the cache. However:
        #
        # NOTE: It is important that this cache is UP TO DATE, because otherwise if the user notices
        #       that two entries are matched falsely as duplicates and modifies one of the entries,
        #       it has to be picked up in the cache!
        #
        # So the simplest is to always recalculate the cache for all entries. It's fast in practice.
        # We actually don't need to store it in the bibolamazi cache.
        #
        #cache_entries = self.cache_for('duplicates_entryinfo_cache')
        cache_entries = {};

        for (key, entry) in bibdata.entries.iteritems():
            cache_entries[key] = {}
            self.prepare_entry_cache(entry, cache_entries[key], arxivaccess)

        for (key, entry) in bibdata.entries.iteritems():
            #
            # search the newbibdata object, in case this entry already exists.
            #
            logger.longdebug('inspecting new entry %s ...', key);
            is_duplicate_of = None
            for (nkey, nentry) in newbibdata.entries.iteritems():
                if self.compare_entries_same(entry, nentry, cache_entries[key], cache_entries[nkey]):
                    logger.longdebug('    ... matches existing entry %s!', nkey);
                    is_duplicate_of = nkey;
                    break

            #
            # if it's a duplicate
            #
            if is_duplicate_of is not None:
                dup = (key, is_duplicate_of)
                self.update_entry_with_duplicate(is_duplicate_of, newbibdata.entries[is_duplicate_of],
                                                 key, entry)
                duplicates.append(dup);
            else:
                newbibdata.add_entry(key, Entry(type_=entry.type,
                                                fields=entry.fields,
                                                persons=entry.persons,
                                                collection=entry.collection
                                                ));

        # output duplicates to the duplicates file

        if (self.dupfile):
            # set the new bibdata, without the duplicates
            bibolamazifile.setBibliographyData(newbibdata);
            # and write definitions to the dupfile
            dupfilepath = os.path.join(bibolamazifile.fdir(),self.dupfile);
            check_overwrite_dupfile(dupfilepath);
            dupstrlist = [];
            with codecs.open(dupfilepath, 'w', 'utf-8') as dupf:
                dupf.write(BIBALIAS_HEADER.replace('####DUP_FILE_NAME####', self.dupfile));
                if not self.custom_bibalias:
                    dupf.write(BIBALIAS_LATEX_DEFINITIONS)
                for (dupalias, duporiginal) in duplicates:
                    dupf.write((r'\bibalias{%s}{%s}' % (dupalias, duporiginal)) + "\n");
                    dupstrlist.append("\t%s is an alias of %s" % (dupalias,duporiginal)) ;

                dupf.write('\n\n');

            # issue debug message
            logger.debug("wrote duplicates to file: \n" + "\n".join(dupstrlist));

        if (self.warn and duplicates):
            def warnline(dupalias, duporiginal):
                def fmt(key, entry, cache_entry):
                    s = ", ".join(string.capwords('%s, %s' % (x[0], "".join(x[1]))) for x in cache_entry['pers']);
                    if 'title_clean' in cache_entry and cache_entry['title_clean']:
                        s += ', "' + (cache_entry['title_clean']).capitalize() + '"'
                    if 'j_abbrev' in cache_entry and cache_entry['j_abbrev']:
                        s += ', ' + cache_entry['j_abbrev']

                    f = entry.fields
                    if f.get('month',None) and f.get('year',None):
                        s += ', ' + f['month'] + ' ' + f['year']
                    elif f.get('month', None):
                        s += ', ' + f['month'] + ' <unknown year>'
                    elif f.get('year', None):
                        s += ', ' + f['year']
                        
                    if 'doi' in entry.fields and entry.fields['doi']:
                        s += ', doi:'+entry.fields['doi']
                    if 'arxivinfo' in cache_entry and cache_entry['arxivinfo']:
                        s += ', arXiv:'+cache_entry['arxivinfo']['arxivid']
                    if 'note_cleaned' in cache_entry and cache_entry['note_cleaned']:
                        s += '; ' + cache_entry['note_cleaned']

                    return s

                tw = textwrap.TextWrapper(width=DUPL_WARN_ENTRY_COLWIDTH)

                fmtalias = fmt(dupalias, bibdata.entries[dupalias], cache_entries[dupalias])
                fmtorig = fmt(duporiginal, bibdata.entries[duporiginal], cache_entries[duporiginal])
                linesalias = tw.wrap(fmtalias)
                linesorig = tw.wrap(fmtorig)
                maxlines = max(len(linesalias), len(linesorig))
                return (DUPL_WARN_ENTRY % { 'alias': dupalias,
                                            'orig': duporiginal
                                            }
                        + "\n".join( ('%s%s%s%s' %(' '*DUPL_WARN_ENTRY_BEGCOL,
                                                   linealias + ' '*(DUPL_WARN_ENTRY_COLWIDTH-len(linealias)),
                                                   ' '*DUPL_WARN_ENTRY_COLSEP,
                                                   lineorig)
                                      for (linealias, lineorig) in
                                      zip(linesalias + ['']*(maxlines-len(linesalias)),
                                          linesorig + ['']*(maxlines-len(linesorig)))) )
                        + "\n\n"
                        )
            logger.warning(DUPL_WARN_TOP  +
                           "".join([ warnline(dupalias, duporiginal)
                                     for (dupalias, duporiginal) in duplicates
                                     ])  +
                           DUPL_WARN_BOTTOM % {'num_dupl': len(duplicates)});

        return


def bibolamazi_filter_class():
    return DuplicatesFilter;





def delatex(s):
    # Fixed: bug in pybtex.
    #    ### FIXME: Where the hell are all the "\~"'s being replaced by "\ " ??
    #    s = s.replace(r'\ ', r'\~');
    return latex2text.latex2text(unicode(s));



# utility: taken from http://hetland.org/coding/python/levenshtein.py
#
# used to detect small differences in names which can result from either typos, or
# alternative spellings (e.g. 'Konig' vs 'Koenig')
def levenshtein(a,b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a,b = b,a
        n,m = m,n
        
    current = range(n+1)
    for i in range(1,m+1):
        previous, current = current, [i]+[0]*n
        for j in range(1,n+1):
            add, delete = previous[j]+1, current[j-1]+1
            change = previous[j-1]
            if a[j-1] != b[i-1]:
                change = change + 1
            current[j] = min(add, delete, change)
            
    return current[n]




def check_overwrite_dupfile(dupfilepath):
    if (not os.path.exists(dupfilepath)):
        return
    # path item exists (but could be dir, etc.)
    if (not os.path.isfile(dupfilepath)):
        raise BibFilterError('duplicates', "Can't overwrite non-file path `%s'"% (dupfilepath))
    
    with codecs.open(dupfilepath, 'r') as f:
        head_content = u'';
        for countline in xrange(10):
            head_content += f.readline()

    if BIBALIAS_WARNING_HEADER not in head_content:
        raise BibFilterError('duplicates', "File `%s' does not seem to have been generated by bibolamazi. Won't overwrite. Please remove the file manually." %(dupfilepath))
