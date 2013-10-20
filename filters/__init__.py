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


import sys
import importlib
import re
import shlex
import inspect
import argparse
import textwrap
from collections import namedtuple

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

    def setName(self, name):
        self.name = name

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


def filter_uses_default_arg_parser(name):

    fmodule = get_module(name)

    if (hasattr(fmodule, 'parse_args')):
        return False
    return True

def filter_arg_parser(name):
    """If the filter `name` uses the default-based argument parser, then returns
    a DefaultFilterOptions object that is initialized with the options available
    for the given filter `name`.

    If the filter has its own option parsing mechanism, this returns `None`.
    """
    
    fmodule = get_module(name)

    if (hasattr(fmodule, 'parse_args')):
        return None

    return DefaultFilterOptions(name);



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
            raise FilterError("Filter's parse_args() didn't return a tuple (args, kwargs)", name=name)
    else:
        fopts = DefaultFilterOptions(name, fclass=fclass)
        (pargs, kwargs) = fopts.parse_optionstring(optionstring);

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






_ArgDoc = namedtuple('_ArgDoc', ('argname', 'argtypename', 'doc',))


class FilterArgumentParser(argparse.ArgumentParser):
    def __init__(self, filtername, **kwargs):
        super(FilterArgumentParser, self).__init__(**kwargs)
        self._filtername = filtername

    def error(self, message):
        self.exit(2, '%s: error: %s' % (self.prog, message))

    def exit(self, status=0, message=None):
        if message:
            msg = message.rstrip()
        else:
            msg = 'Filter Arguments Error (code %d)' % (status)

        raise FilterOptionsParseError(msg, self._filtername)


_rxargdoc = re.compile(r'^\s*(-\s*|\*)(?P<argname>\w+)\s*(\((?P<argtypename>\w+)\))?\s*:\s*', re.MULTILINE);

_add_epilog="""

Have a lot of fun!
"""

