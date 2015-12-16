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


"""
This module contains the code that implements Bibolamazi's main functionality. It also
provides the basic tools for the command-line interface.
"""


import os
import os.path
import re
import sys
import argparse
import textwrap
import types
from collections import namedtuple
import logging


# import all the parts we need from our own application.
# ------------------------------------------------------

import bibolamazi.init
# rest of the modules
from . import blogger
from . import version
from .bibolamazifile import BibolamaziFile
from .bibfilter import BibFilter
from . import argparseactions
from . import butils
from .butils import BibolamaziError

# for list of filters
from .bibfilter import factory as filterfactory


# our logger for the main module
logger = logging.getLogger(__name__)



# ------------------------------------------------------------------------------


# code to set up logging mechanism, if run by command-line

def verbosity_logger_level(verbosity):
    """
    Simple mapping of 'verbosity level' (used, for example for command line
    options) to correspondig logging level (:py:const:`logging.DEBUG`,
    :py:const:`logging.ERROR`, etc.).
    """
    if verbosity == 0:
        return logging.ERROR
    elif verbosity == 1:
        return logging.INFO
    elif verbosity == 2:
        return logging.DEBUG
    elif verbosity >= 3:
        return blogger.LONGDEBUG

    raise ValueError("Bad verbosity level: %r" %(verbosity))




# ------------------------------------------------------------------------------


class BibolamaziNoSourceEntriesError(BibolamaziError):
    def __init__(self):
        msg = "Error: No source entries found. Stopping before we overwrite the bibolamazi file.";
        BibolamaziError.__init__(self, msg);



def setup_filterpackage_from_argstr(argstr):
    """
    Add a filter package definition and path to filterfactory.filterpath from a string
    that is a e.g. a command-line argument to --filterpath or a part of the environment
    variable BIBOLAMAZI_FILTER_PATH.
    """

    if not argstr:
        return

    fpparts = argstr.split('=',1)
    fpname = fpparts[0]
    fpdir = fpparts[1] if len(fpparts) >= 2 and fpparts[1] else None

    if re.search(r'[^a-zA-Z0-9_\.]', fpname):
        raise BibolamaziError("Invalid filter package: `%s': not a valid python identifier. "
                              "Did you get the filterpackage syntax wrong? "
                              "Syntax: '<packagename>[=<path>]'." %(fpname))

    try:
        ok = filterfactory.validate_filter_package(fpname, fpdir, raise_exception=True)
    except filterfactory.NoSuchFilterPackage as e:
        raise BibolamaziError(unicode(e))

    filterfactory.filterpath[fpname] = fpdir
    

def setup_filterpackages_from_env():
    if 'BIBOLAMAZI_FILTER_PATH' in os.environ:
        logger.debug("Detected BIBOLAMAZI_FILTER_PATH=%s, using it" %(os.environ['BIBOLAMAZI_FILTER_PATH']))
        for fp in reversed(os.environ['BIBOLAMAZI_FILTER_PATH'].split(os.pathsep)):
            setup_filterpackage_from_argstr(fp)

class AddFilterPackageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setup_filterpackage_from_argstr(values)
    

