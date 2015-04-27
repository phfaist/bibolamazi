################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2014 by Philippe Faist                                       #
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
import types
from collections import namedtuple, OrderedDict
import logging
logger = logging.getLogger(__name__)

from core.argparseactions import store_key_val, store_key_const, store_key_bool
from core import butils




# some exception classes.

class NoSuchFilter(Exception):
    """
    Signifies that the requested filter was not found. See also `get_module()`.
    """
    def __init__(self, fname, errorstr=None):
        Exception.__init__(self, "No such filter or import error: "+fname+(": "+errorstr if errorstr else ""));

class NoSuchFilterPackage(Exception):
    """
    Signifies that the requested filter package was not found. See also `get_module()`.
    """
    def __init__(self, fpname, errorstr="No such filter package", fpdir=None):
        Exception.__init__(self, "No such filter package or import error: `"+ fpname + "'"
                           + (" (dir=`%s')"%(fpdir) if fpdir is not None else "")
                           + (": "+errorstr if errorstr else ""));
        

class FilterError(Exception):
    """
    Signifies that there was some error in creating or instanciating the filter, or that
    the filter has a problem. (It could be, for example, that a function defined by the
    filter does not behave as expected. Or, that the option string passed to the filter
    could not be parsed.)

    This is meant to signify a problem occuring in this factory, and not in the
    filter. The filter classes themselves should raise `bibfilter.BibFilterError` in the
    event of an error inside the filter.
    """
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
        return self.unicode().encode('latin1')
    

class FilterOptionsParseError(FilterError):
    """
    Raised when there was an error parsing the option string provided by the user.
    """
    def fmt(self, name):
        return "Can't parse options for filter %s: %s" %(name, self.errorstr)


class FilterOptionsParseErrorHintSInstead(FilterOptionsParseError):
    """
    As FilterOptionsParseError, but hinting that maybe -sOption=Value was meant instead of
    -dOption=Value.
    """
    def fmt(self, name):
        return (super(FilterOptionsParseErrorHintSInstead, self).fmt(name)
                + " (was -sKEY=VAL meant instead of -dKEY=VAL?)")


class FilterCreateError(FilterError):
    """
    There was an error instantiating the filter. This could be due because the filter
    constructor raised an exception.
    """
    def fmt(self, name):
        return "Can't create filter %s: %s" %(name, self.errorstr)

class FilterCreateArgumentError(FilterError):
    """
    Although the filter arguments may have been successfully parsed, they may still not
    translate to a valid python filter call (i.e. in terms of function arguments, for
    example when using both positional and keyword arguments). This error is raised when
    the composed filter call is not valid.
    """
    def fmt(self, name):
        return "Bad arguments provided to filter %s: %s" %(name, self.errorstr)




class PrependOrderedDict(OrderedDict):
    """
    An ordered dict that stores the items in the order where the first item is the one
    that was added/modified last.
    """
    def __init__(self, *args, **kwargs):
        self.isupdating = False
        OrderedDict.__init__(self, *args, **kwargs)
        
    def __setitem__(self, key, value):
        if self.isupdating:
            OrderedDict.__setitem__(self, key, value)
            return
        
        self.isupdating = True
        try:
            if key in self:
                del self[key]
            ourself = self.items()
            self.clear()
            self.update({key: value})
            self.update(ourself)
        finally:
            self.isupdating = False

    def set_items(self, items):
        self.isupdating = True
        try:
            self.clear()
            self.update(items)
        finally:
            self.isupdating = False

    def set_at(self, idx, key, value):
        self.isupdating = True
        try:
            items = self.items()
            self.clear()
            self.update(items[:idx] + [ (key, value) ] + items[idx+1:])
        finally:
            self.isupdating = False

    def item_at(self, idx):
        return self.items()[idx]



# list of packages providing bibolamazi filters. `filters` is the core bibolamazi filters
# package. The value is the path to add when looking for the package, or None to add no
# path.
filterpath = PrependOrderedDict([
    ('filters', None,),
    ])




# information about filters and modules etc.


_filter_list = None
_filter_package_listings = None
_filter_modules = {}

# For pyinstaller: precompiled filter list

