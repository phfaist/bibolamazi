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

from pybtex.database import Person

from pylatexenc import latexencode
from pylatexenc import latexwalker
from pylatexenc import latex2text

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList, ColonCommaStrDict
from bibolamazi.core import butils


HELP_AUTHOR = u"""\
Fixes filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Fixes filter: perform some various known fixes for bibtex entries
"""

HELP_TEXT = u"""
Perform some various fixes for bibtex entries.

For now, the implemented fixes are:

  -dFixSpaceAfterEscape
    Removes any space after a LaTeX escape and replaces it by a pair of braces. 
    Indeed, some bibtex styles wrongfully split a word into two halves in such
    cases. For example, \"\\AA berg\" is replaced by \"\\AA{}berg\".

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
    preserve the capitalization of nouns in German titles. (Comparision is done
    case insensitive.)

  -sProtectNames=Name1,Name2...
    A list of names that should be protected within most fields. Whenever a
    field contains one of the given names (as full word), then the name is
    wrapped in braces (e.g. \"On Bell Experiments\" -> \"On {Bell}
    Experiments\") in order to protect the possible upper casing. This applies
    to all fields except 'url', 'file', and people (authors and editors).

  -dRemoveFileField
    Removes the field file={...} (that e.g. Mendeley introduces) from all
    entries. (This option is kept for compatibility, consider the newer and more
    flexible option -sRemoveFields below)

  -sRemoveFields=field1,field2...
    Removes the given fields from *all entries*. `fieldN` are BibTeX field names
    of fields to remove from all entries, e.g. `file', `issn', `note', etc.

  -dRemoveDoiPrefix
    Removes `doi:' prefix from all DOIs, if present.

  -dMapAnnoteToNote
    Changes the 'annote=' field to 'note='. If the 'note' field already has
    contents, the contents of the 'annote' field is appended to the existing
    'note' field.

  -dAutoUrlify
  -sAutoUrlify=field1,field2...
    Automatically wrap strings that look like an URL in the `note' field into
    `\\url{}' commands. If a list of fields is provided, then the
    auto-urlification is applied to those given bibtex fields.

  -sRenameLanguage=alias1:language1,alias2:language2...
    Change language={} field values according to the given rules. An alias (case
    insensitive) is replaced by its corresponding language. Replacements are not
    done recursively.

  -dFixMendeleyBugUrls
  -sFixMendeleyBugUrls=field1,field2...
    Mendeley's BibTeX output currently is buggy and escapes URLs with signs like
    $\sim$ etc. This option enables reverting Mendeley's escape sequences back
    to URL characters (for known escape Mendeley sequences).

    This option is off by default. Use the
    `-sFixMendeleyBugUrls=field1,field2...' variant to specify a list of bibtex
    fields on which to act (but not author nor editor). If the
    `-dFixMendeleyBugUrls' variant is given, the only the 'url' field is
    processed.

The following switch is OBSOLETE, but is still accepted for backwards
compatibility:

  -dFixSwedishA [use -dFixSpaceAfterEscape instead]
    Changes \"\\AA berg\" to \"\\AA{}berg\" and \"M\\o lmer\" to \"M\\o{}lmer\"
    to prevent bibtex/revtex from inserting a blank after the \"\\AA\" or
    \"\\o\". (This fix is needed for, e.g., the bibtex that Mendeley generates)


"""


class FixesFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self,
                 fix_space_after_escape=False,
                 encode_utf8_to_latex=False,
                 encode_latex_to_utf8=False,
                 remove_type_from_phd=False,
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
                 fix_swedish_a=False):
        """
        Constructor method for FixesFilter

        Filter Arguments:
          - fix_space_after_escape(bool): transform `\\AA berg' and `M\\o ller' into `\\AA{}berg',
               `M\\o{}ller' to avoid bibtex styles from wrongfully splitting these words.
          - encode_utf8_to_latex(bool): encode known non-ascii characters into latex escape sequences.
          - encode_latex_to_utf8(bool): encode known latex escape sequences to unicode text (utf-8).
          - remove_type_from_phd(bool): Removes any `type=' field from @phdthesis{..} bibtex entries.
          - remove_full_braces: removes overprotective global braces in field values.
          - remove_full_braces_not_lang(CommaStrList): (in conjunction with --remove-full-braces) removes the
            overprotective global braces only if the language of the entry (as per language={..} bibtex field)
            is not in the given list (case insensitive).
          - protect_names: list of names to protect from bibtex style casing.
          - remove_file_field(bool): removes file={...} fields from all entries.
          - remove_fields(CommaStrList): removes given fields from all entries.
          - remove_doi_prefix(bool): removes `doi:' prefix from all DOIs, if present
          - map_annote_to_note(bool): maps `annote' bibtex field to a `note' field
          - auto_urlify: automatically wrap URLs into `\\url{}' commands
          - rename_language(ColonCommaStrDict): replace e.g. `de' by `Deutsch'. Use
                format `alias1:language1,alias2:language2...'.
          - fix_mendeley_bug_urls(bool): fix the `url' field for Mendeley's
                buggy output. Pass on a list of fields (comma-separated) to specify
                which fields to act on; by default if enabled only 'url'.
          - fix_swedish_a(bool): (OBSOLETE, use -dFixSpaceAfterEscape instead.) 
                transform `\\AA berg' into `\\AA{}berg' for `\\AA' and `\\o' (this
                problem occurs in files generated e.g. by Mendeley); revtex tends to
                insert a blank after the `\\AA' or `\\o' otherwise.
        """
        
        BibFilter.__init__(self);

        self.fix_space_after_escape = butils.getbool(fix_space_after_escape);
        self.fix_swedish_a = butils.getbool(fix_swedish_a); # OBSOLETE

        if (self.fix_swedish_a):
            logger.warning("Fixes Filter: option -dFixSwedishA is now obsolete, in favor of the more"
                           " general and better option -dFixSpaceAfterEscape. The old option will"
                           " still work for backwards compatibility, but please consider changing to"
                           " the new option.")

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
            self.protect_names = dict([ (x.strip(), re.compile(r'\b'+re.escape(x.strip())+r'\b', re.IGNORECASE))
                                        for x in protect_names.split(',') ]);
        else:
            self.protect_names = None;

        self.remove_file_field = butils.getbool(remove_file_field);
        self.remove_fields = CommaStrList(remove_fields);
        self.remove_doi_prefix = butils.getbool(remove_doi_prefix)

        self.map_annote_to_note = butils.getbool(map_annote_to_note)
        
        try:
            auto_urlify_bool = butils.getbool(auto_urlify) # raises ValueError if not a boolean
            self.auto_urlify = [ "note" ] if auto_urlify_bool else []
        except ValueError:
            self.auto_urlify = CommaStrList(auto_urlify)

        # make sure key (language alias) is made lower-case
        self.rename_language = dict([ (k.lower(), v)
                                      for k, v in ColonCommaStrDict(rename_language).iteritems() ])
        self.rename_language_rx = None
        if self.rename_language:
            # e.g. with rename_language={'en':'english','de':'deutsch',
            # 'german':'deutsch', 'french':'francais'}, prepare the regexp
            # '^en|de|german|french$'. Case INsensitive.
            self.rename_language_rx = re.compile(
                r'^\s*(?P<lang>' +
                "|".join([re.escape(k.strip()) for k in self.rename_language.iterkeys()]) +
                r'\s*)$',
                flags=re.IGNORECASE
                )

        if fix_mendeley_bug_urls:
            try:
                self.fix_mendeley_bug_urls = CommaStrList(fix_mendeley_bug_urls)
            except TypeError:
                # just passed, e.g., `True`
                self.fix_mendeley_bug_urls = ['url']
        else:
            self.fix_mendeley_bug_urls = []

        logger.debug(('fixes filter: fix_space_after_escape=%r; encode_utf8_to_latex=%r; encode_latex_to_utf8=%r; '
                      'remove_type_from_phd=%r; '
                      'remove_full_braces=%r [fieldlist=%r, not lang=%r], '
                      'protect_names=%r, remove_file_field=%r, '
                      'remove_fields=%r, remove_doi_prefix=%r, fix_swedish_a=%r, '
                      'map_annote_to_note=%r, auto_urlify=%r, rename_language=%r, rename_language_rx=%r, '
                      'fix_mendeley_bug_urls=%r')
                     % (self.fix_space_after_escape, self.encode_utf8_to_latex, self.encode_latex_to_utf8,
                        self.remove_type_from_phd,
                        self.remove_full_braces, self.remove_full_braces_fieldlist,
                        self.remove_full_braces_not_lang,
                        self.protect_names,
                        self.remove_file_field,
                        self.remove_fields, self.remove_doi_prefix, self.fix_swedish_a,
                        self.map_annote_to_note,
                        self.auto_urlify,
                        self.rename_language,
                        (self.rename_language_rx.pattern if self.rename_language_rx else None),
                        self.fix_mendeley_bug_urls
                        ));
        

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY;

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        # first apply filters that are applied to all fields of the entry

        def thefilter(x):
            if (self.fix_space_after_escape):
                x = do_fix_space_after_escape(x)
            if (self.fix_swedish_a):
                # OBSOLETE, but still accepted for backwards compatibility
                x = re.sub(r'\\AA\s+', r'\AA{}', x);
                x = re.sub(r'\\o\s+', r'\o{}', x);
            if (self.encode_utf8_to_latex):
                # Need non_ascii_only=True because we might have e.g. braces or other
                # LaTeX code we want to preserve.
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
                        # remove the extra braces. But first, check that the braces
                        # enclose the full field, and we don't have e.g. "{Maxwell}'s
                        # demon versus {Szilard}", in which case a dumb algorithm would
                        # leave the invalid LaTeX string "Maxwell}'s demon versus
                        # {Szilard"
                        try:
                            (nodes,pos,length) = latexwalker.get_latex_braced_group(val, 0,
                                                                                    tolerant_parsing=True)
                            if (pos + length == len(val)):
                                # yes, all fine: the braces are one block for the field
                                entry.fields[k] = val[1:-1];
                        except LatexWalkerError:
                            logger.longdebug("LatexWalkerError while checking enclosing braces for key %s,"
                                             " for field %s = `%s' --ignoring", entry.key, k, val)

        if self.remove_full_braces:
            if entry.fields.get('language','').lower() not in self.remove_full_braces_not_lang:
                filter_entry_remove_full_braces(entry, self.remove_full_braces_fieldlist);


        def filter_protect_names(entry):
            for key, val in entry.fields.iteritems():
                if key in ('url', 'file'):
                    continue
                newval = val;
                for n,r in self.protect_names.iteritems():
                    newval = r.sub(lambda m: '{'+n+'}', newval);
                if (newval != val):
                    entry.fields[key] = newval;

        if (self.map_annote_to_note):
            if 'annote' in entry.fields:
                thenote = ''
                if len(entry.fields.get('note', '')):
                    thenote = entry.fields['note'] + '; '
                entry.fields['note'] = thenote + entry.fields['annote']
                del entry.fields['annote']
                
        if (self.auto_urlify):
            for fld in self.auto_urlify:
                if fld in entry.fields:
                    entry.fields[fld] = do_auto_urlify(entry.fields[fld])

        if (self.protect_names):
            filter_protect_names(entry);

        if (self.rename_language):
            if 'language' in entry.fields:
                logger.longdebug('Maybe fixing language in entry %s: lang=%r', entry.key, entry.fields['language'])
                entry.fields['language'] = self.rename_language_rx.sub(
                    lambda m: self.rename_language.get(m.group('lang').lower(), m.group('lang')),
                    entry.fields['language']
                )
                logger.longdebug('  --> language is now = %r', entry.fields['language'])

        if (self.fix_mendeley_bug_urls):
            for fld in self.fix_mendeley_bug_urls:
                if fld in entry.fields:
                    entry.fields[fld] = do_fix_mendeley_bug_urls(entry.fields[fld])

        if (self.remove_file_field):
            if ('file' in entry.fields):
                del entry.fields['file'];

        if (self.remove_fields):
            for fld in self.remove_fields:
                entry.fields.pop(fld,None)

        if (self.remove_doi_prefix):
            if 'doi' in entry.fields:
                entry.fields['doi'] = re.sub(r'^\s*doi:\s*', '', entry.fields['doi'], flags=re.IGNORECASE)

        logger.longdebug("fixes filter, result: %s -> Authors=%r, fields=%r",
                         entry.key, entry.persons.get('author', None),
                         entry.fields)

        return
    