def get_args_parser():

    parser = argparse.ArgumentParser(
        description='Prepare consistent BibTeX files for your LaTeX documents',
        prog='bibolamazi',
        epilog="Log messages will be produced in color by default if outputting to a TTY. To override "
        "the use of TTY colors, set environment variable BIBOLAMAZI_TTY_COLORS to 'yes', 'no' or 'auto'.",
        add_help=False);

    parser.add_argument('-N', '--new', action=argparseactions.opt_init_empty_template, nargs=1,
                        metavar="[new_filename.bib]",
                        help="Create a new bibolamazi file with a template configuration.");
    parser.add_argument('-F', '--list-filters', action=argparseactions.opt_list_filters, dest='list_filters',
                        help="Show a list of available filters along with their description, and exit.");
    parser.add_argument('-C', '--no-cache', action='store_false', dest='use_cache', default=True,
                        help="Bypass and ignore any existing cache file, and regenerate the cache. If "
                        "the cache file exists, it will be overwritten.");
    parser.add_argument('-z', '--cache-timeout', dest='cache_timeout', type=butils.parse_timedelta,
                        default=None,
                        help="The default timeout after which to consider items in cache to be invalid. "
                        "Not all cache items honor this. Format: '<N><unit>' with unit=w/d/m/s");

    parser.add_argument('--help', '-h', action=argparseactions.opt_action_help, nargs='?',
                        metavar='filter',
                        help='Show this help message and exit. If filter is given, show information and '
                        'help text for that filter. See --list-filters for a list of available filters.')
    parser.add_argument('--version', action=argparseactions.opt_action_version, nargs=0,
                        help='Show bibolamazi version number and exit.')

    parser.add_argument('--filterpackage', action=AddFilterPackageAction,
                        help="Add a package name in which to search for filters. You may specify this "
                        "option multiple times; last specified filter packages are searched first. Valid "
                        "values for this option are a simple python package name (if it is in the "
                        "PYTHONPATH), or a pair 'package=/some/location' where package is the python "
                        "package name, which will be loaded with the given path prepended to sys.path.")

    parser.add_argument('--verbosity', action=argparseactions.opt_set_verbosity, nargs=1,
                        help="Set verbosity level (0=quiet, 1=info (default), 2=verbose, 3=long debug).")
    parser.add_argument('-q', '-v0', '--quiet', action=argparseactions.opt_set_verbosity, nargs=0, const=0,
                        help="Don't display any messages (same as --verbosity=0)");
    parser.add_argument('-v1', action=argparseactions.opt_set_verbosity, nargs=0, const=1,
                        help='Set normal verbosity mode (same as --verbosity=1)')
    parser.add_argument('-v', '-v2', '--verbose', action=argparseactions.opt_set_verbosity, nargs=0, const=2,
                        help='Set verbose mode (same as --verbosity=2)')
    parser.add_argument('-vv', '-v3', '--long-verbose', action=argparseactions.opt_set_verbosity, nargs=0, const=3,
                        help='Set very verbose mode, with long debug messages (same as --verbosity=3)')
    parser.add_argument('--fine-log-levels', action=argparseactions.opt_set_fine_log_levels,
                        help=textwrap.dedent('''\
                        Fine-grained logger control: useful for debugging filters or
                        bibolamazi itself. This is a comma-separated list of modules and
                        corresponding log levels to set, e.g.
                        "core=INFO,filters=DEBUG,filters.arxiv=LONGDEBUG", where if in an
                        item no module is given (but just a level or number), then the
                        root logger is addressed. Possible levels are (%s)
                        ''')%(
                            ", ".join( (x[0] for x in blogger.LogLevel.levelnos) )
                        ))

    parser.add_argument('bibolamazifile',
                        help='The .bibolamazi.bib file to update, i.e. that contains the %%%%%%-BIB-OLA-MAZI '
                        'configuration tags.');

    return parser



ArgsStruct = namedtuple('ArgsStruct', ('bibolamazifile', 'use_cache', 'cache_timeout'));



def main(argv=sys.argv[1:]):

    try:

        # run main program
        _main_helper(argv)
        
    except SystemExit:
        raise
    
    except KeyboardInterrupt:
        raise

    except BibolamaziError as e:
        logger.error("\n" + unicode(e))

    except:
        
        print
        print " -- EXCEPTION --"
        print

        # debugging post-mortem
        import traceback; traceback.print_exc()
        import pdb; pdb.post_mortem();

    

