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
import os
import os.path
import shlex
import inspect
import argparse
import textwrap
from collections import namedtuple

from core.argparseactions import store_key_val, store_key_const, store_key_bool
from core.blogger import logger
from core import butils


# don't allow the use of "from filters import *" -- it's time consuming to detect all filters; so
# detect the filters only when needed, when calling `detect_filters()`
__all__ = []



# some exception classes.

class NoSuchFilter(Exception):
    def __init__(self, fname, errorstr=None):
        Exception.__init__(self, "No such filter or import error: "+fname+(": "+errorstr if errorstr else ""));

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





# information about filters and modules etc.


_filter_modules = {}
_filter_list = None

# For pyinstaller: precompiled filter list

_filter_precompiled_load_attempted = False
_filter_precompiled_loaded = False
def _load_precompiled_filters():
    global _filter_precompiled_load_attempted
    global _filter_precompiled_loaded
    global _filter_list
    global _filter_modules
    
    _filter_precompiled_load_attempted = True
    try:
        import bibolamazi_compiled_filter_list
        _filter_list = bibolamazi_compiled_filter_list.filter_list
        for f in _filter_list:
            _filter_modules[f] = bibolamazi_compiled_filter_list.__dict__[f]
        _filter_precompiled_loaded = True
    except ImportError:
        pass


# store additional information about the modules.

def get_module(name, raise_nosuchfilter=True):
    name = str(name)
    if not re.match(r'^[.\w]+$', name):
        raise ValueError("Filter name may only contain alphanum chars and dots (got %r)"%(name))

    if (not _filter_precompiled_load_attempted):
        _load_precompiled_filters()

    # already open
    if (name in _filter_modules):
        return _filter_modules[name];

    # try to open it
    try:
        mod = importlib.import_module('.'+name, package='filters');
        _filter_modules[name] = mod;
    except ImportError as e:
        if (not raise_nosuchfilter):
            return None
        raise NoSuchFilter(name, e.message);

    # and return it
    return _filter_modules[name];



_rxsuffix = re.compile(r'\.pyc?$')

##def _detect_list_of_all_filter_modules(file):
##    thisdir = os.path.dirname(os.path.realpath(file));

##    for fname in os.listdir(thisdir):
##        # make sure this is a .py or .pyc file
##        if (_rxsuffix.search(fname) is None):
##            continue

##        # deduce the module name relative to here
##        modname = fname
##        modname = _rxsuffix.sub('', modname)
        
##        # is a filter module?
##        m = get_module(modname, False)
##        if (m is None or not hasattr(m, 'bibolamazi_filter_class')):
##            continue

##    logger.debug('Filters detected.')

##    return sorted(_filter_modules.keys());

def detect_filters(force_redetect=False):
    global _filter_list

    if (not _filter_precompiled_load_attempted):
        _load_precompiled_filters()

    if (_filter_list is not None and not force_redetect):
        return _filter_list;
    
    if (_filter_precompiled_loaded):
        # no use going further, if we have a precompiled list it means we can't detect the filters.
        return _filter_list
    
    thisdir = os.path.dirname(os.path.realpath(__file__));

    _filter_list = [];

    logger.debug('Detecting filters ...')

    def tomodname(x):
        if (os.sep):
            x = x.replace(os.sep, '.')
        if (os.altsep):
            x = x.replace(os.altsep, '.')
        return x
    def startswithdotslash(x):
        if (os.sep and x.startswith('.'+os.sep)):
            return True
        if (os.altsep and x.startswith('.'+os.altsep)):
            return True
        return False

    for (root, dirs, files) in os.walk(thisdir):
        if (not '__init__.py' in files and
            not '__init__.pyc' in files and
            not '__init__.pyo' in files):
            # skip this directory, not a python module. also skip all subdirectories.
            dirs[:] = []
            continue

        for fname in sorted(files):
            # make sure this is a .py or .pyc file
            if (_rxsuffix.search(fname) is None):
                continue
            if (fname.startswith('__init__.')):
                continue

            # deduce the module name relative to here
            modname = os.path.join(os.path.relpath(root, thisdir), fname)
            modname = _rxsuffix.sub('', modname)
            if (startswithdotslash(modname)):
                modname = modname[2:]
            modname = tomodname(modname)

            if (modname in _filter_list):
                # we already have this one
                continue
            
            # is a filter module?
            m = get_module(modname, False)
            if (m is None or not hasattr(m, 'bibolamazi_filter_class')):
                continue

            # yes, _is_ a filter module.
            _filter_list.append(modname)

    logger.debug('Filters detected.')

    return _filter_list;



