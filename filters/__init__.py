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


import importlib
import re
import shlex
import inspect
import argparse
import textwrap

from core.argparseactions import store_key_val, store_key_const, store_key_bool
from core.blogger import logger


# list all filters here.
__all__ = ( 'arxiv',
            'duplicates',
            'url',
            'nameinitials',
            'fixes',
            'orderentries',
            )


# some exception classes.

class NoSuchFilter(Exception):
    def __init__(self, fname):
        Exception.__init__(self, "No such filter: "+fname);

class FilterError(Exception):
    def __init__(self, errorstr, name=None):
        self.name = name;
        self.errorstr = errorstr;
        Exception.__init__(self, unicode(self));

    def fmt(self, name):
        return "Filter %s: %s" %(name, self.errorstr)

    def __unicode__(self):
        name = ( "`%s'" %(self.name) if self.name else "<unknown>" )
        return self.fmt(name)

    def __str__(self):
        return self.unicode().encode('ascii')
    

class FilterOptionsParseError(FilterError):
    def fmt(self, name):
        return "Can't parse options for filter %s: %s" %(name, self.errorstr)

class FilterCreateError(FilterError):
    def fmt(self, name):
        return "Can't create filter %s: %s" %(name, self.errorstr)

class FilterCreateArgumentError(FilterError):
    def fmt(self, name):
        return "Bad arguments provided to filter %s: %s" %(name, self.errorstr)



# store additional information about the modules.

filter_modules = {};

def get_module(name):
    name = str(name)
    if not re.match(r'^[.\w]+$', name):
        raise ValueError("Filter name may only contain alphanum chars and dots")

    # already open
    if (name in filter_modules):
        return filter_modules[name];

    # try to open it
    try:
        mod = importlib.import_module('filters.'+name);
        filter_modules[name] = mod;
    except ImportError:
        raise NoSuchFilter(name);

    # and return it
    return filter_modules[name];


def get_filter_class(name):
    
    fmodule = get_module(name);

    return fmodule.get_class();


def make_filter(name, optionstring):

    fmodule = get_module(name);

    fclass = fmodule.get_class();

    pargs = [];
    kwargs = {};
    if (hasattr(fmodule, 'parse_args')):
        x = fmodule.parse_args(optionstring);
        try:
            (pargs, kwargs) = x;
        except TypeError, ValueError:
            pargs = [];
            kwargs = x;
    else:
        (pargs, kwargs) = _default_parse_optionstring(name, fclass, optionstring);

    # first, validate the arguments to the function call with inspect.getcallargs()
    try:
        pargs2 = [None]+pargs; # extra argument for `self` slot
        inspect.getcallargs(fclass.__init__, *pargs2, **kwargs)
    except Exception as e:
        raise FilterCreateArgumentError(unicode(e), name)

    # and finally, instantiate the filter.

    logger.debug('calling fclass('+','.join([repr(x) for x in pargs])+', '+
                  ','.join([repr(k)+'='+repr(v) for k,v in kwargs.iteritems()]) + ')');

    # exceptions caught here are those thrown from the filter constructor itself.
    try:
        return fclass(*pargs, **kwargs);
    except Exception as e:
        msg = unicode(e);
        if (not isinstance(e, FilterError) and e.__class__ != Exception):
            # e.g. TypeError or SyntaxError or NameError or KeyError or whatever...
            msg = e.__class__.__name__ + ": " + msg
        raise FilterCreateError(msg, name)



_add_epilog="""

Have a lot of fun!
"""

_rxargdoc = re.compile(r'\n?\s*\*(\w+):\s*', re.S);

