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

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr
from future.standard_library import install_aliases
install_aliases()
import sys
def to_native_str(x): return x.encode('utf-8') if sys.version_info[0] <= 2 else x
def from_native_str(x): return x.decode('utf-8') if sys.version_info[0] <= 2 else x


import sys
import importlib
import re
import os
import os.path
import shlex
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
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibfilter import BibFilter


logger = logging.getLogger(__name__)


import inspect
inspect_getargspec = inspect.getargspec if sys.version_info[0] <= 2 else lambda f: inspect.getfullargspec(f)[:4]



if sys.hexversion < 0x03060000:
    # Python < 3.6 doesn't have ModuleNotFoundError -- define dummy class here;
    # the ImportError branch will be picked up anyway
    class ModuleNotFoundError(Exception):
        pass




# some exception classes.

class NoSuchFilter(Exception):
    """
    Signifies that the requested filter was not found.  See also
    :py:class:`FilterInfo`.
    """
    def __init__(self, fname, errorstr=None):
        super(NoSuchFilter, self).__init__("No such filter or import error: "+fname+
                                           (": "+errorstr if errorstr else ""))

class ModuleNotAValidFilter(NoSuchFilter):
    """
    Signifies that a given module does not expose a valid bibolamazi filter.
    See also :py:class:`FilterInfo`.
    """
    def __init__(self, fname, errorstr=None):
        super(ModuleNotAValidFilter, self).__init__(fname, errorstr)

class NoSuchFilterPackage(Exception):
    """
    Signifies that the requested filter package was not found.  See also
    :py:class:`FilterInfo`.
    """
    def __init__(self, fpname, errorstr="No such filter package", fpdir=None):
        super(NoSuchFilterPackage, self).__init__("No such filter package or import error: `"+ fpname + "'"
                                                  + (" (dir=`%s')"%(fpdir) if fpdir is not None else "")
                                                  + (": "+errorstr if errorstr else ""))
        

@python_2_unicode_compatible
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
        self.name = name
        self.errorstr = errorstr
        super(FilterError, self).__init__(unicodestr(self))

    def setName(self, name):
        self.name = name

    def fmt(self, name):
        return "Filter %s: %s" %(name, self.errorstr)

    def __str__(self):
        name = ( "`%s'" %(self.name) if self.name else "<unknown>" )
        return self.fmt(name)
    

class FilterOptionsParseError(FilterError):
    """
    Raised when there was an error parsing the option string provided by the user.
    """
    def fmt(self, name):
        return "Can't parse options for filter %s: %s" %(name, self.errorstr)


class FilterOptionsParseErrorHintSInstead(FilterOptionsParseError):
    """
    As `FilterOptionsParseError`, but hinting that maybe ``-sOption=Value`` was meant
    instead of ``-dOption=Value``.
    """
    def fmt(self, name):
        return (super(FilterOptionsParseErrorHintSInstead, self).fmt(name)
                + " (was -sKEY=VAL meant instead of -dKEY=VAL?)")


