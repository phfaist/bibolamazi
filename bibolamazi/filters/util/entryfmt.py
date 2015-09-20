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

import re
import string

import bibolamazi.core.bibolamazifile
from pybtex.database import BibliographyData, Entry, Person

from bibolamazi.filters.util.arxivutil import ArxivInfoCacheAccessor


braces = [ ('{', '}'),
           ('(', ')'),
           ('[', ']'),
           ]

open_braces  = [ b[0] for b in braces ]
close_braces = [ b[1] for b in braces ]


def _read_braced_expr(s, brace_type=None):
    """
    Parses a braced expression from s and returns it as a string.
    """

    if brace_type is not None and brace_type != s[0]:
        raise ValueError("Expected opening brace: '%s' in '%s'"%(brace_type, s))
    try:
        brace_idx = open_braces.index(s[0])
    except ValueError:
        raise ValueError("Expected opening brace: '%s'"%(s))

    s_orig = s
    
    expr = s[0]
    s = s[1:]
    while s:
        c = s[0]
        if c in open_braces:
            braced_expr = _read_braced_expr(s)
            expr += braced_expr
            s = s[len(braced_expr):]
            continue
        if c in close_braces:
            if c != close_braces[brace_idx]:
                raise ValueError("Opening brace '%s' closed with '%s' in '%s'"%(open_braces[brace_idx], c, s_orig))
            expr += c
            return expr
        expr += s[0]
        s = s[1:]

    raise ValueError("End of string while searching for closing brace '%s' in '%s'"%(close_braces[brace_idx], s_orig))


class FmtIfExpr(object):
    def __init__(self, entryfmt):
        self.entryfmt = entryfmt

    def __format__(self, fmtexpr):
        ifexpr = _read_braced_expr(fmtexpr, brace_type='(')[1:-1]
        lenifexpr = len(ifexpr)+2
        val = _read_braced_expr(fmtexpr[lenifexpr:], brace_type='(')[1:-1]
        lenval = len(val)+2
        rest = fmtexpr[(lenifexpr+lenval):]
        if rest:
            # still has an expression, for 'else' clause
            valelse = _read_braced_expr(rest, brace_type='(')[1:-1]
        else:
            valelse = ''

        ifexpr_fmt = self.entryfmt.get_field(ifexpr)[0]
        if ifexpr_fmt:
            return self.entryfmt.format(val)
        else:
            return self.entryfmt.format(valelse)


class _Store:
    def __init__(self, d):
        for (k,v) in d.iteritems():
            setattr(self, k, v)

class EntryFormatter(string.Formatter):
    def __init__(self, bibolamazifile, entry, kwargs={}, arxivinfo=None):
        self.bibolamazifile = bibolamazifile
        self.entry = entry

        self.d = {}
        self.d.update(kwargs)

        # some extensions.
        if arxivinfo:
            a = arxivinfo
        else:
            a_access = self.bibolamazi.cacheAccessor(ArxivInfoCacheAccessor)
            if a_access is not None:
                a = a_access.getArXivInfo(entry.key)
            else:
                a = None
        if (a is not None):
            # we have arXiv info.
            self.d['arxiv'] = _Store(a)
        
        self.d.update({
            'p': _Store({
                'firstauthor': self.entry.persons['author'][0] if len(self.entry.persons['author']) else '',
                'authors': self.entry.persons.get('author',{}),
                'editors': self.entry.persons.get('editor',{}),
                'persons': self.entry.persons,
                }),
            'f': self.entry.fields,
            'if': FmtIfExpr(self)
        })


    def format(self, fmt):
        return self.vformat(fmt, [], self.d)

    def get_field(self, fldname, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = self.d

        return super(EntryFormatter, self).get_field(fldname, args, kwargs)

    def get_value(self, key, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = self.d

        return super(EntryFormatter, self).get_value(key, args, kwargs)
