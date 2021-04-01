# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2019 by Philippe Faist                                       #
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
import unicodedata
import logging
logger = logging.getLogger(__name__)

from pybtex.database import Person
from pybtex.bibtex.utils import split_tex_string

from pylatexenc import latexencode, latexwalker, latex2text

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList, ColonCommaStrDict, multi_type_class
from bibolamazi.core import butils




HELP_AUTHOR = r"""
Philippe Faist, (C) 2019, GPL 3+
"""

HELP_DESC = r"""
Perform some various known fixes for bibtex entries
"""

HELP_TEXT = r"""
Perform some various fixes for bibtex entries.

The possible fixes are listed above as Filter Options.  Here is some additional
related information.


*** Removing Overprotective Full Braces in Field Values:

  -dRemoveFullBraces
  -sRemoveFullBraces=title,journal

    Removes the extra protective braces around the field value. For example,

      @article{...
        title = {{Irreversibility and Heat Generation in the Computing Process}},
        ...
      }

    will cause the title to be typeset with the given casing. The present option
    causes the field to be output as

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
    preserve the capitalization of nouns in German titles. (Comparision is done
    case insensitive.)


*** Protecting Uppercase Letters:

  -dProtectCaptialLetterAfterDot
  -dProtectCaptialLetterAtBegin
  -sProtectCaptialLetterAfterDot=title
  -sProtectCaptialLetterAtBegin=title

    In the given fields, or in the title if -dProtectCapitalLetter... is
    provided, protect capital letters following full stops and colons
    (...AfterDot) or at the beginning of the field (...AtBegin) using braces, to
    ensure they are displayed as capital letters. For example,

        title = {Exorcist {XIV}. Part {I}. From {Maxwell} to {Szilard}}

    becomes

        title = {{E}xorcist {XIV}. {P}art {I}. {F}rom {Maxwell} to {Szilard}}


*** Replacing Quotes by LaTeX Macros:

  -dConvertDblQuotes
  -sConvertDblQuotes=title
  -dConvertSglQuotes
  -sConvertSglQuotes=title
  -sDblQuoteMacro=\qq
  -sSglQuoteMacro=\q

    If provided, expressions in double (resp. single) quotes are detected and
    automatically converted to use the given LaTeX macro (which defaults to \qq
    and \q, respectively). For example,

        title = {``Relative state'' formulation of quantum mechanics}

    is converted to

        title = {\qq{Relative state} formulation of quantum mechanics}

    This may be useful if you do fancy stuff with your quotes in your document,
    such as permuting the punctuation etc. (See also the LaTeX package
    {csquotes})

"""




_BoolOrFieldList_doc = """\
A boolean (True/1/Yes/On or False/0/No/Off) or a comma-separated list of bibtex field names."""
BoolOrFieldList = multi_type_class('BoolOrFieldList',
                                   [(bool, 'on/off'), (CommaStrList, 'list of fields')],
                                   doc=_BoolOrFieldList_doc)




_rx_pages_ranges = re.compile(r'^\s*(?P<a>[0-9A-Za-z./]+)\s*\{?\s*'
                              r'(?P<hyphen>(?:[-'
                                '\u2010\u2011\u2012\u2013\u2014\u2015\u2E3A\u2E3B\uFE58\uFE63'
                              r']|\\(?:textendash|textemdash)\b)+)'
                              r'\s*\}?\s*(?P<b>[0-9A-Za-z./]+)\s*$')




class FixesFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self,
                 fix_space_after_escape=False,
                 encode_utf8_to_latex=False,
                 encode_latex_to_utf8=False,
                 remove_type_from_phd=False,
                 remove_pages_from_book=False,
                 remove_full_braces=False,
                 remove_full_braces_not_lang=[],
                 protect_names=None,
                 remove_file_field=False,
                 remove_fields=[],
                 remove_doi_prefix=False,
                 map_annote_to_note=False,
                 auto_urlify=False,
                 rename_language={},
                 fix_mendeley_bug_urls=False,
                 protect_capital_letter_after_dot=False,
                 protect_capital_letter_at_begin=False,
                 convert_dbl_quotes=False,
                 convert_sgl_quotes=False,
                 dbl_quote_macro=r'\qq',
                 sgl_quote_macro=r'\q',
                 unprotect_full_last_names=False,
                 fix_pages_range=False,
                 fix_pages_range_hyphen='--',
                 #
                 # obsolete:
                 unprotect_zotero_title_case=False,
                 fix_swedish_a=False):
        r"""
        Constructor method for FixesFilter

        Arguments:

          - fix_space_after_escape(bool): 

            Removes any space after a LaTeX escape and replaces it by a pair of
            braces.  (Some bibtex styles wrongfully split a word in such cases.)
            For example, "\AA berg" is replaced by "\AA{}berg".

          - encode_utf8_to_latex(bool):

            Encodes known non-ascii special characters, e.g. accented characters, into
            LaTeX equivalents. This affects ALL fields of the bibliographic entry.
            (Cannot be used in conjunction with -dEncodeLatexToUtf8.)

          - encode_latex_to_utf8(bool):

            Replaces LaTeX macros and accents with their unicode representation.
            This affects ALL fields of the bibliographic entry.  (Cannot be used
            in conjunction with -dEncodeUtf8ToLatex.)

          - remove_type_from_phd(bool):

            Removes any ‘type={...}’ field from bibtex entries of type
            ‘@phdthesis{..}’ as long as the type contains the word(s) ‘PhD’ or
            ‘Ph.D.’ (or something close to that).

          - remove_pages_from_book(bool):

            Remove the ‘pages={...}’ field from ‘@book{...}’ bibtex entries.

          - remove_full_braces(BoolOrFieldList):

            Remove overprotective global braces in field values.  See below
            (Filter Documentation) for additional information.

          - remove_full_braces_not_lang(CommaStrList):

            (in conjunction with --remove-full-braces) removes the
            overprotective global braces only if the language of the entry (as
            per language={..} bibtex field) is not in the given list (case
            insensitive).

          - protect_names(CommaStrList):

            A list of names that should be protected within most
            fields. Whenever a field contains one of the given names (as full
            word), then the name is wrapped in braces (e.g. "On Bell
            Experiments" → "On {Bell} Experiments") in order to protect the
            possible upper casing. This applies to all fields except ‘url’,
            ‘file’, and people (authors and editors).  Use, e.g.,
            -sProtectNames="Newton,Bell,Einstein"

          - remove_file_field(bool):

            Remove the ‘file={...}’ field from all entries.  See also
            -sRemoveFields.

          - remove_fields(CommaStrList): removes given fields from all entries.

            Removes the given fields from all entries.  Use the syntax
            -sRemoveFields=field1,field2,...  where `fieldN` are BibTeX field
            names of fields to remove from all entries.,
            e.g. -sRemoveFields=file,issn,note

          - remove_doi_prefix(bool):

            Remove the ‘doi:’ prefix from all DOIs in all ‘doi={...}’ fields, if
            present.

          - map_annote_to_note(bool):

            Changes the ‘annote={...}’ field to ‘note={...}’. If the ‘note’
            field already has contents, the contents of the ‘annote’ field is
            appended to the existing ‘note’ field.

          - auto_urlify(BoolOrFieldList):

            Automatically wrap strings that look like an URL in the ‘note’ field
            into ‘\url{}’ commands.  Use -dAutoUrlify to enable the default
            settings or -sAutoUrlify=field1,field2,... to specify a list of
            fields to act on.  If a comma-separated list of fields is provided,
            then the auto-urlification is applied only to those given bibtex
            fields.

          - rename_language(ColonCommaStrDict):

            Change ‘language={...}’ field by applying a set of replacement
            rules.  E.g., you can change "de" into "German".  An alias (case
            insensitive) is replaced by its corresponding language.
            Replacements are not done recursively.  Use the syntax
            -sRenameLanguage=alias1:language1,alias2:language2...

          - fix_mendeley_bug_urls(BoolOrFieldList):

            Mendeley's BibTeX output currently is buggy and escapes URLs with
            signs like $\sim$ etc.  This option enables reverting Mendeley's
            escape sequences back to URL characters (for known escape Mendeley
            sequences).  This option is off by default. Use the
            ‘-sFixMendeleyBugUrls=field1,field2...’ syntax to specify a list of
            bibtex fields on which to act (but not author nor editor). If the
            ‘-dFixMendeleyBugUrls’ variant is given, the only the ‘url={...}’
            bibtex field is processed.

          - protect_capital_letter_after_dot(BoolOrFieldList):

            Place first (capital) letter after a full stop or colon in
            protective braces (for the the given bibtex fields).  Pass True or
            False here, or a list of fields on which to act (by default only
            ‘title’).  See below (Filter Documentation) for additional
            information.

          - protect_capital_letter_at_begin(BoolOrFieldList):

            Place first (capital) letter of a field in protective braces (for
            the the given bibtex fields).  Pass True or False here, or a list of
            fields on which to act (by default only ‘title’).  See below (Filter
            Documentation) for additional information.

          - convert_dbl_quotes(BoolOrFieldList):

            Detect double-quoted expressions and replace them by a call to a
            LaTeX macro.  Pass True or False here, or a list of fields on which
            to act (by default ‘title,abstract,booktitle,series’).  See below
            (Filter Documentation) for additional information; see also
            -sDblQuoteMacro.

          - dbl_quote_macro:

            The macro to use for double-quotes when -dConvertDblQuotes is set.
            See below (Filter Documentation) for additional information

          - convert_sgl_quotes(BoolOrFieldList):

            Detect double-quoted expressions and replace them by a call to a
            LaTeX macro.  Same as -dConvertDblQuotes but for single quotes.  See
            below (Filter Documentation) for additional information; see also
            -dConvertDblQuotes and -sSglQuoteMacro.

          - sgl_quote_macro:

            The macro to use for single-quotes when -dConvertSglQuotes is set.
            See below (Filter Documentation) for additional information.

          - unprotect_full_last_names(bool):

            If this option is set, remove curly braces that surround the full
            last name of people.  (It looks like Mendeley protects composite
            last names like this, which is not always necessary.)

          - fix_pages_range(bool):

            If set to true, then then we attempt to parse fields `pages={...}`
            and use the LaTeX double-hyphen en-dash to format page ranges.
        
          - fix_pages_range_hyphen:
        
            You can set this option to override which hyphen character to use
            when `fix_pages_range` is set.

          - unprotect_zotero_title_case(bool):

            OBSOLETE option, use 'zotero_bbt_fixes' filter instead.

          - fix_swedish_a(bool):

            OBSOLETE option, please use ‘-dFixSpaceAfterEscape’ instead.
        """
        # - fix_swedish_a(bool): (OBSOLETE, use -dFixSpaceAfterEscape instead.) 
        #       transform `\\AA berg' into `\\AA{}berg' for `\\AA' and `\\o' (this
        #       problem occurs in files generated e.g. by Mendeley); revtex tends to
        #       insert a blank after the `\\AA' or `\\o' otherwise.


        super().__init__()

        self.fix_space_after_escape = butils.getbool(fix_space_after_escape)
        self.fix_swedish_a = butils.getbool(fix_swedish_a); # OBSOLETE

        if (self.fix_swedish_a):
            logger.warning(
                "Fixes Filter: option -dFixSwedishA is now obsolete, in favor of the more"
                " general and better option -dFixSpaceAfterEscape. The old option will"
                " still work for backwards compatibility, but please consider changing to"
                " the new option."
            )

        self.encode_utf8_to_latex = butils.getbool(encode_utf8_to_latex)
        self.encode_latex_to_utf8 = butils.getbool(encode_latex_to_utf8)

        if (self.encode_utf8_to_latex and self.encode_latex_to_utf8):
            raise BibFilterError(
                self.name(),
                "Conflicting options: ‘-dEncodeUtf8ToLatex’ and ‘-dEncodeLatexToUtf8’."
            )

        self.remove_type_from_phd = butils.getbool(remove_type_from_phd)

        self.remove_pages_from_book = butils.getbool(remove_pages_from_book)

        remove_full_braces = BoolOrFieldList(remove_full_braces)
        if remove_full_braces.valuetype is bool:
            self.remove_full_braces = remove_full_braces.value
            self.remove_full_braces_fieldlist = None
        else:
            self.remove_full_braces = bool(len(remove_full_braces.value))
            self.remove_full_braces_fieldlist = [ x.strip().lower() for x in remove_full_braces.value ]

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
            def mkpatternrx(x):
                x = x.strip()
                if not x:
                    return tuple()
                # x may be a name, e.g. 'Bell', but it may also be a more complex string, e.g. 'i.i.d.'.
                #
                pattern = re.escape(x)

                # We need to make sure that a match doesn't begin or end in the
                # middle of a word. (e.g., "Bell" shouldn't match in "doorbell")
                if x[0].isalpha():
                    pattern = r'\b' + pattern
                if x[-1].isalpha():
                    pattern = pattern + r'\b'

                return (x, re.compile(pattern, re.IGNORECASE),)
                    
            self.protect_names = [ t for t in [ mkpatternrx(x) for x in protect_names ]
                                   if len(t) ]
        else:
            self.protect_names = None

        self.remove_file_field = butils.getbool(remove_file_field)
        self.remove_fields = CommaStrList(remove_fields)
        self.remove_doi_prefix = butils.getbool(remove_doi_prefix)

        self.map_annote_to_note = butils.getbool(map_annote_to_note)
        
        try:
            auto_urlify_bool = butils.getbool(auto_urlify) # raises ValueError if not a boolean
            self.auto_urlify = [ "note" ] if auto_urlify_bool else []
        except ValueError:
            self.auto_urlify = CommaStrList(auto_urlify)

        # make sure key (language alias) is made lower-case
        self.rename_language = dict([ (k.lower(), v)
                                      for k, v in ColonCommaStrDict(rename_language).items() ])
        self.rename_language_rx = None
        if self.rename_language:
            # e.g. with rename_language={'en':'english','de':'deutsch',
            # 'german':'deutsch', 'french':'francais'}, prepare the regexp
            # '^en|de|german|french$'. Case INsensitive.
            self.rename_language_rx = re.compile(
                r'^\s*(?P<lang>' +
                "|".join([re.escape(k.strip()) for k in self.rename_language]) +
                r'\s*)$',
                flags=re.IGNORECASE
                )

        fix_mendeley_bug_urls = BoolOrFieldList(fix_mendeley_bug_urls)
        if fix_mendeley_bug_urls.valuetype is bool:
            self.fix_mendeley_bug_urls = ['url'] if fix_mendeley_bug_urls.value else []
        else:
            self.fix_mendeley_bug_urls = fix_mendeley_bug_urls.value

        protect_capital_letter_after_dot = BoolOrFieldList(protect_capital_letter_after_dot)
        if protect_capital_letter_after_dot.valuetype is bool:
            self.protect_capital_letter_after_dot =  \
                ['title'] if protect_capital_letter_after_dot.value else []
        else:
            self.protect_capital_letter_after_dot = protect_capital_letter_after_dot.value

        protect_capital_letter_at_begin = BoolOrFieldList(protect_capital_letter_at_begin)
        if protect_capital_letter_at_begin.valuetype is bool:
            self.protect_capital_letter_at_begin =  \
                ['title'] if protect_capital_letter_at_begin.value else []
        else:
            self.protect_capital_letter_at_begin = protect_capital_letter_at_begin.value

        self.dbl_quote_macro = dbl_quote_macro
        self.sgl_quote_macro = sgl_quote_macro

        convert_dbl_quotes = BoolOrFieldList(convert_dbl_quotes)
        if convert_dbl_quotes.valuetype is CommaStrList:
            self.convert_dbl_quotes = convert_dbl_quotes.value
        else:
            # just passed a bool, e.g. 'True'
            self.convert_dbl_quotes =  \
                ['title','abstract','booktitle','series'] if convert_dbl_quotes.value else []
            
        convert_sgl_quotes = BoolOrFieldList(convert_sgl_quotes)
        if convert_sgl_quotes.valuetype is CommaStrList:
            self.convert_sgl_quotes = convert_sgl_quotes.value
        else:
            # just passed a bool, e.g. 'True'
            self.convert_sgl_quotes =  \
                ['title','abstract','booktitle','series'] if convert_sgl_quotes.value else []
        
        self.fix_pages_range = butils.getbool(fix_pages_range)
        self.fix_pages_range_hyphen = fix_pages_range_hyphen

        self.unprotect_full_last_names = butils.getbool(unprotect_full_last_names)
        self.unprotect_zotero_title_case = butils.getbool(unprotect_zotero_title_case)

        if self.unprotect_zotero_title_case:
            logger.warning(
                "You shouldn't use fixes' -dUnprotectZoteroTitleCase option any longer; "
                "use instead the corresponding option in the zotero_bbt_fixes filter."
            )

        logger.debug(('fixes filter: '
                      'fix_space_after_escape=%r; encode_utf8_to_latex=%r; encode_latex_to_utf8=%r; '
                      'remove_type_from_phd=%r; '
                      'remove_pages_from_book=%r; '
                      'remove_full_braces=%r [fieldlist=%r, not lang=%r], '
                      'protect_names=%r, remove_file_field=%r, '
                      'remove_fields=%r, remove_doi_prefix=%r, fix_swedish_a=%r, '
                      'map_annote_to_note=%r, auto_urlify=%r, rename_language=%r, rename_language_rx=%r, '
                      'fix_mendeley_bug_urls=%r,'
                      'protect_capital_letter_after_dot=%r,protect_capital_letter_at_begin=%r,'
                      'convert_dbl_quotes=%r,dbl_quote_macro=%r,convert_sgl_quotes=%r,sgl_quote_macro=%r,'
                      'unprotect_full_last_names=%r, '
                      'fix_pages_range=%r,fix_pages_range_hyphen=%r, '
                      'unprotect_zotero_title_case=%r')
                     % (self.fix_space_after_escape, self.encode_utf8_to_latex, self.encode_latex_to_utf8,
                        self.remove_type_from_phd, self.remove_pages_from_book,
                        self.remove_full_braces, self.remove_full_braces_fieldlist,
                        self.remove_full_braces_not_lang,
                        self.protect_names,
                        self.remove_file_field,
                        self.remove_fields, self.remove_doi_prefix, self.fix_swedish_a,
                        self.map_annote_to_note,
                        self.auto_urlify,
                        self.rename_language,
                        (self.rename_language_rx.pattern if self.rename_language_rx else None),
                        self.fix_mendeley_bug_urls,
                        self.protect_capital_letter_after_dot, self.protect_capital_letter_at_begin,
                        self.convert_dbl_quotes,self.dbl_quote_macro,
                        self.convert_sgl_quotes,self.sgl_quote_macro,
                        self.unprotect_full_last_names,
                        self.fix_pages_range, self.fix_pages_range_hyphen,
                        self.unprotect_zotero_title_case,
                        ))
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        # first apply filters that are applied to all fields of the entry

        def thefilter(x):
            if self.fix_swedish_a:
                # OBSOLETE, but still accepted for backwards compatibility
                x = re.sub(r'\\AA\s+', r'\\AA{}', x)
                x = re.sub(r'\\o\s+', r'\\o{}', x)
            if self.encode_utf8_to_latex:
                # use custom encoder
                x = custom_uni_to_latex(x)
            if self.fix_space_after_escape: # after converting to LaTeX
                x = do_fix_space_after_escape(x)
            if self.encode_latex_to_utf8:
                x = butils.latex_to_text(x)
            return x

        def filter_person(p):
            oldpstr = str(p)
            #print(oldpstr)
            newpstr = thefilter(oldpstr)
            #print(newpstr)
            return Person(string=newpstr)
            # does not work this way because of the way Person() splits at spaces:
            #parts = {}
            #for typ in ['first', 'middle', 'prelast', 'last', 'lineage']:
            #    parts[typ] = thefilter(u" ".join(p.get_part(typ)))
            #return Person(**parts)


        for (role,perslist) in entry.persons.items():
            for k in range(len(perslist)):
                entry.persons[role][k] = filter_person(perslist[k])
        
        for (k,v) in entry.fields.items():
            entry.fields[k] = thefilter(v)

        logger.longdebug("fixes filter: entry %s after first basic fixes: %r", entry.key, entry)

        # additionally:

        if self.unprotect_full_last_names:
            for (role,perslist) in entry.persons.items():
                for p in perslist:
                    if len(p.last_names) == 1:
                        lname = remove_full_braces(p.last_names[0])
                        p.last_names = split_tex_string(lname)

        # make sure we run this before protect_names
        if self.unprotect_zotero_title_case:
            # clean up Zotero-overprotected titles
            do_fields = ['title', 'booktitle', 'shorttitle']
            for fld in do_fields:
                if fld in entry.fields:
                    entry.fields[fld] = _zotero_title_protection_cleanup(entry.fields[fld])

        def filter_entry_remove_type_from_phd(entry):
            if (entry.type != 'phdthesis' or 'type' not in entry.fields):
                return
            if re.search(r'\bph\W*d\b', entry.fields['type'], flags=re.IGNORECASE):
            #if ('phd' in re.sub(r'[^a-z]', '', entry.fields['type'].lower())):
                # entry is phd type, so remove explicit type={}
                del entry.fields['type']
            
        if (self.remove_type_from_phd):
            filter_entry_remove_type_from_phd(entry)

        if (self.remove_pages_from_book):
            if (entry.type == 'book' and 'pages' in entry.fields):
                del entry.fields['pages']


        #
        # do this before 'self.remove_full_braces', because the latter depends on language
        #
        if (self.rename_language):
            if 'language' in entry.fields:
                logger.longdebug('Maybe fixing language in entry %s: lang=%r',
                                 entry.key, entry.fields['language'])
                entry.fields['language'] = self.rename_language_rx.sub(
                    lambda m: self.rename_language.get(m.group('lang').lower(), m.group('lang')),
                    entry.fields['language']
                )
                logger.longdebug('  --> language is now = %r', entry.fields['language'])



        def filter_entry_remove_full_braces(entry, fieldlist):
            for k,v in entry.fields.items():
                if fieldlist is None or k in fieldlist:
                    entry.fields[k] = remove_full_braces(v)

        if self.remove_full_braces:
            if entry.fields.get('language','').lower() not in self.remove_full_braces_not_lang:
                filter_entry_remove_full_braces(entry, self.remove_full_braces_fieldlist)


        if self.map_annote_to_note:
            if 'annote' in entry.fields:
                thenote = ''
                if len(entry.fields.get('note', '')):
                    thenote = entry.fields['note'] + '; '
                entry.fields['note'] = thenote + entry.fields['annote']
                del entry.fields['annote']
                
        if self.auto_urlify:
            for fld in self.auto_urlify:
                if fld in entry.fields:
                    entry.fields[fld] = do_auto_urlify(entry.fields[fld])

        def filter_protect_names(entry):
            def repl_ltx_str(n, r, x):
                # scan string until next '{', read latex expression and skip it, etc.
                lw = latexwalker.LatexWalker(x, tolerant_parsing=True)
                pos = 0
                newx = u''
                therx = re.compile(r'((?P<openbrace>\{)|'+r.pattern+r')', re.IGNORECASE)
                while True:
                    m = therx.search(x, pos)
                    if m is None:
                        newx += x[pos:]
                        break
                    newpos = m.start()
                    newx += x[pos:newpos]
                    if m.group('openbrace'):
                        # we encountered an opening brace, so we need to copy in everything verbatim
                        (junknode, np, nl) = lw.get_latex_expression(newpos)
                        # just copy the contents as is and move on
                        newx += x[newpos:np+nl]
                        newpos = np + nl
                    else:
                        # we found an instance of the string we wanted to protect, so protect it:
                        newx += '{' + n + '}'
                        newpos = m.end()

                    # continue from our last position
                    pos = newpos
                    
                return newx

            for key, val in entry.fields.items():
                if key in ('doi', 'url', 'file'):
                    continue
                newval = val
                for n,r in self.protect_names:
                    newval = repl_ltx_str(n, r, newval)
                if (newval != val):
                    entry.fields[key] = newval

        if self.protect_names:
            filter_protect_names(entry)

        # include stuff like:
        #
        # title = "{\textquotedblleft}Relative State{\textquotedblright} Formulation of Quantum Mechanics"
        #
        _rx_prcap_lead = r'([^\w\{]|\\[A-Za-z]+|\{\\[A-Za-z]+\})*'
        if self.protect_capital_letter_after_dot:
            for fld in self.protect_capital_letter_after_dot:
                if fld in entry.fields:
                    entry.fields[fld] = re.sub(r'(?P<dotlead>[.:]'+_rx_prcap_lead+r')(?P<ucletter>[A-Z])',
                                               lambda m: m.group('dotlead')+u'{'+m.group('ucletter')+u'}',
                                               entry.fields[fld])
        if self.protect_capital_letter_at_begin:
            for fld in self.protect_capital_letter_at_begin:
                if fld in entry.fields:
                    entry.fields[fld] = re.sub(r'^(?P<lead>'+_rx_prcap_lead+r')(?P<ucletter>[A-Z])',
                                               lambda m: m.group('lead')+u'{'+m.group('ucletter')+u'}',
                                               entry.fields[fld])

        if self.fix_mendeley_bug_urls:
            for fld in self.fix_mendeley_bug_urls:
                if fld in entry.fields:
                    entry.fields[fld] = do_fix_mendeley_bug_urls(entry.fields[fld])

        _rx_dbl_quotes = [
            re.compile(r"``(?P<contents>.*?)''"),
            # this pattern must be tested first, because otherwise we leave stray braces
            re.compile(r'\{\\(textquotedblleft|ldq)\}(?P<contents>.*?)\{\\(textquotedblright|rdq)\}'),
            re.compile(r'\\(textquotedblleft|ldq)(?P<contents>.*?)\\(textquotedblright|rdq)'),
            # unicode quotes
            re.compile('\N{LEFT DOUBLE QUOTATION MARK}'+r"(?P<contents>.*?)"+
                       '\N{RIGHT DOUBLE QUOTATION MARK}'),
        ]
        _rx_sgl_quotes = [
            # try to match correct quote in " `My dad's dog' is a nice book ".
            re.compile(r"`(?P<contents>.*?)'(?=\W|$)"),
            # this pattern must be tested first, because otherwise we leave stray braces
            re.compile(r'\{\\(textquoteleft|lq)\}(?P<contents>.*?)\{\\(textquoteright|rq)\}'),
            re.compile(r'\\(textquoteleft|lq)(?P<contents>.*?)\\(textquoteright|rq)'),
            # unicode quotes
            re.compile('\N{LEFT SINGLE QUOTATION MARK}'+r"(?P<contents>.*?)"+
                       '\N{RIGHT SINGLE QUOTATION MARK}'),
        ]
        if self.convert_dbl_quotes:
            for fld in self.convert_dbl_quotes:
                if fld in entry.fields:
                    for rx in _rx_dbl_quotes:
                        entry.fields[fld] = re.sub(
                            rx,
                            lambda m: self.dbl_quote_macro+u"{"+m.group('contents')+u"}",
                            entry.fields[fld]
                        )
        if self.convert_sgl_quotes:
            for fld in self.convert_sgl_quotes:
                if fld in entry.fields:
                    for rx in _rx_sgl_quotes:
                        entry.fields[fld] = re.sub(
                            rx,
                            lambda m: self.sgl_quote_macro+u"{"+m.group('contents')+u"}",
                            entry.fields[fld]
                        )
                    
        if self.remove_file_field:
            if ('file' in entry.fields):
                del entry.fields['file']

        if self.remove_fields:
            for fld in self.remove_fields:
                entry.fields.pop(fld,None)

        if self.remove_doi_prefix:
            if 'doi' in entry.fields:
                entry.fields['doi'] =  \
                    re.sub(r'^\s*doi[ :]\s*', '', entry.fields['doi'], flags=re.IGNORECASE)

        if self.fix_pages_range:
            if 'pages' in entry.fields:
                m = _rx_pages_ranges.match(entry.fields['pages'])
                if m is not None:
                    entry.fields['pages'] = \
                        m.group('a') + self.fix_pages_range_hyphen + m.group('b')

        logger.longdebug("fixes filter, result: %s -> Authors=%r, fields=%r",
                         entry.key, entry.persons.get('author', None),
                         entry.fields)

        return
    