class FilterCreateError(FilterError):
    """
    There was an error instantiating the filter. This could be due to the filter
    constructor itself raising an exception.
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
            ourself = list(self.items())
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
            items = list(self.items())
            self.clear()
            self.update(items[:idx] + [ (key, value) ] + items[idx+1:])
        finally:
            self.isupdating = False

    def item_at(self, idx):
        return list(self.items())[idx]



# list of packages providing bibolamazi filters. `bibolamazi.filters` is the core
# bibolamazi filters package. The value is the path to add when looking for the package,
# or None to add no path.
filterpath = PrependOrderedDict([
    ('bibolamazi.filters', None,),
    ])




# information about filters and modules etc.


# _filter_package_listings is an OrderedDict() when initialized
# _filter_package_listings[(fpkgname,fpkgdir)] = [finfo1, finfo2, ...]  list of FilterInfo objects
_filter_package_listings = None

# _filter_modules[(fpkgname,fpkgdir)][filtername] = fmodule
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
    global _filter_package_listings
    global _filter_modules
    global _filter_precompiled_cache

    _filter_package_listings = None
    _filter_modules = {}
    # of course, don't reset the precompiled cache!!



def parse_filterpackage_argstr(argstr):
    """
    Parse filter package specification given as
    \"filterpackage=path/to/the/package\" or \"filterpackage=\" or
    \"path/to/the/package\"
    """

    if not argstr:
        raise BibolamaziError("Invalid filter package: No filter package specified")

    fpparts = argstr.split('=',1)
    if len(fpparts) == 1:
        path = fpparts[0].strip()
        fpname = os.path.basename(path)
        fpdir = os.path.dirname(path)
    else:
        fpname = fpparts[0].strip()
        fpdir = fpparts[1].strip() if len(fpparts) >= 2 and fpparts[1] else None

    if not fpdir:
        # e.g., built-in filters must have None as fpdir because they don't
        # reside at a specific location.  Note that when loading filters, we
        # will also check the '.' directory
        fpdir = None


    if not fpname or re.search(r'[^a-zA-Z0-9_\.]', fpname):
        raise BibolamaziError("Invalid filter package: '%s': not a valid python identifier. "
                              "Did you get the filterpackage syntax wrong? "
                              "Syntax: '<packagename>[=<path>]' or 'path/to/packagename'."
                              %(fpname))

    return (fpname, fpdir)


def _syspath_for_fpkgdir(fpkgdir, oldpath):
    return ([fpkgdir] if fpkgdir else []) + oldpath + ['.']


def validate_filter_package(fpname, fpdir, raise_exception=True):
    """
    Make sure given filter package at given directory is valid.

    Utility to warn the user of invalid `--filterpackage` option
    """

    oldsyspath = sys.path
    mod = None
    sys.path = _syspath_for_fpkgdir(fpdir, sys.path)
    try:
        mod = importlib.import_module(fpname)
    except (ImportError,TypeError):  # raises TypeError if fpname is '.modulename'
        if raise_exception:
            raise NoSuchFilterPackage(fpname, fpdir=fpdir)
        return False
    finally:
        sys.path = oldsyspath

    if mod:
        return True

    return False


def _setup_imported_filter_module(mod, fpn, fpd):
    setattr(mod, '_filterpackageinfo', (fpn, fpd,))


def _get_filter_module(name, fpkgname=None, filterpath=filterpath):

    #
    # NOTE: Module gets an additional attribute '_filterpackageinfo' with a
    # tuple (fpname, fpdir) corresponding to the filterpath element where the
    # filter module was found.
    #

    name = str(name)

    logger.longdebug("get_filter_module(name=%r, fpkgname=%r, filter_path=%r)",
                     name, fpkgname, filterpath)

    if not re.match(r'^[.\w]+$', name):
        raise ValueError("Filter name may only contain alphanum chars and dots (got %r)"%(name))

    import_errors = []


    def get_module_in_filterpackage(fpn, fpd):

        global _filter_precompiled_cache
        
        logger.longdebug("Attempting to load filter %s from package %s", name, fpn)

        mod = None

        def dirstradd(fpd):
            return " (dir `%s')"%(fpd) if fpd else ""
        
        def deal_with_import_error(import_errors, name, fpn, fpd, exctypestr, e,
                                   tb_info, is_caused_by_module=True):
            fmt_exc = ''
            if tb_info:
                # print traceback, but try to remove all the stack frames that
                # concern bibolamazi and python importlib internals (to shorten
                # output, and focus the stack trace on the filter's code)
                last_importlib_frame = -1
                exc_type, exc_value, tb = tb_info
                rximportlib = re.compile(r'\bimportlib\b')
                extracted_tb = traceback.extract_tb(tb)
                for i, t in enumerate(extracted_tb):
                    if rximportlib.search(t[0]):
                        last_importlib_frame = i
                fmt_exc = "".join(traceback.format_list(extracted_tb[last_importlib_frame+1:])).strip()
                if fmt_exc:
                    fmt_exc = '\n > ' + fmt_exc.replace('\n', '\n > ')
            logger.debug("Module import failed.", exc_info=tb_info)

            if is_caused_by_module:
                # if the module itself caused the error, we'll report it as a
                # warning. This is really useful for filter developers.
                logger.warning("Failed to import module `%s' from package %s%s:\n ! %s: %s%s\n",
                               name, fpn, dirstradd(fpd), e.__class__.__name__,
                               unicodestr(e), fmt_exc)
            # and log the error for if, at the end, filter loading failed everywhere:
            # useful as additional information for debugging.
            import_errors.append(u"Attempt failed to import module `%s' in package `%s'%s.\n ! %s: %s"
                                 %(name, fpn, dirstradd(fpd), exctypestr,
                                   unicodestr(e)))
            
        # first, search the actual module.
        oldsyspath = sys.path
        sys.path = _syspath_for_fpkgdir(fpd, sys.path)
        try:
            logger.longdebug("Attempting to import filter package `%s`"%(fpn))
            fpmod = importlib.import_module(fpn)
            logger.longdebug("Attempting to import module `%s` from package `%s`"%('.'+name, fpn))
            mod = importlib.import_module('.'+name, package=fpn)
            _setup_imported_filter_module(mod, fpn, fpd)
        except ModuleNotFoundError:
            exc_type, exc_value, tb_root = sys.exc_info()

            logger.debug("Failed to import module `%s' from package %s%s: %s: %s",
                         name, fpn, dirstradd(fpd), unicodestr(exc_type.__name__),
                         unicodestr(exc_value))
            logger.debug("sys.path was: %r", sys.path)
            
            deal_with_import_error(import_errors=import_errors, name=name, fpn=fpn,
                                   fpd=fpd, exctypestr=exc_type.__name__, e=exc_value,
                                   tb_info=(exc_type, exc_value, tb_root),
                                   is_caused_by_module=False)
            mod = None
        except ImportError:
            exc_type, exc_value, tb_root = sys.exc_info()

            logger.debug("Failed to import module `%s' from package %s%s: %s: %s",
                         name, fpn, dirstradd(fpd), unicodestr(exc_type.__name__),
                         unicodestr(exc_value))
            logger.debug("sys.path was: %r", sys.path)

            # On Python 2 and Python < 3.6, attempt to understand whether the
            # ImportError was due to a missing module (e.g. invalid module
            # name), or if the module was found but the code had an invalid
            # import statement. For that, see hack at:
            # http://lucumr.pocoo.org/2011/9/21/python-import-blackbox/
            caused_by_module = True
            logger.longdebug("[was caused by module?] will inspect stack frames:\n%s",
                             "".join(traceback.format_tb(tb_root)))
            tb1 = traceback.extract_tb(tb_root)[-1]
            logger.longdebug("tb1 = %r", tb1)
            if re.search(r'\bimportlib(?:[/.]__init__[^/]{0,4})?(?:[.]py)?$', tb1[0]):
                # alternatively, we could have used:  tb1[2] == 'import_module'
                caused_by_module = False
                logger.longdebug("ImportError was not caused by the module. The module was not found.")

            # and so, now deal with the exception. Maybe log a warning for the user in
            # case the module has an erroneous import statement.
            deal_with_import_error(import_errors=import_errors, name=name, fpn=fpn,
                                   fpd=fpd, exctypestr=exc_type.__name__, e=exc_value,
                                   tb_info=(exc_type, exc_value, tb_root),
                                   is_caused_by_module=caused_by_module)
            mod = None
        except Exception as e:
            exc_type, exc_value, tb_root = sys.exc_info()
            deal_with_import_error(import_errors=import_errors, name=name, fpn=fpn,
                                   fpd=fpd, exctypestr=exc_type.__name__, e=exc_value,
                                   tb_info=(exc_type, exc_value, tb_root),
                                   is_caused_by_module=True)
            mod = None
        finally:
            sys.path = oldsyspath

        # then, check if we have a precompiled filter list for this filter package.
        if mod is None and fpn in _filter_precompiled_cache and not fpd:
            if name in _filter_precompiled_cache[fpn]:
                # found the module in the precompiled cache.
                mod = _filter_precompiled_cache[fpn]

        return mod

    # ---

    if (fpkgname is not None):
        # try to open module from a specific filter package

        if fpkgname not in filterpath:
            raise NoSuchFilterPackage(fpkgname, fpdir=None)

        # already open? Note: only look in those packages in our filterpath
        for fpkgd in (fd for fn,fd in iteritems(filterpath) if fn == fpkgname):
            if (fpkgname,fpkgd) in _filter_modules and name in _filter_modules[(fpkgname,fpkgd)]:
                return _filter_modules[(fpkgname,fpkgd)][name]

        mod = get_module_in_filterpackage(fpkgname, filterpath[fpkgname])

        if mod is None:
            extrainfo = ""
            if import_errors:
                extrainfo = "\n\n" + "\n".join(import_errors) + "\n"
            raise NoSuchFilter(name, "Can't find module defining the filter" + extrainfo)

        # cache the module
        _junk, fpkgdir = getattr(mod, '_filterpackageinfo')

        if (fpkgname,fpkgdir) not in _filter_modules:
            _filter_modules[(fpkgname,fpkgdir)] = {}
        _filter_modules[(fpkgname,fpkgdir)][name] = mod

        return mod
    
    # load the filter from any filter package, or from cache.

    # already open? Note: only look in those packages in our filterpath
    for fpkgn,fpkgd in iteritems(filterpath):
        if (fpkgn,fpkgd) in _filter_modules and name in _filter_modules[(fpkgn,fpkgd)]:
            return _filter_modules[(fpkgn,fpkgd)][name]

    mod = None

    logger.longdebug("Looking for filter %s in filter packages %r", name, filterpath)

    # explore filter packages
    for filterpack in filterpath.keys():
        mod = get_module_in_filterpackage(filterpack, filterpath[filterpack])
        if mod is not None:
            break

    if mod is None:
        extrainfo = ""
        if import_errors:
            extrainfo = "\n\n" + "\n".join(import_errors) + "\n"
        raise NoSuchFilter(name, "Can't find module that defines the filter" + extrainfo)

    if mod is not None:
        # cache the module
        fpkgname, fpkgdir = getattr(mod, '_filterpackageinfo')

        if (fpkgname,fpkgdir) not in _filter_modules:
            _filter_modules[(fpkgname,fpkgdir)] = {}
        _filter_modules[(fpkgname,fpkgdir)][name] = mod

    # and return it
    return mod



_rxpysuffix = re.compile(r'\.py[co]?$')


def detect_filter_package_listings(force_redetect=False, filterpath=filterpath):

    global _filter_package_listings
    global _filter_precompiled_cache

    def detect_filters_in_package(fpkgmod, fpkgname, fpkgdir):
        """
        Explores the given filter package and collects filter listings
        """

        global _filter_package_listings

        logger.debug('looking for filters in package %r (%s) in %s', fpkgmod, fpkgname, fpkgdir)

        if (fpkgname,fpkgdir) not in _filter_package_listings:
            _filter_package_listings[(fpkgname,fpkgdir)] = []

        def ignore(x):
            logger.debug("Ignoring import error of %s", x)
            pass

        filterpackprefix = fpkgname+'.'

        for loader, modname, ispkg in pkgutil.walk_packages(path=fpkgmod.__path__,
                                                            prefix=filterpackprefix,
                                                            onerror=ignore):
            logger.longdebug("Recursively exploring package %s: Found submodule %s (is a package: %s)",
                             fpkgname, modname, ispkg)

            if not modname.startswith(filterpackprefix):
                logger.debug("found module '%s' which doesn't begin with '%s' -- seems to happen e.g. for packages...",
                             modname, filterpackprefix)
                filtername = None
            else:
                # just the module name, relative to the filter package
                filtername = modname[len(filterpackprefix):]

            try:
                module_obj = loader.find_module(modname).load_module(modname)
            except Exception:
                logger.debug("Failed to load module %s", modname)
                continue

            _setup_imported_filter_module(module_obj, fpkgname, fpkgdir)

            # is a filter module? -- re-load with get_module() for proper handling of import errors
            try:
                finfo = FilterInfo.initFromModuleObject(filtername, module_obj, fpkgname=fpkgname, fpkgdir=fpkgdir)
            except NoSuchFilter:
                logger.debug("Module %s: failed to load", modname)
                continue
            except NoSuchFilterPackage:
                logger.debug("Module %s: invalid filter package %s (!?!?)", modname, fpkgname)
                continue
            except ModuleNotAValidFilter:
                logger.debug("Module %s does not define a valid bibolamazi filter", modname)
                continue

            # yes, _is_ a filter module.
            _filter_package_listings[(fpkgname,fpkgdir)].append(finfo)

    # ----
    
    logger.debug("detect_filter_package_listings(force_redetect=%r, filterpath=%r)", force_redetect, filterpath)

    if not _filter_package_listings or force_redetect:
        _filter_package_listings = OrderedDict()

    for (fpkgname, fpkgdir) in iteritems(filterpath):

        if (fpkgname,fpkgdir) in _filter_package_listings:
            # don't need to re-detect. (If force_redetect was set, then we have
            # already cleared the corresponding entry)
            continue

        oldsyspath = sys.path
        sys.path = _syspath_for_fpkgdir(fpkgdir, sys.path)
        try:
            fpkgmod = None
            try:
                fpkgmod = importlib.import_module(fpkgname)
            except ImportError as e:
                logger.warning("Can't import package %s for detecting filters: %s", fpkgname, unicodestr(e))
                continue

            if fpkgmod is not None:
                detect_filters_in_package(fpkgmod, fpkgname, fpkgdir)

        finally:
            sys.path = oldsyspath

        if fpkgname in _filter_precompiled_cache:
            if (fpkgname,None) not in _filter_package_listings:
                _filter_package_listings[(fpkgname,None)] = []

            logger.longdebug("Loading precompiled filters from package %s...", fpkgname)
            for (fname,fmod) in iteritems(_filter_precompiled_cache[fpkgname]):
                logger.longdebug("\tfname=%s, fmod=%r", fname, fmod)
                try:
                    finfo = FilterInfo.initFromModuleObject(fname, fmod, fpkgname=fpkgname, fpkgdir=None)
                except Exception:
                    logger.debug("Precompiled module %s failed to load!", modname)
                    continue
                _filter_package_listings[(fpkgname,None)].append(finfo)


    logger.debug("detect_filter_package_listings(): Filters detected.  _filter_package_listings=%r",
                 _filter_package_listings)

    # now, return a nicer OrderedDict with filter names instead of full fpkgspec
    # keys, keeping only those packages that are accessible in filterpath.
    listing = OrderedDict()
    for (fpkgname, fpkgdir) in iteritems(filterpath):
        if (fpkgname, fpkgdir) not in _filter_package_listings:
            continue
        if fpkgname not in listing:
            listing[fpkgname] = []

        for filterinfo in _filter_package_listings[(fpkgname, fpkgdir)]:
            listing[fpkgname].append(filterinfo)

    return listing

def detect_filters(force_redetect=False, filterpath=filterpath):

    logger.debug("detect_filters(force_redetect=%r, filterpath=%r)"%(force_redetect, filterpath))

    detect_filter_package_listings(force_redetect=force_redetect, filterpath=filterpath)

    # flatten _filter_package_listings list

    # now collect filter names
    filter_list = []
    for (fpkgname, fpkgdir) in iteritems(filterpath):

        if (fpkgname, fpkgdir) not in _filter_package_listings:
            continue

        for finfo in _filter_package_listings[(fpkgname,fpkgdir)]:
            filter_list.append(finfo)

    logger.longdebug("filter_list=%r, _filter_package_listings=%r", filter_list, _filter_package_listings)

    return filter_list



_simple_filter_class_template = """\
from bibolamazi.core.bibfilter import BibFilter

