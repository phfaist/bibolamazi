# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2015 by Philippe Faist                                       #
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


"""
Initialization module

This module is imported before any other bibolamazi module, just to make sure we have
all the proper dependent modules set up, or to include our pre-packaged versions if need
be.

In fact, all bibolamazi modules import this module, so you don't even have to worry
about importing it first.
"""


import sys
import re


if sys.version_info < (3, 4):
    raise RuntimeError("FATAL ERROR: Bibolamazi requires Python >= 3.4")


#
# add the LONGDEBUG level, and set our custom logger class
#
from .core import blogger as _blogger # lgtm



#
# Patch for pybtex. Bug in pybtex/bibtex/utils.py in split_tex_string
# (https://sourceforge.net/p/pybtex/bugs/65/)
#
import pybtex.bibtex.utils as _pybtex_bibtex_utils
def _split_tex_string(string, sep=None, strip=True, filter_empty=False):
    if sep is None:
        sep = r'(?:\s|(?<!\\)~)+' ### PhF: FIX TO NOT MATCH e.g. Brand\~{a}o
        filter_empty = True
    sep_re = re.compile(sep)
    brace_level = 0
    name_start = 0
    result = []
    string_len = len(string)
    #pos = 0
    for pos, char in enumerate(string):
        if char == '{':
            brace_level += 1
        elif char == '}':
            brace_level -= 1
        elif brace_level == 0 and pos > 0:
            ### PhF: FIX TO NOT TRUNCATE THE STRING, TO ENABLE THE LOOKBEHIND ASSERTION IN REGEX.
            match = sep_re.match(string, pos=pos)
            if match:
                sep_len = len(match.group())
                if pos + sep_len < string_len:
                    result.append(string[name_start:pos])
                    name_start = pos + sep_len
    if name_start < string_len:
        result.append(string[name_start:])
    if strip:
        result = [part.strip() for part in result]
    if filter_empty:
        result = [part for part in result if part]
    return result
#
_pybtex_bibtex_utils.split_tex_string = _split_tex_string



#
# Patch for pybtex. Bug in pybtex.database.output.bibtex: will insist on
# escaping everything into latex, even latex commands themselves....
# so disable that.
#
import pybtex.database.output.bibtex as _pybtex_database_output_bibtex
_pybtex_database_output_bibtex.Writer._encode = lambda self, text: text # do nothing please!!





#
# Patch for pybtex. Add __delitem__ to a OrderedCaseInsensitiveDict so that we
# can erase fields in entry.fields
#
import pybtex.utils as _pybtex_utils
def _OrderedCaseInsensitiveDict_delitem(self, key):
    # find item
    key_match = [k for k in self.order if k.lower() == key.lower()]
    if len(key_match) == 0:
        raise KeyError(key)
    assert (len(key_match) == 1), "Multiple instances of same key in dictionary: %s"%(key)
    # now we have the key with the right case
    key_ok = key_match[0]
    self.order.remove(key_ok)
    super(_pybtex_utils.OrderedCaseInsensitiveDict, self).__delitem__(key_ok)
    
_pybtex_utils.OrderedCaseInsensitiveDict.__delitem__ = _OrderedCaseInsensitiveDict_delitem





#
# Patch for arxiv2bib (see https://github.com/nathangrigg/arxiv2bib/issues/8).
# Recognize some really old arXiv IDs like 'atom-ph/XXXXXXX' instead of
# 'physics/XXXXXXX' etc.
#
import arxiv2bib as _arxiv2bib
_arxiv2bib.OLD_STYLE = re.compile(r"""^[a-zA-Z.-]+/\d{7}(v\d+)?$""")