_filter_precompiled_cache = {}
def load_precompiled_filters(filterpackage, precompiled_modules):
    """
    `filterpackage`: name of the filter package under which to scope the given precompiled
        filter modules.
    `precompiled_modules`: a dictionary of `'filter_name': filter_module` of precompiled
        filter modules, along with their name.
    """

    global _filter_precompiled_cache
    
    _filter_precompiled_cache[filterpackage] = precompiled_modules


def reset_filters_cache():
    global _filter_list
    global _filter_package_listings
    global _filter_modules
    global _filter_precompiled_cache

    _filter_list = None
    _filter_package_listings = None
    _filter_modules = {}
    # of course, don't reset the precompiled cache!!


# utility to warn the user of invalid --filterpackage option
def validate_filter_package(fpname, fpdir, raise_exception=True):
    oldsyspath = sys.path
    mod = None
    if fpdir:
        sys.path = [fpdir] + sys.path
    try:
        mod = importlib.import_module(fpname)
    except ImportError:
        if raise_exception:
            raise NoSuchFilterPackage(fpname, fpdir=fpdir)
        return False
    finally:
        sys.path = oldsyspath
    return True if mod else False


# store additional information about the modules.

def get_module(name, raise_nosuchfilter=True, filterpackage=None):

    global filterpath

    name = str(name)

    logger.longdebug("get_module: name=%r, raise_nosuchfilter=%r, filterpackage=%r",
                     name, raise_nosuchfilter, filterpackage)

    # shortcut: a filter name may be 'filterpackage:the.module.name' to force search in a
    # specific filter package.
    if ':' in name and filterpackage is None:
        fpparts = name.split(':',1)
        return get_module(name=fpparts[1], raise_nosuchfilter=raise_nosuchfilter,
                          filterpackage=fpparts[0])

    if not re.match(r'^[.\w]+$', name):
        raise ValueError("Filter name may only contain alphanum chars and dots (got %r)"%(name))


    import_errors = []

    def get_module_in_filterpackage(filterpackname):

        global _filter_precompiled_cache
        global filterpath
        
        logger.longdebug("Attempting to load filter %s from package %s", name, filterpackname)

        mod = None

        def dirstradd(filterdir):
            return " (dir `%s')"%(filterdir) if filterdir else ""
        
        def remember_import_error(import_errors, name, filterpackname, filterdir, exctypestr, e):
            import_errors.append(u"Attempt failed to import module `%s' in package `%s'%s: %s\n > %s"
                                 %(name, filterpackname, dirstradd(filterdir), exctypestr, unicode(e)))
            
        # first, search the actual module.
        oldsyspath = sys.path
        filterdir = filterpath[filterpackname]
        if filterdir:
            sys.path = [filterdir] + sys.path
        try:
            mod = importlib.import_module('.'+name, package=filterpackname);
        except ImportError as e:
            logger.debug("Failed to import module `%s' from package %s%s: %s",
                         name, filterpackname, dirstradd(filterdir), unicode(e))
            #import_errors.append(u"Attempted import module %s in package `%s'%s failed:\n > %s"
            #                     %(name, filterpackname, "(dir `%s')"%(filterdir) if filterdir else "",
            #                       unicode(e)))
            remember_import_error(import_errors, name, filterpackname, filterdir, e.__class__.__name__, e)
            mod = None
        except Exception as e:
            logger.warning("Failed to import module `%s' from package %s%s:\n > %s: %s\n",
                           name, filterpackname, dirstradd(filterdir), e.__class__.__name__, unicode(e))
            remember_import_error(import_errors, name, filterpackname, filterdir, e.__class__.__name__, e)
            mod = None
        finally:
            sys.path = oldsyspath

        # then, check if we have a precompiled filter list for this filter package.
        if mod is None and filterpackname in _filter_precompiled_cache:
            if name in _filter_precompiled_cache[filterpackname]:
                # found the module in the precompiled cache.
                mod = _filter_precompiled_cache[filterpackname]

        return mod

    # ---

    if (filterpackage is not None):
        # try to open module from a specific filter package
        if (isinstance(filterpackage, types.ModuleType)):
            filterpackage = filterpackage.__name__
        if filterpackage not in filterpath:
            raise NoSuchFilterPackage(filterpackage, fpdir=None)

        mod = get_module_in_filterpackage(filterpackage)

        if mod is None and raise_nosuchfilter:
            extrainfo = ""
            if import_errors:
                extrainfo = "\n\n" + "\n".join(import_errors) + "\n"
            raise NoSuchFilter(name, "Can't find module defining the filter" + extrainfo)

        return mod
    
    # load the filter from any filter package, or from cache.

    # already open?
    if (name in _filter_modules):
        return _filter_modules[name];

    mod = None

    logger.longdebug("Looking for filter %s in filter packages %r", name, filterpath)

    # explore filter packages
    for filterpack in filterpath.keys():
        mod = get_module_in_filterpackage(filterpack)
        if mod is not None:
            break

    if mod is None and raise_nosuchfilter:
        extrainfo = ""
        if import_errors:
            extrainfo = "\n\n" + "\n".join(import_errors) + "\n"
        raise NoSuchFilter(name, "Can't find module that defines the filter" + extrainfo);

    if mod is not None:
        # cache the module
        _filter_modules[name] = mod;

    # and return it
    return mod



