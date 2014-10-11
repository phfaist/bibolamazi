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

from pybtex.database import Person

from core.bibfilter import BibFilter, BibFilterError, CommaStrList
from core.blogger import logger
from core import butils
from core.pylatexenc import latexencode
from core.pylatexenc import latex2text


HELP_AUTHOR = u"""\
Fixes filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Fixes filter: perform some various known fixes for bibtex entries
"""

HELP_TEXT = u"""
Perform some various fixes for bibtex entries.

For now, the implemented fixes are:

  -dFixSwedishA
    Changes "\\AA berg" to "\\AA{}berg" to prevent bibtex/revtex from inserting
    a blank after the "\\AA". (This fix is needed for, e.g., the bibtex that
    Mendeley generates)

  -dEncodeUtf8ToLatex
    Encodes known non-ascii special characters, e.g. accented characters, into
    LaTeX equivalents. This affects ALL fields of the bibliographic entry.

  -dEncodeLatexToUtf8
    Encodes all LaTeX content, including accents and escape sequences, to unicode
    text saved as UTF-8. This affects ALL fields of the bibliographic entry.

  -dRemoveTypeFromPhd
    Removes any `type=' field from @phdthesis{..} bibtex entries if it contains
    the word(s) 'PhD' or 'Ph.D.'.

  -dRemoveFullBraces
  -sRemoveFullBraces=title,journal
    Removes the extra protective braces around the field value. For example,
      @article{...
        title = {{Irreversibility and Heat Generation in the Computing Process}},
        ...
      }
    will cause the title to be typeset with the given casing. This option will
    cause the field to be output as
      @article{...
        title = {Irreversibility and Heat Generation in the Computing Process},
        ...
      }
    so that the bibtex style can adapt the casing to any bibliography standard.
    If -dRemoveFullBraces is given, then this is applied to all fields except
    people (author and editors), otherwise this is applied only to the specified
    (comma-separated) fields of the bibtex entries.

  -sRemoveFullBracesNotLang=German
    Useful only if `RemoveFullBraces' is set. This option inhibits the removal of
    the extra braces if the language of the entry (as given by a bibtex
    language={...} field) is in the given list. This is useful, for example, to
    preserve the capitalization of nouns in German titles.

  -sProtectNames=Name1,Name2...
    A list of names that should be protected within most fields. Whenever a field
    contains one of the given names (as full word), then the name is wrapped in
    braces (e.g. "On Bell Experiments" -> "On {Bell} Experiments") in order to
    protect the possible upper casing. This applies to all fields except 'url',
    'file', and people (authors and editors).

  -dRemoveFileField
    Removes the field file={...} (that e.g. Mendeley introduces) from all entries. (This
    option is kept for compatibility, consider the newer and more flexible option
    -sRemoveFields below)

  -sRemoveFields=field1,field2...
    Removes the given fields from *all entries*. `fieldN` are BibTeX field names of fields
    to remove from all entries, e.g. `file', `issn', `note', etc.

  -dRemoveDoiPrefix
    Removes `doi:' prefix from all DOIs, if present.

"""



class FixesFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self,
                 fix_swedish_a=False,
                 encode_utf8_to_latex=False,
                 encode_latex_to_utf8=False,
                 remove_type_from_phd=False,
                 remove_full_braces=False,
                 remove_full_braces_not_lang=[],
                 protect_names=None,
                 remove_file_field=False,
                 remove_fields=[],
                 remove_doi_prefix=False):
        """
        Constructor method for FixesFilter

        Filter Arguments:
          - fix_swedish_a(bool): transform `\\AA berg' into `\\AA{}berg' (the former is generated e.g. by Mendeley
                        automatically); revtex tends to insert a blank after the `\\AA' otherwise.
          - encode_utf8_to_latex(bool): encode known non-ascii characters into latex escape sequences.
          - encode_latex_to_utf8(bool): encode known latex escape sequences to unicode text (utf-8).
          - remove_type_from_phd(bool): Removes any `type=' field from @phdthesis{..} bibtex entries.
          - remove_full_braces: removes overprotective global braces in field values.
          - remove_full_braces_not_lang(CommaStrList): (in conjunction with --remove-full-braces) removes the
            overprotective global braces only if the language of the entry (as per language={..} bibtex field)
            is not in the given list.
          - protect_names: list of names to protect from bibtex style casing.
          - remove_file_field(bool): removes file={...} fields from all entries.
          - remove_fields(CommaStrList): removes given fields from all entries.
          - remove_doi_prefix(bool): removes `doi:' prefix from all DOIs, if present
        """
        
        BibFilter.__init__(self);

        self.fix_swedish_a = butils.getbool(fix_swedish_a);

        self.encode_utf8_to_latex = butils.getbool(encode_utf8_to_latex);
        self.encode_latex_to_utf8 = butils.getbool(encode_latex_to_utf8);

        if (self.encode_utf8_to_latex and self.encode_latex_to_utf8):
            raise BibFilterError("Conflicting options: `encode_utf8_to_latex' and `encode_latex_to_utf8'.");

        self.remove_type_from_phd = butils.getbool(remove_type_from_phd);

        try:
            self.remove_full_braces = butils.getbool(remove_full_braces);
            self.remove_full_braces_fieldlist = None; # all fields
        except ValueError:
            # not boolean, we have provided a field list.
            self.remove_full_braces = True;
            self.remove_full_braces_fieldlist = [ x.strip().lower() for x in remove_full_braces.split(',') ];

        if self.remove_full_braces:
            if not remove_full_braces_not_lang:
                self.remove_full_braces_not_lang = []
            else:
                self.remove_full_braces_not_lang = [
                    x.lower()
                    for x in CommaStrList(remove_full_braces_not_lang)
                    ]
        else:
            self.remove_full_braces_not_lang = None

        if protect_names is not None:
            self.protect_names = dict([ (x.strip(), re.compile(r'\b'+x.strip()+r'\b', re.IGNORECASE))
                                        for x in protect_names.split(',') ]);
        else:
            self.protect_names = None;

        self.remove_file_field = butils.getbool(remove_file_field);
        self.remove_fields = CommaStrList(remove_fields);
        self.remove_doi_prefix = butils.getbool(remove_doi_prefix)


        logger.debug(('fixes filter: fix_swedish_a=%r; encode_utf8_to_latex=%r; encode_latex_to_utf8=%r; '
                      'remove_type_from_phd=%r; '
                      'remove_full_braces=%r [fieldlist=%r, not lang=%r],'
                      ' protect_names=%r, remove_file_field=%r'
                      'remove_fields=%r, remove_doi_prefix=%r')
                     % (self.fix_swedish_a, self.encode_utf8_to_latex, self.encode_latex_to_utf8,
                        self.remove_type_from_phd,
                        self.remove_full_braces, self.remove_full_braces_fieldlist,
                        self.remove_full_braces_not_lang,
                        self.protect_names,
                        self.remove_file_field,
                        self.remove_fields, self.remove_doi_prefix
                        ));
        

    def name(self):
        return "fixes"

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        # first apply filters that are applied to all fields of the entry

        def thefilter(x):
            if (self.fix_swedish_a):
                x = re.sub(r'\\AA\s+', r'\AA{}', x);
            if (self.encode_utf8_to_latex):
                x = latexencode.utf8tolatex(x, non_ascii_only=True);
            if (self.encode_latex_to_utf8):
                x = latex2text.latex2text(x);
            return x

        def filter_person(p):
            return Person(string=thefilter(unicode(p)));
            # does not work this way because of the way Person() splits at spaces:
            #parts = {}
            #for typ in ['first', 'middle', 'prelast', 'last', 'lineage']:
            #    parts[typ] = thefilter(u" ".join(p.get_part(typ)));
            #return Person(**parts);


        for (role,perslist) in entry.persons.iteritems():
            for k in range(len(perslist)):
                entry.persons[role][k] = filter_person(perslist[k]);
        
        for (k,v) in entry.fields.iteritems():
            entry.fields[k] = thefilter(v);


        # additionally:

        def filter_entry_remove_type_from_phd(entry):
            if (entry.type != 'phdthesis' or 'type' not in entry.fields):
                return
            if ('phd' in re.sub(r'[^a-z]', '', entry.fields['type'].lower())):
                # entry is phd type, so remove explicit type={}
                del entry.fields['type'];
            
        if (self.remove_type_from_phd):
            filter_entry_remove_type_from_phd(entry);


        def filter_entry_remove_full_braces(entry, fieldlist):
            for k,v in entry.fields.iteritems():
                if (fieldlist is None or k in fieldlist):
                    val = v.strip();
                    if (len(val) and val[0] == '{' and val[-1] == '}'):
                        # remove the extra braces.
                        entry.fields[k] = val[1:-1];

        if self.remove_full_braces:
            if entry.fields.get('language','').lower() not in self.remove_full_braces_not_lang:
                filter_entry_remove_full_braces(entry, self.remove_full_braces_fieldlist);


        def filter_protect_names(entry):
            for key, val in entry.fields.iteritems():
                if key in ('url', 'file'):
                    continue
                newval = val;
                for n,r in self.protect_names.iteritems():
                    newval = r.sub('{'+n+'}', newval);
                if (newval != val):
                    entry.fields[key] = newval;

        if (self.protect_names):
            filter_protect_names(entry);


        if (self.remove_file_field):
            if ('file' in entry.fields):
                del entry.fields['file'];

        if (self.remove_fields):
            for fld in self.remove_fields:
                entry.fields.pop(fld,None)

        if (self.remove_doi_prefix):
            if 'doi' in entry.fields:
                entry.fields['doi'] = re.sub(r'^\s*doi:\s*', '', entry.fields['doi'], flags=re.IGNORECASE)

        return entry;
    

def bibolamazi_filter_class():
    return FixesFilter;

