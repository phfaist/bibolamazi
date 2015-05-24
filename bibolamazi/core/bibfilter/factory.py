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
import pkgutil
from collections import namedtuple, OrderedDict
import logging
import traceback

import bibolamazi.init
from bibolamazi.core.argparseactions import store_key_val, store_key_const, store_key_bool
from bibolamazi.core import butils

logger = logging.getLogger(__name__)



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



# list of packages providing bibolamazi filters. `bibolamazi.filters` is the core
# bibolamazi filters package. The value is the path to add when looking for the package,
# or None to add no path.
filterpath = PrependOrderedDict([
    ('bibolamazi.filters', None,),
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
    
    logger.debug("Loading precompiled filter list for '%s': %r", filterpackage, precompiled_modules)

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
        
        def deal_with_import_error(import_errors, name, filterpackname, filterdir, exctypestr, e,
                                   fmt_exc='', is_caused_by_module=True):
            if fmt_exc:
                fmt_exc = '\n > ' + fmt_exc.replace('\n', '\n > ')
            if is_caused_by_module:
                # if the module itself caused the error, we'll report it as a
                # warning. This is really useful for filter developers.
                logger.warning("Failed to import module `%s' from package %s%s:\n ! %s: %s%s\n",
                               name, filterpackname, dirstradd(filterdir), e.__class__.__name__,
                               unicode(e), fmt_exc)
            # and log the error for if, at the end, filter loading failed everywhere:
            # useful as additional information for debugging.
            import_errors.append(u"Attempt failed to import module `%s' in package `%s'%s.\n ! %s: %s"
                                 %(name, filterpackname, dirstradd(filterdir), exctypestr,
                                   unicode(e)))
            
        # first, search the actual module.
        oldsyspath = sys.path
        filterdir = filterpath[filterpackname]
        if filterdir:
            sys.path = [filterdir] + sys.path
        try:
            mod = importlib.import_module('.'+name, package=filterpackname);
        except ImportError:
            exc_type, exc_value, tb_root = sys.exc_info()

            logger.debug("Failed to import module `%s' from package %s%s: %s: %s",
                         name, filterpackname, dirstradd(filterdir), unicode(exc_type.__name__), unicode(exc_value))
            logger.debug("sys.path was: %r", sys.path)

            # Attempt to understand whether the ImportError was due to a missing module
            # (e.g. invalid module name), or if the module was found but the code had an
            # invalid import statement. For that, see hack at:
            # http://lucumr.pocoo.org/2011/9/21/python-import-blackbox/
            caused_by_module = True
            logger.longdebug("[was caused by module?] will inspect stack frames:\n%s",
                             "".join(traceback.format_tb(tb_root)))
            tb1 = traceback.extract_tb(tb_root)[-1]
            logger.longdebug("tb1 = %r", tb1)
            if re.search(r'\bimportlib(?:[/.]__init__[^/]{0,4})?$', tb1[0]): # or:  tb1[2] == 'import_module':
                caused_by_module = False
            ##tb_last_frame_mod_name = tb.tb_frame.f_globals.get('__name__')
            ##if tb_last_frame_mod_name == 'importlib':
            ##    # it is importlib that raised the exception, not the filter module
            ##    caused_by_module = False
            #tb = tb_root
            #while tb is not None:
            #    tb_frame_mod_name = tb.tb_frame.f_globals.get('__name__')
            #    logger.longdebug("[was caused by module?] checking frame: __name__ is %s", tb_frame_mod_name)
            #    if tb_frame_mod_name == (filterpackname+'.'+name):
            #        caused_by_module = True
            #        break
            #    tb = tb.tb_next

            # and so, now deal with the exception. Maybe log a warning for the user in
            # case the module has an erroneous import statement.
            deal_with_import_error(import_errors=import_errors, name=name, filterpackname=filterpackname,
                                   filterdir=filterdir, exctypestr=exc_type.__name__, e=exc_value,
                                   fmt_exc="".join(traceback.format_exception(exc_type, exc_value, tb_root, 5)),
                                   is_caused_by_module=caused_by_module)
            mod = None
        except Exception as e:
            exc_type, exc_value, tb_root = sys.exc_info()
            deal_with_import_error(import_errors=import_errors, name=name, filterpackname=filterpackname,
                                   filterdir=filterdir, exctypestr=exc_type.__name__, e=exc_value,
                                   fmt_exc="".join(traceback.format_exception(exc_type, exc_value, tb_root, 5)),
                                   is_caused_by_module=True)
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
    

    def detect_filters_in_module(filterpackage, filterpackname):
        """
        Explores the module `filterpackage` (to which one refers by the name `filterpackname`)
        for available filters.
        """

        global _filter_list
        global _filter_package_listings
        global filterpath

        logger.debug('looking for filters in package %r (%s) in %s',
                     filterpackage, filterpackname, filterpackage.__path__)

        if not filterpackname in _filter_package_listings:
            _filter_package_listings[filterpackname] = []

        def ignore(x):
            logger.debug("Ignoring import error of %s", x)
            pass

        filterpackprefix = filterpackname+'.'

        for importer, modname, ispkg in pkgutil.walk_packages(path=filterpackage.__path__,
                                                              prefix=filterpackprefix,
                                                              onerror=ignore):
            logger.longdebug("Recursively exploring package %s: Found submodule %s (is a package: %s)",
                             filterpackname, modname, ispkg)

            if not modname.startswith(filterpackprefix):
                logger.debug("found module '%s' which doesn't begin with '%s' -- seems to happen e.g. for packages...",
                               modname, filterpackprefix)
            else:
                # just the module name, relative to the filter package
                modname = modname[len(filterpackprefix):]

            ## seems the module needs to be imported for recursive walk to work...
            #try:
            #    mjunk = importer.find_module(module_name).load_module(module_name)
            #except Exception as e:
            #    # ignore exception -- e.g. syntax error in py -- let get_module() re-capture it
            #    pass

            # is a filter module? -- re-load with get_module() for proper handling of import errors
            m = get_module(modname, raise_nosuchfilter=False, filterpackage=filterpackage)
            if (m is None or not hasattr(m, 'bibolamazi_filter_class')):
                logger.longdebug("Module %s: failed to load or doesn't have bibolamazi_filter_class()", modname)
                continue

            # yes, _is_ a filter module.
            if modname not in _filter_package_listings[filterpackname]:
                _filter_package_listings[filterpackname].append(modname)

            if modname not in _filter_list:
                _filter_list.append(modname)

    # ----
    
    _filter_list = []
    _filter_package_listings = OrderedDict()

    logger.debug("Detecting filters ... filter path is %r", filterpath)

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
            #thisdir = os.path.realpath(os.path.dirname(filterpackage.__file__))
            detect_filters_in_module(filterpackage, filterpack)

            if filterpack in _filter_precompiled_cache:
                logger.longdebug("Loading precompiled filters from package %s...", filterpack)
                for (fname,fmod) in _filter_precompiled_cache[filterpack].iteritems():
                    logger.longdebug("\tfname=%s, fmod=%r", fname, fmod)
                    if fname not in _filter_package_listings[filterpack]:
                        _filter_package_listings[filterpack].append(fname)
                    if fname not in _filter_list:
                        _filter_list.append(fname)

        finally:
            sys.path = oldsyspath

    logger.debug('Filters detected.')
    logger.longdebug("_filter_list=%r, _filter_package_listings=%r", _filter_list, _filter_package_listings)

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

    logger.debug(name + u': calling fclass('+','.join([repr(x) for x in pargs])+', '+
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
        self.fclass_arg_defs = inspect.getargspec(fclass.__init__)
        (fargs, varargs, keywords, defaults) = self.fclass_arg_defs

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
            # just format whitespace, don't fill. This is for the GUI. we'll fill to a
            # certain width only when specifying this as the argparse help argument.
            docstr = textwrap.TextWrapper(width=sys.maxint, replace_whitespace=True, drop_whitespace=True).fill(docstr)
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
                                 epilog=_add_epilog,
                                 add_help=False,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 );

        group_filter = p.add_argument_group('Filter Arguments');

        # add option for all arguments

        # memo for later, whether to show info about boolean args in help text. Wrap this
        # in a class so that we can access this from member functions.
        class Store:
            pass
        ns = Store()
        ns.has_a_boolean_arg = False
        ns.seen_types = []

        self._filteroptions = []
        self._filtervaroptions = []

        def make_filter_option(farg):
            fopt = farg.replace('_', '-');
            argdoc = argdocs.get(farg, _ArgDoc(farg,None,None))
            if argdoc.doc is not None:
                argdocdoc = argdoc.doc.replace('%', '%%')
                argdocdoc = textwrap.TextWrapper(width=80, replace_whitespace=True, drop_whitespace=True).fill(
                    argdocdoc
                    )
            else:
                argdocdoc = None
            optkwargs = {
                'action': 'store',
                'dest': farg,
                'help': argdocdoc,
                }
            if argdoc.argtypename == 'bool':
                # boolean switch
                optkwargs['metavar'] = '<BOOLEAN ARG>'
                if not fopt.startswith('no-'):
                    optkwargs['help'] = '' # only provide help for second option
                group_filter.add_argument('--'+fopt, nargs='?', default=None, const=True,
                                          type=butils.getbool, **optkwargs)
                if not fopt.startswith('no-'):
                    optkwargs['help'] = argdocdoc # only provide help for second option
                    group_filter.add_argument('--no-'+fopt, nargs='?', default=None, const=False,
                                              type=lambda val: not butils.getbool(val), **optkwargs)
                # remember that we've seen a bool arg
                ns.has_a_boolean_arg = True
            else:
                if argdoc.argtypename:
                    if (argdoc.argtypename not in ns.seen_types):
                        ns.seen_types.append(argdoc.argtypename)
                    optkwargs['metavar'] = '<%s>'%(argdoc.argtypename)
                else:
                    optkwargs['metavar'] = '<ARG>'
                group_filter.add_argument('--'+fopt, **optkwargs)
            return argdoc


        argdocs_left = [ x.argname for x in argdoclist ];
        for n in xrange(len(fargs)):
            if n == 0: # Skip 'self' argument. Don't use "farg == 'self'" because in
                       # theory the argument could have any name.
                continue
            farg = fargs[n]
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

        group_general = p.add_argument_group('Alternative Option Syntax')

        # a la ghostscript: -sOutputFile=blahblah -sKey=Value
        group_general.add_argument('-s', action=store_key_val, dest='_s_args', metavar='Key=Value',
                                   exception=FilterOptionsParseError,
                                   help="-sKey=Value sets parameter values");
        group_general.add_argument('-d', action=store_key_bool, const=True, dest='_d_args',
                                   metavar='Switch[=<value>]', exception=FilterOptionsParseErrorHintSInstead,
                                   help="-dSwitch[=<value>] sets flag `Switch' to given boolean value, by default "
                                   "True. Valid boolean values are 1/T[rue]/Y[es]/On and 0/F[alse]/N[o]/Off");

        # allow also to give arguments without the keywords.
        if varargs:
            group_general.add_argument('_args', nargs='*', metavar='<arg>',
                                       help="Additional arguments will be passed as is to the filter--see "
                                       "documentation below");

        #p.add_argument_group(u"Python filter syntax",
        #                     textwrap.fill(fclasssyntaxdesc, width=80, subsequent_indent='        '));

        filter_options_syntax_help = textwrap.dedent(
            u"""\
            For passing option values, you may use either the `--key value' syntax, or the
            (ghostscript-like) `-sKey=Value' syntax. For boolean switches, use -dSwitch to
            set the given option to True. When using the -s or -d syntax, the option names
            are camel-cased, i.e. an option like `--add-description arxiv' can be
            specified as `-sAddDescription=arxiv'. Likewise, `--preserve-ids' can provided
            as `-dPreserveIds' or `-dPreserveIds=yes'.""")

        if ns.has_a_boolean_arg:
            filter_options_syntax_help += textwrap.dedent(u"""

            The argument to options which accept a <BOOLEAN ARG> may be omitted. <BOOL
            ARG> may be one of ("t", "true", "y", "yes", "1", "on") to activate the
            switch, or ("f", "false", "n", "no", "0", "off") to disable it (case
            insensitive). If you specify a false argument to the variant '--no-<SWITCH>'
            of the option, that argument negates the negative effect of the switch.""")

        for (typname, typ) in ((y, x) for (y, x) in
                               ((y, butils.resolve_type(y, self._fmodule)) for y in ns.seen_types)
                               if hasattr(x, '__doc__')):
            if not typ.__doc__: # e.g., is None
                continue
            docstr = typ.__doc__.strip()
            if not len(docstr):
                continue
            docstr = textwrap.TextWrapper(width=80, replace_whitespace=True, drop_whitespace=True,
                                          subsequent_indent='    ').fill(
                "TYPE %s: "%(typname) + docstr
            )
            filter_options_syntax_help += "\n\n" + docstr

        if varargs:
            filter_options_syntax_help += textwrap.dedent(u"""

            This filter accepts additional positional arguments. See the documentation
            below for more information.""")

        p.add_argument_group(u'Note on Filter Options Syntax', filter_options_syntax_help)

        p.add_argument_group(u'FILTER DESCRIPTION', "\n" + fclass.getHelpText())


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


    def parse_optionstring_to_optspec(self, optionstring):
        """
        Parses the optionstring, and returns a description of which options where
        specified, which which values.

        This doesn't go as far as :py:meth:`parse_optionstring()`, which returns pretty
        much exactly how to call the filter constructor. This function is meant for
        example for the GUI, who needs to parse what the user specified, and not
        necessarily how to construct the filter itself.

        Return a dictionary::

            {
              "_args": <additional *pargs positional arguments>
              "kwargs": <keyword arguments>
            }

        The value of ``_args`` is either `None`, or a list of additional positional
        arguments if the filter accepts `*args` (and hence the option parser too). These
        will only be passed to `*args` and NOT be distributed to the declared arguments of
        the filter constructor.

        The value of ``kwargs`` is a dictionary of all options specified by keywords,
        either with the ``--keyword=value`` syntax or with the syntax ``-sKey=Value``. The
        corresponding value is converted to the type the filter expects, in each case
        whenever possible (i.e. documented by the filter).
        """
        
        logger.debug("parse_optionstring: "+self._filtername+"; fclass="+repr(self._fclass)
                     +"; optionstring="+optionstring);

        p = self._parser

        (fargs, varargs, keywords, defaults) = self.fclass_arg_defs
        if defaults is None:
            defaults = []

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

        optspec = {
            '_args': None,
            'kwargs': {}
            }

        if varargs:
            optspec['_args'] = []

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
                kwargs[argname] = argval # raw type if we can't figure one out (could be
                                         # extra kwargs argument, or not documented)

        for (arg, argval) in dargs.iteritems():
            if (varargs and arg == '_args'):
                optspec['_args'] = argval;
                continue
            if (arg == '_d_args' and argval is not None):
                # get all the defined args
                for (thekey, theval) in argval:
                    # store this definition
                    therealkey = self.getArgNameFromSOpt(thekey);
                    optspec['kwargs'][therealkey] = theval

                    logger.debug("Set switch `%s' to %s" %(thekey, "True" if theval else "False"))

                continue

            if (arg == '_s_args' and argval is not None):
                # get all the set args
                for (key, v) in argval:
                    thekey = self.getArgNameFromSOpt(key);
                    set_kw_arg(optspec['kwargs'], thekey, v)

                    logger.debug("Set option `%s' to `%s'" %(thekey, v))

                continue

            if (argval is None):
                continue

            set_kw_arg(optspec['kwargs'], arg, argval)

        return optspec


    def parse_optionstring(self, optionstring):
        """
        Parse the given option string (one raw string, which may contain quotes, escapes
        etc.) into arguments which can be directly provided to the filter constructor.
        """

        optspec = self.parse_optionstring_to_optspec(optionstring)

        (fargs, varargs, keywords, defaults) = self.fclass_arg_defs
        if defaults is None:
            defaults = []

        pargs = optspec["_args"]
        kwargs = optspec["kwargs"]

        if pargs is None:
            pargs = []

        # The following bit of code is only important for filters with varargs. However to
        # uniformize behavior (and error messages), we'll do this for all filters (there
        # should be no harm for non-varargs filters).
        #
        #if varargs:
        #
        # if we have varargs, make sure we provide a value for all declared parameters. We
        # want to forbid *pargs to fill the declared parameters of the filter constructor,
        # because it's confusing for the user. The *pargs should only be captured in the
        # filter's explicit *args argument. So we need to pass all declared arguments as
        # positional arguments.
        #
        # This is the index of first argument with a default value. See
        # https://docs.python.org/2/library/inspect.html#inspect.getargspec
        n_deflts_offset = len(fargs)-len(defaults)
        #
        fdeclpargs = []
        for n in xrange(len(fargs)):
            if n == 0: # Skip 'self' argument. Don't use "farg == 'self'" because in
                       # theory the argument could have any name.
                continue
            farg = fargs[n]
            if farg in kwargs:
                fdeclpargs.append(kwargs.pop(farg))
            else:
                # add explicit default argument for this farg, if any, or report error
                # if no value given.
                if n < n_deflts_offset:
                    raise FilterOptionsParseError("No value provided for mandatory option `%s'"%(farg),
                                                  self._filtername)
                defaultval = defaults[n - n_deflts_offset]
                logger.longdebug("filter %s: adding argument #%d with default value %s=%r", self._filtername,
                                 n, farg, defaultval)
                fdeclpargs.append(defaultval)
        # ensure that all filter-declared arguments have values, then add all remaining args for *args.
        pargs = fdeclpargs + pargs
                    
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
    