class DefaultFilterOptions:
    def __init__(self, filtername, fclass=None):
        self._filtername = filtername

        self._fmodule = get_module(filtername)

        if fclass is None:
            fclass = get_filter_class(filtername)

        self._fclass = fclass

        # find out what the arguments to the filter constructor are
        (fargs, varargs, keywords, defaults) = inspect.getargspec(fclass.__init__);

        # get some doc about the parameters
        doc = fclass.__init__.__doc__;
        if (doc is None):
            doc = ''
        argdocspos = [];
        for m in re.finditer(_rxargdoc, doc):
            argdocspos.append(m);
        argdoclist = [];
        begindoc = None;
        for k in range(len(argdocspos)):
            m = argdocspos[k]
            if (begindoc is None):
                begindoc = doc[:m.start()];
            thisend = (argdocspos[k+1].start() if k < len(argdocspos)-1 else len(doc));
            argdoclist.append(_ArgDoc(argname=m.group('argname'),
                                      argtypename=m.group('argtypename'),
                                      doc=doc[m.end():thisend].strip()))
        argdocs = dict([(x.argname, x) for x in argdoclist])

        self._use_auto_case = True
        if (re.search(r'[A-Z]', "".join(fargs))):
            logger.debug("filter "+self._filtername+": will not automatically adjust option letter case.");
            self._use_auto_case = False

        if (defaults is None):
            defaults = [];
        def fmtarg(k, fargs, defaults):
            s = fargs[k];
            off = len(fargs)-len(defaults);
            if (k-off >= 0):
                s += "="+repr(defaults[k-off]);
            return s
        fclasssyntaxdesc = fclass.__name__+("(" + (", ".join([fmtarg(k, fargs, defaults)
                                                              for k in range(len(fargs))
                                                              if fargs[k] != "self"]))
                                            + (" ..." if (varargs or keywords) else "") + ")");

        p = FilterArgumentParser(filtername=self._filtername,
                                 prog=self._filtername,
                                 description=fclass.getHelpDescription(),
                                 epilog=
                                 "------------------------------\n\n"+
                                 fclass.getHelpText()+"\n"+_add_epilog,
                                 add_help=False,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 );

        group_filter = p.add_argument_group('Filter Arguments');

        # add option for all arguments

        self._filteroptions = []
        
        for farg in fargs:
            # skip 'self'
            if (farg == 'self'):
                continue
            # normalize name
            fopt = re.sub('_', '-', farg);
            argdoc = argdocs.get(farg, _ArgDoc(farg,None,None))
            group_filter.add_argument('--'+fopt, action='store', dest=farg,
                                      help=argdoc.doc);
            self._filteroptions.append(argdoc)

        group_general = p.add_argument_group('Other Options')

        # a la ghostscript: -sOutputFile=blahblah -sKey=Value
        group_general.add_argument('-s', action=store_key_val, dest='_s_args', metavar='Key=Value',
                                   exception=FilterOptionsParseError,
                                   help="-sKey=Value sets parameter values");
        group_general.add_argument('-d', action=store_key_bool, const=True, dest='_d_args',
                                   metavar='Switch[=<value>]', exception=FilterOptionsParseError,
                                   help="-dSwitch[=<value>] sets flag `Switch' to given boolean value, by default "
                                   "True. Valid boolean values are 1/T[rue]/Y[es]/On and 0/F[alse]/N[o]/Off");

        # allow also to give arguments without the keywords.
        group_general.add_argument('_args', nargs='*', metavar='<arg>',
                                   help="Additional arguments will be passed as is to the filter--see "
                                   "documentation below");

        p.add_argument_group(u"Python filter syntax",
                             textwrap.fill(fclasssyntaxdesc, width=80, subsequent_indent='        '));

        p.add_argument_group(u'Note', textwrap.dedent(u"""\
            For passing option values, you may use either the `--key value' syntax, or the
            (ghostscript-like) `-sKey=Value' syntax. For switches, use -dSwitch to set the
            given option to True. When using the -s or -d syntax, the option names are
            camel-cased, i.e. an option like `--add-description arxiv' can be specified as
            `-sAddDescription=arxiv'. Likewise, `--preserve-ids 1' can provided as
            `-dPreserveIds' or `-dPreserveIds=yes'."""));


        self._parser = p


    def filtername(self):
        return self._filtername

    def filteroptions(self):
        """This gives a list of `_ArgDoc` named tuples."""
        return self._filteroptions

    def use_auto_case(self):
        return self._use_auto_case

    def getSOptNameFromArg(self, x):
        if (not self._use_auto_case):
            return x
        x = re.sub(r'(?:^|_)([a-z])', lambda m: m.group(1).upper(), x)
        return x

    def getArgNameFromSOpt(self, x):
        if (not self._use_auto_case):
            return x
        x = re.sub(r'[A-Z]', lambda mo: ('_' if mo.start() > 0 else '')+mo.group().lower(), x);
        return x


    def parser(self):
        return self._parser


    def parse_optionstring(self, optionstring):

        logger.debug("parse_optionstring: "+self._filtername+"; fclass="+repr(self._fclass)
                     +"; optionstring="+optionstring);

        p = self._parser

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
                    therealkey = self.getArgNameFromSOpt(thekey);
                    kwargs[therealkey] = theval

                    logger.debug("Set switch `%s' to %s" %(thekey, "True" if theval else "False"))

                continue

            if (arg == '_s_args' and argval is not None):
                # get all the set args
                for (key, v) in argval:
                    thekey = self.getArgNameFromSOpt(key);
                    kwargs[thekey] = v

                    logger.debug("Set option `%s' to `%s'" %(thekey, v))

                continue

            if (argval is None):
                continue

            kwargs[arg] = argval;

        return (pargs, kwargs);


    def format_filter_help(self):
        prolog = self._fclass.getHelpAuthor();
        if (prolog):
            prolog += "\n\n";

        return prolog + self._parser.format_help();


def format_filter_help(filtname):
    #
    # Get the parser via the filter, and use its format_help()
    #

    fmodule = get_module(filtname)

    if (hasattr(fmodule, 'format_help')):
        return fmodule.format_help();

    # otherwise, use the help formatter of the default option parser
    fopt = DefaultFilterOptions(filtname)
    return fopt.format_filter_help()
    