# used to store variables in a way we can access from inner functions
class _Namespace:
    pass


def remove_full_braces(val):
    val = val.strip()
    if len(val) and val[0] == '{' and val[-1] == '}':
        # remove the extra braces. But first, check that the braces
        # enclose the full field, and we don't have e.g. "{Maxwell}'s
        # demon versus {Szilard}", in which case a dumb algorithm would
        # leave the invalid LaTeX string "Maxwell}'s demon versus
        # {Szilard"
        try:
            (nodes,pos,length) =  \
                latexwalker.LatexWalker(val, tolerant_parsing=True).get_latex_braced_group(0)
            if pos + length == len(val):
                # yes, all fine: the braces are one block for the field
                return val[1:-1]
        except latexwalker.LatexWalkerError:
            logger.longdebug(
                "LatexWalkerError while attempting to remove curly braces around valud in %s",
                val
            )
    return val


# custom utf8_to_latex


# # override default rules to keep some characters unescaped
# _rx_macro = re.compile(r'\\(?P<macroname>([a-zA-Z]+)|.)')
# def _keep_latex_macros(s, pos):
#     m =  _rx_macro.match(s, pos)
#     if m is None:
#         return None
#     # latex macro -- leave it as it is.  Recall we need to return a tuple
#     # `(consumed-length, replacement-text)`
#     return (m.end()-m.start(), m.group())
# def _apply_protection(repl):
#     # apply brackets aggressively, for some bibtex styles.  E.g. revtex style
#     # does not abbreviate names correctly if they start with an accented char
#     # that is not fully protected by braces like "\v{C}adz Zykzyz"
#     if '\\' not in repl and '{' not in repl:
#         # no macros/groups, keep like this
#         return repl
#     return '{' + repl + '}'
#     # k = repl.rfind('\\')
#     # if k >= 0 and repl[k+1:].isalpha():
#     #     # has dangling named macro, apply protection.
#     #     return '{' + repl + '}'
#     # return repl
# _our_uni2latex_map = {
#     k: _apply_protection(v)
#     for k,v in latexencode.get_builtin_uni2latex_dict().items()
#     if chr(k) not in r""" $ " \ _ { } ~ < > """
# }
# _our_unicode_to_latex = latexencode.UnicodeToLatexEncoder(
#     conversion_rules=[
#         latexencode.UnicodeToLatexConversionRule(
#             latexencode.RULE_CALLABLE,
#             _keep_latex_macros
#         ),
#         latexencode.UnicodeToLatexConversionRule(
#             latexencode.RULE_DICT,
#             _our_uni2latex_map
#         ),
#     ],
#     # protection is done manually:
#     replacement_latex_protection='none'
# )

