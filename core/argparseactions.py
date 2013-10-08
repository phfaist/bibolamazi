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
import os
import sys
import os.path
import argparse

# pydoc.pager(text) will open a pager for text (e.g. less), or pipe it out, and do everything as
# it should automatically.
import pydoc

import butils;
from butils import getbool
from blogger import logger



class store_or_count(argparse.Action):
    def __init__(self, option_strings, dest, nargs='?', **kwargs):
        # some checks
        if nargs != '?':
            raise ValueError('store_or_const: nargs must be "?"');

        if ('type' in kwargs):
            raise TypeError("Can't enforce a type on a store_or_count option!");
        
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

        # Note: I don't know how to fix situations like "prog.py -v some_prog_arg" which is taken
        # as "-v some_prog_arg" ... we would need to interfere with the option parser to match the
        # argument not to the option (because of the wrong type), but to the program...


        # get the argument of -v (e.g.,  -v2  or  --verbose 2  or  --verbose=2 )
        if (isinstance(values, basestring)):
            try:
                values = int(values);
            except ValueError:
                opt_name = ", ".join(self.option_strings)
                parser.error(u"Invalid argument to %s: `%s' (maybe use %s option at the end of the command?)"
                             %(opt_name, values, opt_name))

        if (values is not None):
            # value provided
            val = int(values);
        else:
            val += 1;
        
        setattr(namespace, self.dest, val);



rxkeyval = re.compile(r'^([\w.-]+)=(.*)$', re.DOTALL);

class store_key_val(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, exception=ValueError, **kwargs):
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_val actions must be == 1')

        self.exception = exception

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
            raise self.exception("cannot parse key=value pair: "+repr(values));

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


class store_key_bool(argparse.Action):
    def __init__(self, option_strings, dest, nargs=1, const=True,
                 exception=ValueError, **kwargs):
        
        # some checks
        if nargs != 1:
            raise ValueError('nargs for store_key_bool actions must be == 1')

        self.exception = exception

        super(store_key_bool, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=bool(const),
            **kwargs);


    def __call__(self, parser, namespace, values, option_string):

        key = values[0]

        storeval = self.const

        eqindex = key.find('=');
        if (eqindex != -1):
            try:
                storeval = getbool(key[eqindex+1:])
                key = key[:eqindex];
            except ValueError as e:
                raise self.exception(unicode(e))

        if (not self.dest):
            setattr(namespace, key, self.const);
        else:
            try:
                d = getattr(namespace, self.dest);
                if d is None:
                    d = [];
            except AttributeError:
                d = [];
            d.append(
                (key, storeval,)
                );
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


def helptext_prolog():
    return ("""
Bibolamazi Version %(version)s by Philippe Faist (C) 2013
Licensed under the terms of the GNU Public License GPL, version 3 or higher.

""" % { 'version': butils.get_version(),
        } );
    


class opt_action_help(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):

        if (not values or values == "elp"): # in case of -help: seen as -h elp
            helptext = helptext_prolog()
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



class opt_action_version(argparse.Action):
    def __call__(self, parser, namespace, values, option_string):

        helptext = """\
Version: %(version)s
Bibolamazi by Philippe Faist (C) 2013
Licensed under the terms of the GNU Public License GPL, version 3 or higher.
""" % { 'version': butils.get_version(),
}
        sys.stdout.write(helptext);
        parser.exit()





FILTERS_HELP = """

List of available filters:
--------------------------

%(filter_list)s

--------------------------

Use  bibolamazi --help <filter>  for more information about each filter and
its options.


"""


def help_list_filters():

    import textwrap;
    import filters;

    def fmt_filter_helpline(f):

        nlindentstr = "\n%16s"%(""); # newline, followed by 16 whitespaces
        return ( "  %-13s " %(f) +
                 nlindentstr.join(textwrap.wrap(filters.get_filter_class(f).getHelpDescription(),
                                                (80-16) # 80 line width, -16 indent chars
                                                ))
                 )

    filter_list = [
        fmt_filter_helpline(f)
        for f in filters.__all__
        ]

    return FILTERS_HELP % {'filter_list': "\n".join(filter_list)};



class opt_list_filters(argparse.Action):
    def __init__(self, nargs=0, **kwargs):
        if nargs != 0:
            raise ValueError('nargs for opt_list_filters must be == 0')

        argparse.Action.__init__(self, nargs=0, **kwargs);
        
    def __call__(self, parser, namespace, values, option_string):

        all_text = help_list_filters()

        pydoc.pager(all_text);
        parser.exit();




class opt_init_empty_template(argparse.Action):
    def __init__(self, nargs=1, **kwargs):
        if nargs != 1:
            raise ValueError('nargs for init_empty_template must be == 1')
        
        argparse.Action.__init__(self, nargs=1, **kwargs);
        
    def __call__(self, parser, namespace, values, option_string):

        import bibolamazifile;

        try:
            newfilename = values[0];
        except IndexError:
            newfilename = values;

        if (os.path.exists(newfilename)):
            logger.error("Cowardly refusing to overwrite existing file `%s'. Remove it first."
                         %(newfilename))
            parser.exit(9);

        bfile = bibolamazifile.BibolamaziFile(newfilename, create=True);
        bfile.save_to_file();

        parser.exit();

