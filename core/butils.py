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
import types

from blogger import logger
import version


def get_version():
    return version.version_str;

_theversionsplit = None

def get_version_split():
    if (_theversionsplit is None):
        m = re.match(r'^(\d+)(?:\.(\d+)(?:\.(\d+)(.+)?)?)?', version.version_str);
        _theversionsplit = (m.group(1), m.group(2), m.group(3), m.group(4));
    return _theversionsplit;




class BibolamaziError(Exception):
    def __init__(self, msg, where=None):
        self.where = where;
        fullmsg = msg
        if (where is not None):
            fullmsg += "\n\t@: "+where;

        Exception.__init__(self, fullmsg);



def getbool(x):
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



def resolve_type(typename):
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