# used to store variables in a way we can access from inner functions
class _Namespace:
    pass


# helper function
def do_fix_space_after_escape(x):

    logger.longdebug("fixes filter: do_fix_space_after_escape(`%s')", x)

    def deal_with_escape(x, m): # helper
        macroname = m.group('macroname')
        if macroname not in latexwalker.macro_dict:
            logger.longdebug("fixes filter: Unknown macro \\%s for -dFixSpaceAfterEscape, assuming no arguments.",
                             macroname)
            replacexstr = '\\' + macroname + "{}"
            return (x[:m.start()] + replacexstr + x[m.end():], m.start() + len(replacexstr))

        macrodef = latexwalker.macro_dict[macroname]

        ns = _Namespace()
        ns.pos = m.end()
        ns.args = ""
        # now, ns.pos and ns.args can be seen and modified from the following inner nested
        # functions. (see https://www.python.org/dev/peps/pep-3104/)

        def addoptarg():
            optarginfotuple = latexwalker.get_latex_maybe_optional_arg(x, ns.pos,
                                                                       strict_braces=False,
                                                                       tolerant_parsing=True)
            if (optarginfotuple is not None):
                # recursively fix the arguments, in case they themselves have escapes with spaces
                ns.args += do_fix_space_after_escape(ns.x[optargpos : optargpos+optarglen])
                ns.pos = optargpos+optarglen;

        def addarg():
            (nodearg, npos, nlen) = latexwalker.get_latex_expression(x, ns.pos, strict_braces=False,
                                                                     tolerant_parsing=True)
            argstr = x[npos : npos+nlen]
            if not (argstr[:1] == '{' and argstr[-1:] == '}'):
                argstr = "{" + argstr + "}"

            # recursively fix the arguments, in case they themselves have escapes with spaces
            ns.args += do_fix_space_after_escape(argstr)
            ns.pos = npos+nlen;

        if (macrodef.optarg):
            addoptarg()

        if (isinstance(macrodef.numargs, basestring)):
            # specific argument specification
            for arg in macrodef.numargs:
                if (arg == '{'):
                    addarg()
                elif (arg == '['):
                    addoptarg()
                else:
                    logger.debug("Unknown macro argument kind for macro %s: %s"
                                 % (macrodef.macname, arg));
        else:
            for n in range(macrodef.numargs):
                addarg()

        # now that we got all the args as a string, replace that in the string

        replacexstr = '\\'+macrodef.macname + ns.args
        finalx = x[:m.start()] + replacexstr + x[ns.pos:]
        logger.longdebug("fix_space_after_escape: Replaced `%s' by `%s', remaining=`%s'",
                         m.group(), replacexstr, x[ns.pos:])
        return (finalx, m.start() + len(replacexstr))

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
_rx_url = re.compile(r"(https?|ftp)://[A-Za-z0-9_]+(\.[A-Za-z0-9_]+)+(/[A-Za-z0-9._~:/?#\[\]@!$&'()*+,;=-]*)?")
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
    return x


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
    return FixesFilter;