# in case fn's default argument values refer to custom types in that module
from {fmodulename} import *

import sys

import logging
logger = logging.getLogger("filter." + "{filtername}")

class simplefilter_{filtername}(BibFilter):

    helpauthor = {filter_help_author}
    helpdescription = {filter_help_description}
    helptext = {filter_fn_doc_str}

    def __init__(self, {init_signature}):
        {init_fields_doc_str}
        
        super(simplefilter_{filtername}, self).__init__()

        self.kwargs = dict({init_kwargs_set_dict})

        logger.debug('Instantiated {filtername} instance with arguments %r', self.kwargs)

    def getRunningMessage(self):
        return "running filter {filtername}"

    def action(self):
        return {bib_filter_action_type}

    def requested_cache_accessors(self):
        return []

    def filter_bibolamazifile(self, bibolamazifile):
        # in case we are filtering a bibolamazifile
        sys.modules["{fmodulename}"].bib_filter_bibolamazifile(bibolamazifile=bibolamazifile, **self.kwargs)

    def filter_bibentry(self, entry):
        # in case we are filtering a single entry
        fn = sys.modules["{fmodulename}"].bib_filter_entry
        fn(entry=entry, {entry_fn_bibolamazifile_kwarg} **self.kwargs)

"""

def _get_filter_class(name, fmodule=None):
    """
    Use :py:class:`FilterInfo`.
    """

    if hasattr(fmodule, 'bibolamazi_filter_class'):
        return fmodule.bibolamazi_filter_class()

    # other ways to define a filter -- quick-n-dirty minimal way
    is_simple_entry_filter = hasattr(fmodule, 'bib_filter_entry')
    is_simple_bibolamazifile_filter = hasattr(fmodule, 'bib_filter_bibolamazifile')
    if is_simple_entry_filter or is_simple_bibolamazifile_filter:

        if is_simple_entry_filter and is_simple_bibolamazifile_filter:
            raise ModuleNotAValidFilter(("Custom simple filter %s may not define both "
                                         "bib_filter_entry() and bib_filter_bibolamazifile().")%(name))

        # the following is highly inspired from Python's
        # collections.namedtuple() definition

        if is_simple_entry_filter:
            simple_filter_action_type = 'BibFilter.BIB_FILTER_SINGLE_ENTRY'
            simple_filter_fn = fmodule.bib_filter_entry
        elif is_simple_bibolamazifile_filter:
            simple_filter_action_type = 'BibFilter.BIB_FILTER_BIBOLAMAZIFILE'
            simple_filter_fn = fmodule.bib_filter_bibolamazifile
        else:
            raise RuntimeError("Shouldn't be here")

        # inspect the fn's signature and declare arguments for documentation
        argspec = inspect_getargspec(simple_filter_fn)
        nargs = argspec[0]
        # one value for EACH argument (first values set to None)
        argdefvals = argspec[3] if argspec[3] is not None else []
        argdefvals = [None]*(len(nargs)-len(argdefvals)) + list(argdefvals)
        init_signature_list = []
        init_kwargs_set_dict_list = []
        init_fields_doc_dict = {}
        for i in range(len(nargs)):
            if nargs[i] == 'entry':
                continue
            if nargs[i] == 'bibolamazifile':
                continue
            typname = type(argdefvals[i]).__name__
            typinfo = ''
            if typname in ['bool', 'int']:
                typinfo = typname
            init_signature_list.append('%s=%r'%(nargs[i], argdefvals[i]))
            init_kwargs_set_dict_list.append('%s=%s'%(nargs[i], nargs[i]))
            init_fields_doc_dict[nargs[i]] = _ArgDoc(argname=nargs[i],
                                                     argtypename=typinfo,
                                                     doc='<no documentation available>')

        # special case, see if the entry filter accepts bibolamazi= kw arg
        entry_fn_bibolamazifile_kwarg = ''
        if is_simple_entry_filter and 'bibolamazifile' in nargs:
            entry_fn_bibolamazifile_kwarg = 'bibolamazifile=self.bibolamaziFile(), '

        fn_docstring = textwrap.dedent(simple_filter_fn.__doc__)

        fn_argdoclist, fn_docstring_docpart = parseArgdoc(fn_docstring)
        if not fn_docstring_docpart:
            fn_docstring_docpart = '<no documentation available>'

        fn_argdocs = dict([(x.argname, x) for x in fn_argdoclist])
        init_fields_doc_dict.update(fn_argdocs)

        logger.debug("init_fields_doc_dict=%r", init_fields_doc_dict)

        fn_help_description = "<No description available>"
        fn_help_author = "<Author unknown>"

        m = re.search(r'^\s*Author\s*:\s*(?P<author>(.|(\n(?!\s*\n)))*)(\n\s*\n|\Z)', fn_docstring_docpart,
                      flags=re.MULTILINE|re.IGNORECASE)
        if m is not None:
            fn_help_author = textwrap.dedent(m.group('author').strip())
            fn_docstring_docpart = fn_docstring_docpart[:m.start()] + fn_docstring_docpart[m.end():]
        
        m = re.search(r'^\s*Description\s*:\s*(?P<description>(.|(\n(?!\s*\n)))*)(\n\s*\n|\Z)',
                      fn_docstring_docpart, flags=re.MULTILINE|re.IGNORECASE)
        if m is not None:
            fn_help_description = textwrap.dedent(m.group('description').strip())
            fn_docstring_docpart = fn_docstring_docpart[:m.start()] + fn_docstring_docpart[m.end():]
        
        # extract filter name from "pkg:filter"
        if ':' in name:
            filtername = name.split(':')[-1]
        else:
            filtername = name

        # now, format class definition source
        cls_source = _simple_filter_class_template.format(
            filtername=filtername,
            fmodulename=fmodule.__name__,
            filter_help_author=repr(fn_help_author),
            filter_help_description=repr(fn_help_description),
            filter_fn_doc_str=repr(fn_docstring_docpart.strip()),
            bib_filter_action_type=simple_filter_action_type,
            init_signature=", ".join(init_signature_list),
            init_kwargs_set_dict=", ".join(init_kwargs_set_dict_list),
            init_fields_doc_str=repr("Arguments:\n"  +  "\n".join([
                '  * ' + x.argname + ('('+x.argtypename+')' if x.argtypename else '') + ':'
                + x.doc
                for x in init_fields_doc_dict.values()
            ])),
            entry_fn_bibolamazifile_kwarg=entry_fn_bibolamazifile_kwarg
            )

        logger.longdebug("Creating simple filter class, source = \n%s", cls_source)

        # Execute the template string in a temporary namespace and support
        # tracing utilities by setting a value for frame.f_globals['__name__']
        namespace = dict(__name__='bibolamazisimplefilter_%s' % name)
        exec(cls_source, namespace)
        result = namespace['simplefilter_%s' % filtername]
        result._source = cls_source

        return result

    raise ModuleNotAValidFilter(name, "Module is not a valid filter definition")



@python_2_unicode_compatible
class FilterInfo(object):
    """
    Information about a given filter.

    Arguments:

      - `name`: the name of the filter to get information about.  It may be of
        the form 'filtername' or 'pkgname:filtername'.

      - `filterpath`: an :py:class:`collections.OrderedDict` of paths where to
        look for filters.  Keys are package names and values are the filesystem
        directory that needs to be added to `sys.path` to be able to import the
        given filter package as a Python package.

    .. note: The constructor of this class may raise :py:exc:`NoSuchFilter`,
             :py:exc:`NoSuchFilterPackage`, or :py:exc:`ModuleNotAValidFilter`,
             if a corresponding error occurs while inspecting the filter.


    .. py:attribute:: filtername

       The filter name (without any filter package information).

    .. py:attribute:: fmodule

       The module object that contains the filter.

    .. py:attribute:: fclass

       The class object that implements the filter.

       Note that simple-syntax filters are internally translated into a class
       object that fulfils the full-syntax filters API. So all filters have a
       valid class object that behaves as one would expect.

    .. py:attribute:: filterpackagename

       The name of the filter package in which this filter is located.  This
       value is always valid.  The built-in filters are in the filter package
       ``bibolamazi.filters``.

    .. py:attribute:: filterpackagedir

       The filesystem path that needs to be added to :py:attr:`sys.path` in
       order to be able to import the filter package `filterpackagename` as a
       Python package.  Note: bibolamazi assumes that `sys.path` is not being
       mischieviously manipulated by other parts of the Python code.  If the
       filter package can be loaded from Python's default path, this directory
       may not be accurate.

    .. py:attribute:: filterpackagespec

       A string of the form 'pkgname=file/system/path' that combines the
       information of `filterpackagename` and `filterpackagedir` in a single
       string.  This is a valid argument to the function
       :py:func:`parse_filterpackage_argstr()`.


    This object also exposes the following attributes, which reflect what
    arguments were given to the constructor.

    .. py:attribute:: name

       The filter name, as specified to the constructor.

    .. py:attribute:: filterpath

       The filter path specified to the constructor (or the default one), that
       was used to resolve the information to the present filter.
    
    The following methods are available for more specific filter information.
    """
    def __init__(self, name, filterpath=filterpath):

        if name is None:
            # called by some other initXXX static method -- let them continue
            return

        self.name = name
        self.filterpath = OrderedDict(filterpath)

        # shortcut: a filter name may be 'filterpackage:the.module.name' to force search in a
        # specific filter package.
        if ':' in name:
            fpkgref, self.filtername = name.split(':',1)
        else:
            self.filtername = self.name
            fpkgref = None

        self.fmodule = _get_filter_module(self.filtername, fpkgname=fpkgref, filterpath=self.filterpath)
        self.fclass = _get_filter_class(self.filtername, fmodule=self.fmodule)

        self.filterpackagename, self.filterpackagedir = getattr(self.fmodule, '_filterpackageinfo')
        self.filterpackagespec = (self.filterpackagename + '=' +
                                  (self.filterpackagedir if self.filterpackagedir else ''))

        self.uses_default_argparse = not hasattr(self.fmodule, 'parse_args')

    @staticmethod
    def initFromModuleObject(filtername, module_obj, fpkgname, fpkgdir):
        """
        Initializes a `FilterInfo` object from an already-imported module object
        `module_obj` in a given filter package with name `fpkgname` residing in
        dir `fpkgdir`.  The module name without the package information must be
        given in `filtername`.
        """

        finfo = FilterInfo(None)

        finfo.filtername = filtername
        finfo.fmodule = module_obj
        finfo.fclass = _get_filter_class(filtername, fmodule=finfo.fmodule)

        finfo.filterpackagename = fpkgname
        finfo.filterpackagedir = fpkgdir
        finfo.filterpackagespec = fpkgname + '=' + (fpkgdir if fpkgdir else '')

        finfo.uses_default_argparse = not hasattr(finfo.fmodule, 'parse_args')

        finfo.name = filtername
        finfo.filterpath = None

        return finfo

    def __str__(self):
        return "FilterInfo(filtername=%r, fpkgname=%r, fpkgdir=%r)"%(
            self.filtername, self.filterpackagename, self.filterpackagedir
        )
    def __repr__(self):
        return str(self)
        
    def parseOptionStringArgs(self, optionstring):

        pargs = []
        kwargs = {}

        if not self.uses_default_argparse:
            x = self.fmodule.parse_args(optionstring)
            try:
                (pargs, kwargs) = x
            except (TypeError, ValueError):
                raise FilterError("Filter's parse_args() didn't return a tuple (args, kwargs)",
                                  name=self.name)
        else:
            fopts = self.defaultFilterOptions()
            (pargs, kwargs) = fopts.parse_optionstring(optionstring)

        return (pargs, kwargs)

    def validateOptionStringArgs(self, pargs, kwargs):
        """
        Validate the arguments as OK to pass to constructor, i.e. that all argument
        names are correct.

        We use :py:func:`inspect.getcallargs()` to inspect the filter class
        constructor's signature.

        Raises :py:exc:`FilterCreateArgumentError` if the validation fails.
        """
        try:
            pargs2 = [None]+pargs; # extra argument for `self` slot
            inspect.getcallargs(self.fclass.__init__, *pargs2, **kwargs)
        except Exception as e:
            logger.debug("Filter exception:\n" + traceback.format_exc())
            raise FilterCreateArgumentError(unicodestr(e), self.name)
    

    def defaultFilterOptions(self):
        """
        Return a :py:class:`DefaultFilterOptions` object that is capable of standard
        filter argument parsing for this filter.

        This method returns `None` if the filter doesn't use the default
        argument parsing mechanism.
        """
        if not self.uses_default_argparse:
            return None
        
        return DefaultFilterOptions(finfo=self)


    def formatFilterHelp(self):
        """
        Get the filter's help text.

        This is either the filter's own custom help text, or the help text
        retrieved from the filter's argument parser.
        """
        if hasattr(self.fmodule, 'format_help'):
            return self.fmodule.format_help()
        fopt = self.defaultFilterOptions()
        if fopt is not None:
            return fopt.format_filter_help()
        return "<no help available>"

    def makeFilter(self, optionstring):
        """
        Instantiate the filter with the given option string.

        Returns the new filter instance.

        Raises py:exc:`FilterCreateError` if any exception was raised during the
        filter instantiation.
        """

        (pargs, kwargs) = self.parseOptionStringArgs(optionstring)

        # make sure arguments are valid
        self.validateOptionStringArgs(pargs, kwargs)

        # and finally, instantiate the filter.
        logger.debug(self.name + u': calling fclass('+','.join([repr(x) for x in pargs])+', '+
                     ','.join([repr(k)+'='+repr(v) for k,v in iteritems(kwargs)]) + ')')

        # exceptions caught here are those thrown from the filter constructor itself.
        try:
            return self.fclass(*pargs, **kwargs)
        except Exception as e:
            logger.debug("Filter exception:\n" + traceback.format_exc())
            msg = unicodestr(e)
            if (not isinstance(e, FilterError) and e.__class__ != Exception):
                # e.g. TypeError or SyntaxError or NameError or KeyError or whatever...
                msg = e.__class__.__name__ + ": " + msg
            raise FilterCreateError(msg, self.name)



    
def make_filter(name, options, filterpath=filterpath):
    """
    Main filter instance factory function: Create the filter instance.

    This is a simple wrapper for `FilterInfo(...).makeFilter(...)`.
    """

    return FilterInfo(name, filterpath=filterpath).makeFilter(options)





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


_rxargdoc = re.compile(r'^\s*(-\s*|\*)\s*(?P<argname>\w+)\s*(\((?P<argtypename>\w+)\))?\s*:\s*', re.MULTILINE)


def parseArgdoc(doc):
    """
    Parses argument documentation from a docstring.  Extracts lists of argument
    documentation in a relatively crude way.  Expects arguments to be documented
    in lines of the form::

      * argument_name (type) :  Here comes the documentation of the argument. It
        may span several lines, that is ok.
      *arg2: as you can see, whitespace is optional and ignored; the type
             name is also not necessary.
      - arg3: also, argument listings may begin with a dash instead of an asterisk

    The argument list is expected to be a the end of the docstring. I.e.,
    anything that follows the argument list will be included in the doc of the
    last argument!

    If there is a line with the single word 'Arguments' (with possible
    punctuation), e.g.::

        Arguments:

    Then argdocs are processed only after that line.

    Returns a tuple (argdoclist, fndoc). The `argdoclist` is a list of objects
    (actually, named tuples), with the fields 'argname', 'argtypename', and
    'doc'.  If an argtypename is absent, it is set to an empty value.  The
    `fndoc` is a string corresponding to the rest of the docstring before the
    argument documentation.
    """
    if (doc is None):
        doc = ''

    # If there is a "Arguments" title line, then everything before that is
    # regular doc we shouldn't parse

    argumentstitlem = re.search(re.compile(r'^[^A-Za-z]*Arguments[^A-Za-z]*$', flags=re.MULTILINE), doc)

    prebegindoc = ''
    if argumentstitlem is not None:
        prebegindoc = doc[:argumentstitlem.start()] + '\n'
        doc = doc[argumentstitlem.end():]

    # now find argdocs.

    argdocspos = []
    for m in re.finditer(_rxargdoc, doc):
        argdocspos.append(m)

    argdoclist = []
    begindoc = None
    for k in range(len(argdocspos)):
        m = argdocspos[k]
        if (begindoc is None):
            begindoc = doc[:m.start()]
        thisend = (argdocspos[k+1].start() if k < len(argdocspos)-1 else len(doc))
        # adjust whitespace in docstr
        docstr = doc[m.end():thisend].strip()
        # just format whitespace, don't fill to a fixed width. This is for the
        # GUI. we'll fill to a certain width only when specifying this as the
        # argparse help argument.
        docstr = re.sub(r'\n\s*', '\n', docstr) # TextWrapper doesn't simplify whitespace apparently
        docstr = (textwrap.TextWrapper(width=100*len(docstr), replace_whitespace=True, drop_whitespace=True)
                  .fill(docstr))
        argdoclist.append(_ArgDoc(argname=m.group('argname'),
                                  argtypename=m.group('argtypename'),
                                  doc=docstr))

    if begindoc is None:
        # there were no argdocs
        begindoc = doc

    begindoc = prebegindoc + begindoc
    
    return argdoclist, textwrap.dedent(begindoc.strip())


_add_epilog="""