def _apply_protection(repl):
    # apply brackets aggressively, for some bibtex styles.  E.g. revtex style
    # does not abbreviate names correctly if they start with an accented char
    # that is not fully protected by braces like "\v{C}adz Zykzyz"
    if '\\' not in repl and '{' not in repl:
        # no macros/groups, keep like this
        return repl
    return '{' + repl + '}'
_our_unicode_to_latex = latexencode.PartialLatexToLatexEncoder(
    keep_latex_chars=r'\${}^_"~<>',
    # protection is done manually:
    replacement_latex_protection=_apply_protection,
)

def custom_uni_to_latex(s):
    # recompose combining unicode characters whenever possible so that
    # unicode_to_latex can translate them correctly
    s = unicodedata.normalize('NFC', s)

    return _our_unicode_to_latex.unicode_to_latex(s)



# helper function
def _zotero_title_protection_cleanup(title):

    from .zotero_bbt_fixes import zotero_title_protection_cleanup

    return zotero_title_protection_cleanup(title)




# helper function
def do_fix_space_after_escape(x):

    logger.longdebug("fixes filter: do_fix_space_after_escape('%s')", x)

    def deal_with_escape(x, m): # helper

        #logger.longdebug("deal_with_escape: x=%r, m=%r", x, m)

        # make sure we create a new lw instance each time, because the string
        # changes between calls to deal_with_escape()!
        lw = latexwalker.LatexWalker(x, tolerant_parsing=True)

        # read and parse macro invocation, including all known macro arguments
        (nodelist, pos, len_) = lw.get_latex_nodes(pos=m.start(), read_max_nodes=1)

        # now that we got all the args as a string, replace that in the string
        assert nodelist[0].isNodeType(latexwalker.LatexMacroNode)
        macronode = nodelist[0]
        replacexstr = '\\'+macronode.macroname
        if len(macronode.nodeargd.argnlist) == 0:
            replacexstr += '{}'
        elif len(macronode.nodeargd.argspec):
            # there is an argspec, looks like a standard macro args structure
            #
            # re-convert args to strings, making sure we have braces around each
            # mandatory argument
            for n in macronode.nodeargd.argnlist:
                if n is not None:
                    if n.isNodeType(latexwalker.LatexCharsNode) and n.chars != '*':
                        # mandatory argument not enclosed in braces, force braces
                        replacexstr += '{' + n.latex_verbatim() + '}'
                    else:
                        replacexstr += n.latex_verbatim()
        else:
            # unknown situation. keep macro as it is... might be a custom args
            # parser at work
            replacexstr += macronode.latex_verbatim() # macro + arguments as they were

        finalx = x[:pos] + replacexstr + x[pos+len_:]
        logger.longdebug("fix_space_after_escape: Replaced ‘%s’ by ‘%s’, remaining=‘%s’",
                         x[pos:pos+len_], replacexstr, x[pos+len_:])
        return (finalx, pos + len(replacexstr))

    #
    # do_fix_space_after_escape function body:
    #

    # iterate all matches & replace them appropriately
    # we are looking for a named macro (not \' or \&, but e.g. \c), followed by some space.
    rxesc = re.compile(r'\\(?P<macroname>[A-Za-z]+)\s+')
    m = rxesc.search(x)
    newx = x
    while m:
        (newx, newpos) = deal_with_escape(newx, m)
        logger.longdebug("\t\tMatched `%s', newx=`%s'", m.group(), newx)
        m = rxesc.search(newx, newpos)

    logger.longdebug("\t\t--> `%s'", newx)

    return newx



