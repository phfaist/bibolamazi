
import importlib;
import re;
import shlex;
import inspect;
import argparse;
import pdb;

from core.butils import store_key_val
from core.blogger import logger;


# list all filters here.
__all__ = ( 'arxiv',
            'duplicates',
            )


# some exception classes.

class NoSuchFilter(Exception):
    def __init__(self, fname):
        Exception.__init__(self, "No such filter: "+fname);

class FilterOptionsParseError(Exception):
    def __init__(self, name, errorstr):
        Exception.__init__(self, "Can't parse options for filter "+name+"': "+errorstr);



# store additional information about the modules.

filter_modules = {};

def get_module(name):
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
    

def make_filter(name, optionstring):

    fmodule = get_module(name);

    fclass = fmodule.getclass();

    pargs = [];
    kwargs = {};
    if (hasattr(fmodule, 'parse_args')):
        x = fmodule.parse_args(optionstring);
        try:
            (pargs, kwargs) = x;
        except TypeError, ValueError:
            kwargs = x;
    else:
        (pargs, kwargs) = _default_parse_optionstring(name, fclass, optionstring);

    # and finally, instantiate the filter.
    return fclass(*pargs, **kwargs);




# a basic, default option parser. Simply constructs an argparse object with the function's argument
# names mapped to options.
def _default_parse_optionstring(name, fclass, optionstring):

    logger.debug("_default_parse_optionstring: name: "+name+"; fclass="+repr(fclass)
                 +"; optionstring="+optionstring);

    (fargs, varargs, keywords, defaults) = inspect.getargspec(fclass.__init__);
    
    p = argparse.ArgumentParser(prog=(u'bibolamazi:'+name), description=(name+u' bibolamazi filter'));

    for farg in fargs:
        # normalize name
        fopt = re.sub('_', '-', farg);
        p.add_argument('--'+fopt, action='store');

    if keywords:
        # a la ghostscript: -sOutputFile=blahblah -sKey=Value
        p.add_argument('-s', action=store_key_val, dest='');

    if varargs:
        p.add_argument('args', nargs=argparse.REMAINDER, dest='_args');

    parts = shlex.split(optionstring);
    args = p.parse_args(parts);

    # parse and collect arguments now

    dargs = vars(args);
    pargs = [];
    kwargs = {};

    for (arg, argval) in dargs.iteritems():
        if (arg == '_args'):
            pargs = argval;
            continue
        if (arg == 'self'):
            continue
        if (argval is None):
            continue
        kwargs[arg] = argval;
    
    #pdb.set_trace()

    return (pargs, kwargs);
        