def get_filter_class(name):
    
    fmodule = get_module(name);

    return fmodule.bibolamazi_filter_class();


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

    fclass = fmodule.bibolamazi_filter_class();

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
        import traceback
        logger.debug("Filter exception:\n" + traceback.format_exc())
        raise FilterCreateArgumentError(unicode(e), name)

    # and finally, instantiate the filter.

    logger.debug('calling fclass('+','.join([repr(x) for x in pargs])+', '+
                  ','.join([repr(k)+'='+repr(v) for k,v in kwargs.iteritems()]) + ')');

    # exceptions caught here are those thrown from the filter constructor itself.
    try:
        return fclass(*pargs, **kwargs);
    except Exception as e:
        import traceback
        logger.debug("Filter exception:\n" + traceback.format_exc())
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
            thisend = (argdocspos[k+1].start() if k < len(argdocspos)-1 else len(doc))
            # adjust whitespace in docstr
            docstr = doc[m.end():thisend].strip()
            docstr = textwrap.TextWrapper(width=80, replace_whitespace=True, drop_whitespace=True).fill(docstr)
            argdoclist.append(_ArgDoc(argname=m.group('argname'),
                                      argtypename=m.group('argtypename'),
                                      doc=docstr))
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
        fclasssyntaxdesc = fclass.__name__+("(" + " ".join([xpart for xpart in [
            (", ".join([fmtarg(k, fargs, defaults)
                        for k in range(len(fargs))
                        if fargs[k] != "self"])),
            ("[...]" if varargs else ""),
            ("[..=...]" if keywords else ""),
            ] if xpart]) + ")");

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
        self._filtervaroptions = []

        def make_filter_option(farg):
            fopt = farg.replace('_', '-');
            argdoc = argdocs.get(farg, _ArgDoc(farg,None,None))
            group_filter.add_argument('--'+fopt, action='store', dest=farg,
                                      help=argdoc.doc.replace('%','%%'));
            return argdoc


        argdocs_left = [ x.argname for x in argdoclist ];
        for farg in fargs:
            # skip 'self'
            if (farg == 'self'):
                continue
            # normalize name
            argdoc = make_filter_option(farg)
            argdocs_left.remove(farg)
            self._filteroptions.append(argdoc)

        # in case user specified more docs than declared arguments, they document additional arguments that
        # can be given as **kwargs
        if (not keywords and argdocs_left):
            raise FilterError("Filter's argument documentation provides additional documentation for "
                              "non-arguments %r. (Did you forget a **kwargs?)"
                              %(argdocs_left), name=filtername)
        for farg in argdocs_left:
            argdoc = make_filter_option(farg)
            self._filtervaroptions.append(argdoc)

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

    def filterOptions(self):
        """This gives a list of `_ArgDoc` named tuples."""
        return self._filteroptions + self._filtervaroptions

    def filterDeclOptions(self):
        """This gives a list of `_ArgDoc` named tuples."""
        return self._filteroptions
    def filterVarOptions(self):
        """This gives a list of `_ArgDoc` named tuples."""
        return self._filtervaroptions

    def optionSpec(self, argname):
        l = [x for x in self._filteroptions if x.argname == argname]
        if (not len(l)):
            return None
        return l[0]

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

        try:
            parts = shlex.split(optionstring);
        except ValueError as e:
            raise FilterOptionsParseError("Error parsing option string: %s\n\t%s" %(e, optionstring.strip()),
                                          self._filtername)
        
        try:
            args = p.parse_args(parts);
        except FilterOptionsParseError as e:
            e.name = self._filtername
            raise

        # parse and collect arguments now

        dargs = vars(args);
        pargs = [];
        kwargs = {};

        def set_kw_arg(kwargs, argname, argval):
            # set the type correctly, too.
            argspec = self.optionSpec(argname)
            if (argspec is not None):
                if (argspec.argtypename is not None):
                    typ = butils.resolve_type(argspec.argtypename, self._fmodule)
                else:
                    typ = str
                kwargs[argname] = typ(argval)
            else:
                kwargs[argname] = argval # raw type if we can't figure one out (could be extra kwargs argument)

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
                    set_kw_arg(kwargs, thekey, v)

                    logger.debug("Set option `%s' to `%s'" %(thekey, v))

                continue

            if (argval is None):
                continue

            set_kw_arg(kwargs, arg, argval)

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
    
