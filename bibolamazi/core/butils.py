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

"""
Various utilities for use within all of the Bibolamazi Project.
"""


import re
import types
import math
import datetime
import logging

import bibolamazi.init
from . import version

logger = logging.getLogger(__name__)



def get_version():
    """
    Return the version string :py:data:`~core.version.version_str`, unchanged.
    """
    return version.version_str;

_theversionsplit = None

def get_version_split():
    """
    Return a 4-tuple `(maj, min, rel, suffix)` resulting from parsing the version obtained
    via :py:data:`version.version_str`.

    ............ TODO: FIXME: CURRENTLY, the elements are strings! why not integers? If
    not there, they will/should be empty or None?

    """
    if (_theversionsplit is None):
        m = re.match(r'^(\d+)(?:\.(\d+)(?:\.(\d+)(.+)?)?)?', version.version_str);
        _theversionsplit = (m.group(1), m.group(2), m.group(3), m.group(4));
    return _theversionsplit;


def get_copyrightyear():
    """
    Return the copyright year :py:data:`~core.version.copyright_year`, unchanged.
    """
    return version.copyright_year;





class BibolamaziError(Exception):
    """
    Root bibolamazi error exception.

    See also :py:class:`~core.bibfilter.BibFilterError` and
    :py:class:`~core.bibusercache.BibUserCacheError`.
    """
    def __init__(self, msg, where=None):
        self.where = where;
        fullmsg = msg
        if (where is not None):
            fullmsg += "\n\t@: "+where;

        super(BibolamaziError, self).__init__(fullmsg);



def getbool(x):
    """
    Utility to parse a string representing a boolean value.

    If `x` is already of integer or boolean type (actually, anything castable to an
    integer), then the corresponding boolean convertion is returned. If it is a
    string-like type, then it is matched against something that looks like 't(rue)?', '1',
    'y(es)?' or 'on' (ignoring case), or against something that looks like 'f(alse)?',
    '0', 'n(o)?' or 'off' (also ignoring case). Leading or trailing whitespace is ignored. 
    If the string cannot be parsed, a :py:exc:`ValueError` is raised.
    """
    try:
        return (int(x) != 0)
    except (TypeError, ValueError):
        pass
    if (isinstance(x, basestring)):
        m = re.match(r'^\s*(t(?:rue)?|1|y(?:es)?|on)\s*$', x, re.IGNORECASE);
        if m:
            return True
        m = re.match(r'^\s*(f(?:alse)?|0|n(?:o)?|off)\s*$', x, re.IGNORECASE);
        if m:
            return False
    raise ValueError("Can't parse boolean value: %r" % x);



def resolve_type(typename, in_module=None):
    """
    Returns a type object corresponding to the given type name `typename`, given as a
    string.

    ..... TODO: MORE DOC .........
    """

    if (in_module is not None):
        logger.longdebug("Resolving type %s in module %s", typename, in_module)
        if (typename in in_module.__dict__):
            return in_module.__dict__.get(typename)

    logger.longdebug("Resolving type %s (no module)", typename)

    if (typename == 'str'):
        return types.StringType
    if (typename == 'bool'):
        return types.BooleanType

    typestypename = (typename.title()+'Type') # e.g. "int" -> "IntType"
    return types.__dict__.get(typestypename, None)


def quotearg(x):
    if (re.match(r'^[-\w./:~%#]+$', x)):
        # only very sympathetic chars
        return x
    return '"' + re.sub(r'("|\\)', lambda m: '\\'+m.group(), x) + '"';





def guess_encoding_decode(dat, encoding=None):
    if encoding:
        return dat.decode(encoding);

    try:
        return dat.decode('utf-8');
    except UnicodeDecodeError:
        pass

    # this should always succeed
    return dat.decode('latin1');






def call_with_args(fn, *args, **kwargs):
    """
    Utility to call a function `fn` with `*args` and `**kwargs`.

    `fn(*args)` must be an acceptable function call; beyond that, additional keyword
    arguments which the function accepts will be provided from `**kwargs`.

    This function is meant to be essentially `fn(*args, **kwargs)`, but without raising an
    error if there are arguments in `kwargs` which the function doesn't accept (in which
    case, those arguments are ignored).
    """

    args2 = args
    kwargs2 = kwargs
    if hasattr(fn, '__call__'):
        args2 = [fn] + args
        fn = fn.__call__

    (fargs, varargs, keywords, defaults) = inspect.getargspec(fn)

    if keywords:
        return fn(*args2, **kwargs2)
    
    kwargs2 = dict([(k,v) for (k,v) in kwargs2 if k in fargs])
    return fn(*args2, **kwargs2)




_rx_timedelta_part = re.compile(r'(?P<value>\d+(?:\.\d*)?|\d*\.\d+)(?P<unit>\w+)', flags=re.IGNORECASE)
    
def parse_timedelta(in_s):
    """
    Note: only positive timedelta accepted.
    """

    # all-lowercase, please
    keys = {"weeks": (7, 'days'),
            "days": (24, 'hours'),
            "hours": (60, 'minutes'),
            "minutes": (60, 'seconds'),
            "seconds": (1000, 'milliseconds'),
            }

    kwargs = {}
    for k in keys.keys():
        kwargs[k] = 0.0
        kwargs[keys[k][1]] = 0.0

    for m in _rx_timedelta_part.finditer(in_s):
        unit = m.group('unit').lower()
        keyoks = [x for x in keys if x.startswith(unit)]
        if len(keyoks) < 1:
            raise ValueError("Unknown unit for timedelta: %s" %(unit))
        if len(keyoks) > 1:
            raise ValueError("Ambiguous unit for timedelta: %s" %(unit)) # should never happen
        
        key = keyoks[0]
        value = float(m.group('value'))
        value_int = math.floor(value)
        kwargs[key] += value_int

        x = value - value_int

        while True:
            x *= keys[key][0]
            newkey = keys[key][1]
            v = math.floor(x)
            kwargs[newkey] += v
            x = (x - v)

            key = newkey
            if key not in keys:
                break
            
    #print 'kwargs: %r'%(kwargs)
    return datetime.timedelta(**kwargs)



def warn_deprecated(classname, oldname, newname, modulename=None, explanation=None):
    import traceback

    if modulename is not None:
        warnlogger = logging.getLogger(modulename)
    else:
        warnlogger = logger

    warnlogger.warning(
        ("%(modulenamecolon)s%(classnamedot)s%(oldname)s is deprecated. Please use "
         "%(modulenamecolon)s%(classnamedot)s%(newname)s instead. %(explanationspace)s"
         "at:\n"
         "%(stack)s")
        % { 'classnamedot': (classname+'.' if classname else ''),
            'modulenamecolon': (modulename+':' if modulename else ''),
            'oldname': oldname,
            'newname': newname,
            'explanationspace': (explanation+' ' if explanation else ''),
            'stack': traceback.format_stack(limit=3)[0],
            }
        )
