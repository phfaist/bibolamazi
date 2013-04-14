
import importlib;
import re;
import shlex;
import inspect;
import argparse;
import pdb;

from core.butils import store_key_val, store_key_const
from core.blogger import logger;


# list all filters here.
__all__ = ( 'arxiv',
            'duplicates',
            'url',
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
            pargs = [];
            kwargs = x;
    else:
        (pargs, kwargs) = _default_parse_optionstring(name, fclass, optionstring);

    # and finally, instantiate the filter.
    logger.debug('calling fclass('+','.join([repr(x) for x in pargs])+', '+
                  ','.join([repr(k)+'='+repr(v) for k,v in kwargs.iteritems()]) + ')');
    return fclass(*pargs, **kwargs);



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
    for k in range(len(pos)):
        m = pos[k]
        thisend = (pos[k+1].start() if k < len(pos)-1 else len(doc));
        argdocs[m.group(1)] = doc[m.end():thisend];

    use_auto_case = True
    if (re.search(r'[A-Z]', "".join(fargs))):
        logger.debug("filter "+name+": will not automatically adjust option letter case.");
        use_auto_case = False

    def getArgNameFromSOpt(x):
        if (not use_auto_case):
            return x
        x = re.sub(r'^[A-Z]', lambda mo: mo.group(0).lower(), x);
        x = re.sub(r'([a-z])([A-Z])', lambda mo: mo.group(1)+"_"+mo.group(2).lower(), x);
        return x
    
    p = argparse.ArgumentParser(prog=(u'bibolamazi:'+name),
                                description=fclass.helptext,
                                add_help=False,
                                );

    # a la ghostscript: -sOutputFile=blahblah -sKey=Value
    p.add_argument('-s', action=store_key_val, dest='_s_args', metavar='Key=Value',
                   help='-sKey=Value sets parameter values');
    p.add_argument('-d', action=store_key_const, const=True, dest='_d_args', metavar='Switch',
                   help='-dKey sets parameter Key to True');

    # allow also to give arguments without the keywords.
    p.add_argument('_args', nargs='*', metavar='<arg>');

    p.add_argument_group('filter parameters');

    for farg in fargs:
        # skip 'self'
        if (farg == 'self'):
            continue
        # normalize name
        fopt = re.sub('_', '-', farg);
        p.add_argument('--'+fopt, action='store', dest=farg,
                       help=argdocs.get(farg, None));


    return (p, getArgNameFromSOpt)

    
def _default_parse_optionstring(name, fclass, optionstring):

    logger.debug("_default_parse_optionstring: name: "+name+"; fclass="+repr(fclass)
                 +"; optionstring="+optionstring);

    (p, getArgNameFromSOpt) = _default_option_parser(name, fclass);

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
        if (arg == '_d_args' and argval is not None):
            # get all the defined args
            for key in argval:
                thekey = getArgNameFromSOpt(key);
                kwargs[thekey] = True
            continue
            
        if (arg == '_s_args' and argval is not None):
            # get all the set args
            for (key, v) in argval:
                thekey = getArgNameFromSOpt(key);
                kwargs[thekey] = v
            continue

        if (argval is None):
            continue
        
        kwargs[arg] = argval;
    
    #pdb.set_trace()

    return (pargs, kwargs);
        





def print_filter_help(name):
    #
    # First, get the filter help text.
    #

    fmodule = get_module(name);

    fclass = fmodule.getclass();

    (p, getArgNameFromSOpt) = _default_option_parser(name, fclass);

    p.print_help();