#
# a basic, default option parser. Simply constructs an argparse object with the function's argument
# names mapped to options, and adds the ability to use the -sKey=Value and -dSwitch options.
#
def _default_option_parser(name, fclass):

    (fargs, varargs, keywords, defaults) = inspect.getargspec(fclass.__init__);

    # get some doc about the parameters
    doc = fclass.__init__.__doc__;
    if (doc is None):
        doc = ''
    pos = [];
    for m in re.finditer(_rxargdoc, doc):
        pos.append(m);
    argdocs = {};
    begindoc = None;
    for k in range(len(pos)):
        m = pos[k]
        if (begindoc is None):
            begindoc = doc[:m.start()];
        thisend = (pos[k+1].start() if k < len(pos)-1 else len(doc));
        argdocs[m.group(1)] = doc[m.end():thisend];

    use_auto_case = True
    if (re.search(r'[A-Z]', "".join(fargs))):
        logger.debug("filter "+name+": will not automatically adjust option letter case.");
        use_auto_case = False

    if (defaults is None):
        defaults = [];
    def fmtarg(k, fargs, defaults):
        s = fargs[k];
        off = len(fargs)-len(defaults);
        if (k-off >= 0):
            s += "="+repr(defaults[k-off]);
        return s
    fclasssyntaxdesc = fclass.__name__+("(" + (", ".join([fmtarg(k, fargs, defaults) for k in range(len(fargs)) if fargs[k] != "self"]))
                                        + (" ..." if (varargs or keywords) else "") + ")");
    

    p = argparse.ArgumentParser(prog=name,
                                description=fclass.getHelpDescription(),
                                epilog=
                                "------------------------------\n\n"+
                                fclass.getHelpText()+"\n"+_add_epilog,
                                add_help=False,
                                formatter_class=argparse.RawDescriptionHelpFormatter,
                                );

    group_filter = p.add_argument_group('Filter Arguments');

    for farg in fargs:
        # skip 'self'
        if (farg == 'self'):
            continue
        # normalize name
        fopt = re.sub('_', '-', farg);
        group_filter.add_argument('--'+fopt, action='store', dest=farg,
                                  help=argdocs.get(farg, None));


    group_general = p.add_argument_group('Other Options')

    # a la ghostscript: -sOutputFile=blahblah -sKey=Value
    group_general.add_argument('-s', action=store_key_val, dest='_s_args', metavar='Key=Value',
                               exception=FilterOptionsParseError,
                               help="-sKey=Value sets parameter values");
    group_general.add_argument('-d', action=store_key_bool, const=True, dest='_d_args', metavar='Switch[=<value>]',
                               exception=FilterOptionsParseError,
                               help="-dSwitch[=<value>] sets flag `Switch' to given boolean value, by default True. Valid"+
                               " boolean values are 1/T[rue]/Y[es]/On and 0/F[alse]/N[o]/Off");

    # allow also to give arguments without the keywords.
    group_general.add_argument('_args', nargs='*', metavar='<arg>',
                               help='Additional arguments will be passed as is to the filter--see documentation below');

    p.add_argument_group(u"Python filter syntax",
                         textwrap.fill(fclasssyntaxdesc, width=80, subsequent_indent='        '));

    p.add_argument_group(u'Note', textwrap.dedent(u"""\
        For passing option values, you may use either the `--key value' syntax, or the
        (ghostscript-like) `-sKey=Value' syntax. For switches, use -dSwitch to set the
        given option to True. When using the -s or -d syntax, the option names are
        camel-cased, i.e. an option like `--add-description arxiv' can be specified as
        `-sAddDescription=arxiv'. Likewise, `--preserve-ids 1' can provided as
        `-dPreserveIds' or `-dPreserveIds=yes'."""));


    return (p, use_auto_case)

def _getArgNameFromSOpt(x, use_auto_case=True):
    if (not use_auto_case):
        return x
    x = re.sub('[A-Z]', lambda mo: ('_' if mo.start() > 0 else '')+mo.group().lower(), x);
    return x

    
def _default_parse_optionstring(name, fclass, optionstring):

    logger.debug("_default_parse_optionstring: name: "+name+"; fclass="+repr(fclass)
                 +"; optionstring="+optionstring);

    (p, use_auto_case) = _default_option_parser(name, fclass);

    parts = shlex.split(optionstring);
    try:
        args = p.parse_args(parts);
    except FilterOptionsParseError as e:
        e.name = name
        raise

    # parse and collect arguments now

    dargs = vars(args);
    pargs = [];
    kwargs = {};

    for (arg, argval) in dargs.iteritems():
        if (arg == '_args'):
            pargs = argval;
            continue
        if (arg == '_d_args' and argval is not None):
            # get all the defined args
            for (thekey, theval) in argval:
                # store this definition
                therealkey = _getArgNameFromSOpt(thekey, use_auto_case);
                kwargs[therealkey] = theval

                logger.debug("Set switch `%s' to %s" %(thekey, "True" if theval else "False"))
                
            continue
            
        if (arg == '_s_args' and argval is not None):
            # get all the set args
            for (key, v) in argval:
                thekey = _getArgNameFromSOpt(key, use_auto_case);
                kwargs[thekey] = v

                logger.debug("Set option `%s' to `%s'" %(thekey, v))
                
            continue

        if (argval is None):
            continue
        
        kwargs[arg] = argval;
    
    #import pdb; pdb.set_trace();

    return (pargs, kwargs);
        





def format_filter_help(name):
    #
    # Get the parser via the filter, and use its format_help()
    #

    fmodule = get_module(name);

    if (hasattr(fmodule, 'format_help')):
        return fmodule.format_help();

    # otherwise, use the help formatter of the default option parser

    fclass = fmodule.get_class();

    (p, use_auto_case) = _default_option_parser(name, fclass);

    prolog = fclass.getHelpAuthor();
    if (prolog):
        prolog += "\n\n";

    return prolog + p.format_help();
    