Have a lot of fun!
"""

class DefaultFilterOptions(object):
    def __init__(self, filtername=None, filterpath=filterpath, finfo=None):
        """
        Instantiate this class as::

            defopt = DefaultFilterOptions(filtername [, filterpath=...])    OR
            defopt = DefaultFilterOptions(finfo=...)
        """

        if finfo is not None:
            self.finfo = finfo
            if filtername is not None:
                raise ValueError("use signature DefaultFilterOptions(filtername, [filterpath=]) "
                                 "or  DefaultFilterOptions(finfo=)")
        else:
            self.finfo = FilterInfo(filtername, filterpath=filterpath)

        self._filtername = self.finfo.name
        self._fmodule = self.finfo.fmodule
        self._fclass = self.finfo.fclass

        # find out what the arguments to the filter constructor are
        self.fclass_arg_defs = inspect_getargspec(self._fclass.__init__)
        (fargs, varargs, keywords, defaults) = self.fclass_arg_defs

        # get some doc about the parameters
        docstr = self._fclass.__init__.__doc__
        argdoclist, fndocpart = parseArgdoc(docstr)
        argdocs = dict([(x.argname, x) for x in argdoclist])

        self._use_auto_case = True
        if (re.search(r'[A-Z]', "".join(fargs))):
            logger.debug("filter "+self._filtername+": will not automatically adjust option letter case.")
            self._use_auto_case = False

        if (defaults is None):
            defaults = []
        def fmtarg(k, fargs, defaults):
            s = fargs[k]
            off = len(fargs)-len(defaults)
            if (k-off >= 0):
                s += "="+repr(defaults[k-off])
            return s
        fclasssyntaxdesc = self._fclass.__name__+("(" + " ".join([xpart for xpart in [
            (", ".join([fmtarg(k, fargs, defaults)
                        for k in range(len(fargs))
                        if fargs[k] != "self"])),
            ("[...]" if varargs else ""),
            ("[..=...]" if keywords else ""),
            ] if xpart]) + ")")

        p = FilterArgumentParser(filtername=self._filtername,
                                 prog=self._filtername,
                                 description=self._fclass.getHelpDescription(),
                                 epilog=_add_epilog,
                                 add_help=False,
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 )

        group_filter = p.add_argument_group('Filter Arguments')

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

        self._filtervarargs = True if varargs else False
        self._filtervarkwargs = True if keywords else False

        def make_filter_option(farg):
            fopt = farg.replace('_', '-')
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


        argdocs_left = [ x.argname for x in argdoclist ]
        for n in range(len(fargs)):
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
                                   help="-sKey=Value sets parameter values")
        group_general.add_argument('-d', action=store_key_bool, const=True, dest='_d_args',
                                   metavar='Switch[=<value>]', exception=FilterOptionsParseErrorHintSInstead,
                                   help="-dSwitch[=<value>] sets flag `Switch' to given boolean value, by default "
                                   "True. Valid boolean values are 1/T[rue]/Y[es]/On and 0/F[alse]/N[o]/Off")

        # allow also to give arguments without the keywords.
        if varargs:
            group_general.add_argument('_args', nargs='*', metavar='<arg>',
                                       help="Additional arguments will be passed as is to the filter--see "
                                       "documentation below")

        #p.add_argument_group(u"Python filter syntax",
        #                     textwrap.fill(fclasssyntaxdesc, width=80, subsequent_indent='        '))

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

        p.add_argument_group(u'FILTER DESCRIPTION', "\n" + self._fclass.getHelpText())


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

    def filterAcceptsVarArgs(self):
        """Returns `True` if the filter can accept additional positional arguments."""
        return self._filtervarargs

    def filterAcceptsVarKwargs(self):
        """Returns `True` if the filter can accept additional keyword arguments."""
        return self._filtervarkwargs

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
        x = re.sub(r'[A-Z]', lambda mo: ('_' if mo.start() > 0 else '')+mo.group().lower(), x)
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

        NOTE: This function doesn't actually validate all options to check
        whether the filter will accept them (e.g., options like '-sKey=Value'
        will be blindly appended to the kwargs). See
        :py:meth:`FilterInfo.validateOptionStringArgs()` for that.
        """

        logger.debug("parse_optionstring: "+self._filtername+"; fclass="+repr(self._fclass)
                     +"; optionstring="+optionstring)

        p = self._parser

        (fargs, varargs, keywords, defaults) = self.fclass_arg_defs
        if defaults is None:
            defaults = []

        try:
            #
            # shlex.split() doesn't work on unicode objects directly, need to encode it in
            # 8-bit e.g. using 'utf-8'.
            #
            parts = [ from_native_str(x) for x in shlex.split(to_native_str(optionstring)) ]
        except ValueError as e:
            raise FilterOptionsParseError(u"Error parsing option string: %s\n\t%s"
                                          %(unicodestr(e), optionstring.strip()),
                                          self._filtername)
        
        try:
            args = p.parse_args(parts)
        except FilterOptionsParseError as e:
            e.name = self._filtername
            raise

        # parse and collect arguments now

        dargs = vars(args)

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
                    typ = unicodestr
                kwargs[argname] = typ(argval)
            else:
                kwargs[argname] = argval # raw type if we can't figure one out (could be
                                         # extra kwargs argument, or not documented)

        def safe_set_kw_arg(kwargs, argname, argval):
            try:
                set_kw_arg(kwargs, argname, argval)
            except Exception as e:
                raise FilterOptionsParseError(
                    "Error parsing key option value: %s -> %s (%s)\n\t%s"
                    %(unicodestr(arg), unicodestr(argval),
                      unicodestr(e), optionstring.strip()),
                    self._filtername)


        for (arg, argval) in iteritems(dargs):
            if (varargs and arg == '_args'):
                optspec['_args'] = argval
                continue
            if (arg == '_d_args' and argval is not None):
                # get all the defined args
                for (thekey, theval) in argval:
                    # store this definition
                    therealkey = self.getArgNameFromSOpt(thekey)
                    optspec['kwargs'][therealkey] = theval

                    logger.debug("Set switch `%s' to %s" %(thekey, "True" if theval else "False"))

                continue

            if (arg == '_s_args' and argval is not None):
                # get all the set args
                for (key, v) in argval:
                    thekey = self.getArgNameFromSOpt(key)
                    safe_set_kw_arg(optspec['kwargs'], thekey, v)

                    logger.debug("Set option `%s' to `%s'" %(thekey, v))

                continue

            if (argval is None):
                continue

            safe_set_kw_arg(optspec['kwargs'], arg, argval)

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
        for n in range(len(fargs)):
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
        
        return (pargs, kwargs)


    def format_filter_help(self):
        prolog = self._fclass.getHelpAuthor()
        if (prolog):
            prolog += "\n\n"

        return prolog + self._parser.format_help()


def format_filter_help(filtname=None, filterpath=filterpath):
    """
    Format help text for the given filter.  This is a shortcut to the
    corresponding method in :py:class:`FilterInfo`.
    """

    return FilterInfo(filtname, filterpath=filterpath).formatFilterHelp()