# see http://stackoverflow.com/a/1547940
_rx_url = re.compile(
    r"(https?|ftp)://[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+(/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=-]*)?"
)
_rx_urlcmd = re.compile(r"((\\url\s*\{|\\href\s*\{)\s*)")

def do_auto_urlify(x):
    pos = 0
    while True:
        m = _rx_url.search(x, pos=pos)
        if m is None:
            return x
        # found a candidate URL. Now check it is not preceeded by e.g. "\url{"
        mpreclast = None
        for mprec in _rx_urlcmd.finditer(x[0:m.start()]):
            mpreclast = mprec
        if mpreclast is not None and mpreclast.end() == m.start():
            pos = m.start()
            continue
        # safe to wrap this URL into \url{...}
        x = x[:m.start()] + u"\\url{" + m.group() + u"}" + x[m.end():]
        pos = m.end()

    # The value x is returned within the block above. Code here is unreachable.


_mendeley_bug_urls_escapes = {
    r'$\sim$': '~',
}

_rx_mendeley_bug_urls_escapes = re.compile(
    r'(?P<esc>' + r'|'.join(
        (re.escape(k) for k in _mendeley_bug_urls_escapes.keys())
    ) + r')'
)

def do_fix_mendeley_bug_urls(x):
    return _rx_mendeley_bug_urls_escapes.sub(
        lambda m: _mendeley_bug_urls_escapes.get(m.group('esc'),m.group('esc')),
        x)



def bibolamazi_filter_class():
    return FixesFilter


