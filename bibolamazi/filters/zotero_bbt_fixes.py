# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2020 by Philippe Faist                                       #
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
#import unicodedata
import logging
logger = logging.getLogger(__name__)

from pybtex.database import Person
from pybtex.bibtex.utils import split_tex_string

from pylatexenc import latexencode
from pylatexenc import latexwalker
from pylatexenc import latex2text

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList, ColonCommaStrDict, multi_type_class
from bibolamazi.core import butils




HELP_AUTHOR = r"""
Philippe Faist, (C) 2020, GPL 3+
"""

HELP_DESC = r"""
Perform some rearrangements on entries exported by Zotero/BetterBibTeX
"""

HELP_TEXT = r"""
(See documentation for each option.)
"""




class ZoteroBbtFixesFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(
            self,
            unprotect_title_case=False,
            remove_arxiv_primary_class=False,
    ):
        r"""
        Arguments:

          - unprotect_title_case(bool):

            Zotero's better bibtex exports tend to be overzealous in protecting
            every word in the title that starts with an uppercase letter,
            because it assumes that the titles are stored in lower cases by
            default, with any upper cases having to remain so.  With this
            option, you can try to revert this behavior to allow bibtex styles
            to change the casing of the title (lowercase or title-case).  We try
            to be careful and keep protected those words that look like acronyms
            (anything more complicated than a word that starts with an
            uppercase).

          - remove_arxiv_primary_class(bool):

            The primaryclass field exported by Zotero/Better BibTeX is populated
            with all the category classes associated with the arXiv post,
            apparently without singling out which one is the primary one.  This
            value is not very useful in a bibliography; use the
            -dRemovePrimaryClass option to simply remove this field entirely.

        """

        super().__init__()

        self.unprotect_title_case = butils.getbool(unprotect_title_case)

        self.remove_arxiv_primary_class = butils.getbool(remove_arxiv_primary_class)

        logger.debug(
            "Constructed zotero_bbt_fixes filter. "
            "unprotect_title_case=%r, remove_arxiv_primary_class=%r",
            self.unprotect_title_case,
            self.remove_arxiv_primary_class,
        )

    def action(self):
        return BibFilter.BIB_FILTER_SINGLE_ENTRY

    def filter_bibentry(self, entry):
        #
        # entry is a pybtex.database.Entry object
        #

        if self.unprotect_title_case:
            # clean up Zotero-overprotected titles
            do_fields = ['title', 'booktitle', 'shorttitle']
            for fld in do_fields:
                if fld in entry.fields:
                    entry.fields[fld] = \
                        zotero_title_protection_cleanup(entry.fields[fld])

        if self.remove_arxiv_primary_class:
            if 'primaryclass' in entry.fields:
                del entry.fields['primaryclass']






# helper function
def zotero_title_protection_cleanup(title):

    logger.longdebug("zotero_title_protection_cleanup(%r)", title)

    def needs_protection(s):
        # what doesn't need protection is a sequence of words for which
        # only the first letter of each word might be capitalized
        # ... except if the braces are there to protect something in
        # math mode, in which case we keep the protection
        return ( not all(ws == '' or ws.islower()
                         for ws in (w.strip()[1:] for w in s.split()))
                 or (s.startswith(r'$') or s.startswith(r'\(')) )

    def iterate_over_words_in_nodelist(nodelist):
        # first, split the root-level char nodes at spaces and keep the rest.
        split_nodelist = []
        for n in nodelist:
            if n.isNodeType(latexwalker.LatexCharsNode):
                # split at whitespace
                chunks = re.compile(r'(\s+)').split(n.chars)
                plen = 0
                for chunk, sep in zip(chunks[0::2], chunks[1::2]+['']):
                    split_nodelist += [
                        (latexwalker.LatexCharsNode(parsing_state=n.parsing_state,
                                                    chars=chunk,
                                                    pos=n.pos+plen, len=len(chunk)), sep)
                    ]
                    plen += len(chunk)+len(sep)
            else:
                split_nodelist += [(n, '')]

        # now, combine them smarly into words.
        cur_nodelist = []
        need_protection_hint = False
        for n, sep in split_nodelist:
            logger.longdebug("node to consider for chunk: %r, sep=%r", n, sep)
            if sep: # has separator
                cur_nodelist += [n]
                # flush what we've accumulated so far
                yield cur_nodelist, sep, need_protection_hint
                cur_nodelist = []
                need_protection_hint = False
            else:
                # if there is anything else than a chars, macro or group node
                # (group node for e.g., {\'e}), then this chunk will require
                # protection (e.g. inline math)
                if not n.isNodeType(latexwalker.LatexCharsNode) and \
                   not n.isNodeType(latexwalker.LatexMacroNode) and \
                   not n.isNodeType(latexwalker.LatexGroupNode):
                    need_protection_hint = True
                # add this node to the current chunk
                cur_nodelist += [n]
        # flush last nodes
        yield cur_nodelist, '', need_protection_hint

    def process_protection_for_expression(nodelist, l2t):
        new_expression = ''
        for nl, sep, need_protection_hint in iterate_over_words_in_nodelist(nodelist):
            #logger.longdebug("chunk: nl=%r, sep=%r, need_protection_hint=%r, text-version=%r",
            #                 nl, sep, need_protection_hint, l2t.nodelist_to_text(nl))
            nl_to_latex = "".join(nnn.latex_verbatim() for nnn in nl)
            if need_protection_hint:
                #logger.longdebug("protecting chunk due to hint flag")
                new_expression += '{{' + nl_to_latex + '}}' + sep
            elif needs_protection(l2t.nodelist_to_text(nl)):
                #logger.longdebug("protecting chunk by inspection of text representation")
                new_expression += '{{' + nl_to_latex + '}}' + sep
            else:
                new_expression += nl_to_latex + sep
        return new_expression

    lw = latexwalker.LatexWalker(title)
    l2t = latex2text.LatexNodes2Text(math_mode='with-delimiters',
                                     latex_context=butils.latex2text_latex_context)
    newtitle = ''
    oldi = 0
    while True:
        i = title.find('{{', oldi)
        if i == -1: # not found
            break
        (n, pos, len_) = lw.get_latex_expression(i, strict_braces=False)
        assert pos == i
        newi = i + len_
        if title[newi-2:newi] != '}}':
            # expression must be closed by '}}', i.e. we used
            # get_latex_expression to get the inner {...} braced group,
            # but the outer group must be closed immediately after the
            # expression we read. Otherwise it's not Zotero-protected
            # and we skip this group.
            newtitle += title[oldi:newi]
            oldi = newi
            continue
        # we got a very-probably-Zotero-protected "{{...}}" group
        newtitle += title[oldi:i]
        #protected_expression = title[i+2:newi-2]
        # go through each top-level node in the protected content and
        # see individually if it requires protection.  Split char nodes
        # at spaces.
        assert len(n.nodelist) == 1 and n.nodelist[0].isNodeType(latexwalker.LatexGroupNode)
        nodelist = n.nodelist[0].nodelist
        new_expression = process_protection_for_expression(nodelist, l2t)
        #logger.longdebug("Zotero protect block: protected_expression=%r, new_expression=%r",
        #                 protected_expression, new_expression)
        newtitle += new_expression
        oldi = newi

    # last remaining part of the title
    newtitle += title[oldi:]
    return newtitle



def bibolamazi_filter_class():
    return ZoteroBbtFixesFilter


