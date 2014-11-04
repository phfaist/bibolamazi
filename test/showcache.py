#!/usr/bin/env python

import sys
import os.path
import argparse
import pickle
import textwrap
import pydoc
import StringIO

sys.path += [os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))]

import bibolamazi_init

from core.bibusercache import BibUserCacheDic, BibUserCacheList


parser = argparse.ArgumentParser('showcache')


parser.add_argument('cachefile')


args = parser.parse_args()

cache = None
with open(args.cachefile, 'rb') as f:
    cache = pickle.load(f)


def dump_bibcacheobj(cacheobj, name=None, f=sys.stdout, indent=0, **kwargs):
    indent_step = kwargs.get('indent_step', 4)
    kwargs['f'] = f
    if isinstance(cacheobj, BibUserCacheDic):
        ncount = 0
        for (key, val) in cacheobj.dic.iteritems():
            f.write("\n" + " "*indent + key + ": ")
            dump_bibcacheobj(val, name=key, indent=indent+indent_step, **kwargs)
            if key in cacheobj.tokens:
                f.write("\n" + " "*(indent+indent_step) + "{token: "+repr(cacheobj.tokens[key])+"}")
            ncount += 1
        if ncount > 10 and name:
            f.write("\n" + " "*indent + "[end of `%s' items]"%(name))
        return
    if isinstance(cacheobj, BibUserCacheList):
        for val in cacheobj.lst:
            f.write("\n" + " "*indent + "* ")
            dump_bibcacheobj(val, name='<item>', indent=indent+indent_step, **kwargs)
        return
    # display as string:
    s = str(cacheobj)
    if len(s) < 50:
        f.write(s)
        return

    #wrapper = textwrap.TextWrapper(width=90-indent, initial_indent=" "*indent, subsequent_indent=" "*indent)
    #f.write("\n" + wrapper.fill(s))

    f.write("\n" + " "*indent + s.replace('\n', "\n"+" "*indent))
    return


f = StringIO.StringIO()

f.write("\n")
f.write("Cache Dump\n")
f.write("=" * 90 + "\n")
f.write("Cache dump version: %s\n"%(cache['cachepickleversion']))
f.write("-" * 90 + "\n")

dump_bibcacheobj(cache['cachedic'], f=f)

f.write("\n" + "=" * 90 + "\n\n\n")

pydoc.pager(f.getvalue())

sys.exit(0)
