
import importlib;
import re;
import shlex;
import inspect;

from core.blogger import logger;


# list all filters here.
__all__ = [ 'arxiv'
            ]


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
        kwargs = fmodule.parse_args(optionstring);
    else:
        (pargs, kwargs) = _default_parse_optionstring(name, fclass, optionstring);

    # and finally, instantiate the filter.
    return fclass(*pargs, **kwargs);




# a basic, default option parser. Simply maps the options in the form key=value to
# the filter constructor's function argument names; unrecognized chunks are positional
# arguments.
def _default_parse_optionstring(name, fclass, optionstring):

    logger.debug("_default_parse_optionstring: name: "+name+"; fclass="+repr(fclass)
                 +"; optionstring="+optionstring);

    pargs = [];
    kwargs = {};

    (fargs, varargs, keywords, defaults) = inspect.getargspec(flcass.__init__)[0];
    
    parts = shlex.split(optionstring);
    for x in parts:
        m = re.match(r'/(\w+)=(.*)/', x);
        if (not m):
            logger.debug("positional argument: "+x);
            pargs.append(x);
            continue

        arg = m.group(1);
        val = m.group(2);
        if (arg not in fargs):
            if (keywords is None):
                raise FilterOptionsParseError(name, "Bad option key: `"+arg+"'");
            # otherwise, this arg will be captured by the constructor's **kwargs

        # store this arg as a keyword argument.
        kwargs[arg] = val;

    return (pargs, kwargs);
        