_rxpysuffix = re.compile(r'\.py[co]?$')


def detect_filters(force_redetect=False):
    global _filter_list
    global _filter_package_listings
    global _filter_precompiled_cache
    global filterpath

    if (_filter_list is not None and not force_redetect):
        return _filter_list;
    

    def detect_filters_in_dir(thisdir, filterpackagename, filterpackage):
        """
        thisdir: the directory corresponding to the filter package (inside the package)
        filterpackage: the module object
        """

        global _filter_list
        global _filter_package_listings
        global filterpath

        logger.debug('looking for filters in package %r in directory %r', filterpackagename, thisdir)

        if not filterpackagename in _filter_package_listings:
            _filter_package_listings[filterpackagename] = []

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
                if (_rxpysuffix.search(fname) is None):
                    continue
                if (fname.startswith('__init__.')):
                    continue

                # deduce the module name relative to here
                modname = os.path.join(os.path.relpath(root, thisdir), fname)
                modname = _rxpysuffix.sub('', modname)
                if (startswithdotslash(modname)):
                    modname = modname[2:]
                modname = tomodname(modname)

                # is a filter module?
                m = get_module(modname, raise_nosuchfilter=False, filterpackage=filterpackage)
                if (m is None or not hasattr(m, 'bibolamazi_filter_class')):
                    continue

                # yes, _is_ a filter module.
                
                if modname not in _filter_package_listings[filterpackagename]:
                    _filter_package_listings[filterpackagename].append(modname)

                if modname not in _filter_list:
                    _filter_list.append(modname)

    # ----
    
    _filter_list = []
    _filter_package_listings = OrderedDict()

    logger.debug('Detecting filters ...')
    logger.longdebug("Filter path is %r", filterpath)

    for (filterpack, filterdir) in filterpath.iteritems():
        oldsyspath = sys.path
        try:
            if filterdir:
                sys.path = [filterdir] + sys.path
            try:
                filterpackage = importlib.import_module(filterpack);
            except ImportError as e:
                logger.warning("Can't import package %s for detecting filters: %s", filterpack, unicode(e))
                continue
            thisdir = os.path.realpath(os.path.dirname(filterpackage.__file__))
            
            detect_filters_in_dir(thisdir, filterpack, filterpackage)

            if filterpack in _filter_precompiled_cache:
                for (fname,fmod) in _filter_precompiled_cache[filterpack].iteritems():
                    if fname not in _filter_package_listings[filterpack]:
                        _filter_package_listings[filterpack].append(fname)
                    if fname not in _filter_list:
                        _filter_list.append(fname)

        finally:
            sys.path = oldsyspath

    logger.debug('Filters detected.')

    return _filter_list;

def detect_filter_package_listings():
    detect_filters()
    #print "detected filters. _filter_package_listings=%r\n" %(_filter_package_listings)
    return _filter_package_listings


def get_filter_class(name, filterpackage=None):
    
    fmodule = get_module(name, filterpackage=filterpackage);

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
            argdocdoc = (argdoc.doc.replace('%', '%%') if argdoc.doc is not None else None)
            group_filter.add_argument('--'+fopt, action='store', dest=farg,
                                      help=argdocdoc);
            return argdoc


        argdocs_left = [ x.argname for x in argdoclist ];
        for farg in fargs:
            # skip 'self'
            if (farg == 'self'):
                continue
            # normalize name
            argdoc = make_filter_option(farg)
            if farg in argdocs_left:
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
                                   metavar='Switch[=<value>]', exception=FilterOptionsParseErrorHintSInstead,
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
    