def _main_helper(argv):

    # get some basic logging mechanism running
    blogger.setup_simple_console_logging()
    # start with level INFO
    logging.getLogger().setLevel(logging.INFO)

    # load precompiled filters, if we've got any
    # ------------------------------------------
    #try:
    #    import bibolamazi.bibolamazi_compiled_filter_list as pc
    #    filters_factory.load_precompiled_filters('bibolamazi.filters', dict([
    #        (fname, pc.__dict__[fname])  for fname in pc.filter_list
    #        ]))
    #except ImportError:
    #    pass

    
    # set up extra filter packages from environment variables
    # -------------------------------------------------------

    setup_filterpackages_from_env()

    
    # parse the command line arguments
    # --------------------------------

    parser = get_args_parser()

    args = parser.parse_args(args=argv);

    return run_bibolamazi_args(args)



def run_bibolamazi(bibolamazifile, **kwargs):
    # defaults
    kwargs2 = {
        'use_cache': True,
        'cache_timeout': None,
        }
    kwargs2.update(kwargs);
    args = ArgsStruct(bibolamazifile, **kwargs2)
    return run_bibolamazi_args(args)


def run_bibolamazi_args(args):
    #
    # args is supposed to be the parsed arguments from main()
    #

    logger.debug(textwrap.dedent("""
    Bibolamazi Version %(ver)s by Philippe Faist (C) 2015

    Use option --help for help information.
    """         %   {
                     'ver': version.version_str
                     }));


    # open the bibolamazifile, which is the main bibtex file
    # ------------------------------------------------------

    kwargs = {
        'use_cache': args.use_cache
        }

    #
    # If given a cache_timeout, give it as parameter
    #
    if args.cache_timeout is not None:
        logger.debug("default cache timeout: %r", args.cache_timeout)
        kwargs['default_cache_invalidation_time'] = args.cache_timeout
    

    # open the bibolamazi file and create the BibolamaziFile object. This will parse the rules
    # and the entries, as well as keep some information on how to re-write to the file.
    bfile = BibolamaziFile(args.bibolamazifile, **kwargs)


    bibdata = bfile.bibliographyData();
    if (bibdata is None or not len(bibdata.entries)):
        logger.critical("No source entries found. Stopping before we overwrite the bibolamazi file.");
        raise BibolamaziNoSourceEntriesError()


    # now, run the selected filters in the corresponding order.
    # ---------------------------------------------------------

    for filtr in bfile.filters():
        #
        # For debugging: dump the library at each filter step on level longdebug()
        #
        if logger.isEnabledFor(blogger.LONGDEBUG):
            s = "========== Dumping Bibliography Database ==========\n"
            for key, entry in bibdata.entries.iteritems():
                s += "  %10s: %r\n\n"%(key, entry)
            s += "===================================================\n"
            logger.longdebug(s)

        #
        # See how the filter acts. It can act on the full bibolamazifile object, it can act on the
        # full list of entries (possibly adding/deleting entries etc.), or it can act on a single
        # entry.
        #
        action = filtr.action();

        logger.info("Filter: %s" %(filtr.getRunningMessage()));

        filtr.prerun(bfile)

        #
        # pass the whole bibolamazifile to the filter. the filter can actually do
        # whatever it wants with it (!!)
        #
        if (action == BibFilter.BIB_FILTER_BIBOLAMAZIFILE):
            filtr.filter_bibolamazifile(bfile);

            logger.debug('filter '+filtr.name()+' filtered the full bibolamazifile.');
            continue

        #
        # filter all the bibentries one by one throught the filter. The filter can only
        # process a single bibentry at a time.
        #
        if (action == BibFilter.BIB_FILTER_SINGLE_ENTRY):

            bibdata = bfile.bibliographyData();

            for (k, entry) in bibdata.entries.iteritems():
                filtr.filter_bibentry(entry);

            bfile.setBibliographyData(bibdata);

            logger.debug('filter '+filtr.name()+' filtered each of the the bibentries one by one.');
            continue

        raise ValueError("Bad value for BibFilter.action(): "+repr(action));

    # and output everything back to the original file.
    bfile.saveToFile();


    logger.debug('Done.');

    return None



if __name__ == "__main__":
    
    main()
