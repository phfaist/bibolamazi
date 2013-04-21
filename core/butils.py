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
import argparse

# pydoc.pager(text) will open a pager for text (e.g. less), or pipe it out, and do everything as
# it should automatically.
import pydoc

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


def getbool(x):
    try:
        return (int(x) != 0)
    except TypeError, ValueError:
        pass
    if (isinstance(x, basestring)):
        m = re.match(r'^\s*(t(?:rue)?|1|y(?:es)?|on)\s*$', x, re.IGNORECASE);
        if m:
            return True
        m = re.match(r'^\s*(f(?:alse)?|0|n(?:o)?|off)\s*$', x, re.IGNORECASE);
        if m:
            return False
    raise ValueError("Can't parse boolean value: %r" % x);




def guess_encoding_decode(dat, encoding=None):
    if encoding:
        return dat.decode(encoding);

    try:
        return dat.decode('utf-8');
    except UnicodeDecodeError:
        pass

    # this should always succeed
    return dat.decode('latin1');




class store_or_count(argparse.Action):
    def __init__(self, option_strings, dest, nargs='?', **kwargs):
        # some checks
        if nargs != '?':
            raise ValueError('store_or_const: nargs must be "?"');
        
        super(store_or_count, self).__init__(option_strings, dest, nargs=nargs, const=None, **kwargs);


    def __call__(self, parser, namespace, values, option_string):
                
        try:
            val = getattr(namespace, self.dest);
        except AttributeError:
            val = 0;

        # count -vv as -v -v
        if (isinstance(values, basestring) and not option_string.startswith('--') and len(option_string) > 1):
            optstr = option_string[1:]
            while values.startswith(optstr):
                # add an additional count for each additional specification of the option.
                val += 1;
                values = values[len(optstr):] # strip that from the values
            if not values:
                values = None

        if (values is not None):
            # value provided
            val = int(values);
        else:
            val += 1;
        
        setattr(namespace, self.dest, val);



rxkeyval = re.compile(r'^([\w.-]+)=(.*)$', re.DOTALL);

class store_key_val(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_val actions must be == 1')

        super(store_key_val, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            **kwargs);


    def __call__(self, parser, namespace, values, option_string):
        # parse key-value pair in values
        if (isinstance(values, list)):
            values = values[0];
        m = rxkeyval.match(values);
        if not m:
            raise ValueError("cannot parse key=value pair: "+repr(values));

        keyvalpair = (m.group(1), m.group(2),)

        if (not self.dest):
            (key, val) = keyvalpair;
            setattr(namespace, key, val);
        else:
            try:
                d = getattr(namespace, self.dest);
            except AttributeError:
                pass
            if not d:
                d = [];
            d.append(keyvalpair);
            setattr(namespace, self.dest, d);



class store_key_const(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, const=True, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_const actions must be == 1')

        super(store_key_const, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            **kwargs);


    def __call__(self, parser, namespace, values, option_string):

        key = values[0]

        if (not self.dest):
            setattr(namespace, key, self.const);
        else:
            try:
                d = getattr(namespace, self.dest);
                if d is None:
                    d = [];
            except AttributeError:
                d = [];
            d.append(key);
            setattr(namespace, self.dest, d);


class opt_action_help(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):

        if (not values or values == "elp"): # in case of -help: seen as -h elp
            helptext = """
Bibolamazi Version %(version)s by Philippe Faist (C) 2013
Licensed under the terms of the GNU Public License GPL, version 3 or higher.

""" % {'version': get_version()}
            helptext += parser.format_help()
            pydoc.pager(helptext)
            parser.exit()

        thefilter = values

        import filters;
        try:
            helptext = filters.format_filter_help(thefilter);
            pydoc.pager(helptext);
            parser.exit();
        except filters.NoSuchFilter:
            logger.error("No Such Filter: `"+thefilter+"'");
            parser.exit();




FILTERS_HELP = """
List of available filters:
--------------------------
%(filter_list)s
--------------------------

Use  bibolamazi --help <filter>  for more information about each filter.

"""

class opt_list_filters(argparse.Action):
    def __init__(self, nargs=0, **kwargs):
        argparse.Action.__init__(self, nargs=0, **kwargs);
        
    def __call__(self, parser, namespace, values, option_string):

        import filters;

        filter_list = [
            "%-16s %s" % (f+': ', filters.get_filter_class(f).getHelpDescription())
            for f in filters.__all__
            ]

        all_text = FILTERS_HELP % {'filter_list': "\n".join(filter_list)};

        pydoc.pager(all_text);
        parser.exit();




