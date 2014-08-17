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


import os
import os.path
import re
import sys
import argparse
import textwrap
import types
from collections import namedtuple


# import all the parts we need from our own application.
# ------------------------------------------------------

from core import version
from core.bibolamazifile import BibolamaziFile
from core.bibfilter import BibFilter
from core.blogger import logger
from core.argparseactions import store_or_count, opt_list_filters, opt_action_help, opt_action_version, opt_init_empty_template
from core import butils
from core.butils import BibolamaziError

# for list of filters
import filters



class BibolamaziNoSourceEntriesError(BibolamaziError):
    def __init__(self):
        msg = "Error: No source entries found. Stopping before we overwrite the bibolamazi file.";
        BibolamaziError.__init__(self, msg);



def setup_filterpackage_from_argstr(argstr):
    """
    Add a filter package definition and path to filters.filterpath from a string that is a
    e.g. a command-line argument to --filterpath or a part of the environment variable
    BIBOLAMAZI_FILTER_PATH.
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

    if not filters.validate_filter_package(fpname, fpdir, raise_exception=False):
        raise BibolamaziError("Invalid filter package `%s' [in directory `%s']" % (fpname, fpdir))

    filters.filterpath[fpname] = fpdir
    

def setup_filterpackages_from_env():
    if 'BIBOLAMAZI_FILTER_PATH' in os.environ:
        logger.debug("Detected BIBOLAMAZI_FILTER_PATH=%s, using it" %(os.environ['BIBOLAMAZI_FILTER_PATH']))
        for fp in reversed(os.environ['BIBOLAMAZI_FILTER_PATH'].split(os.pathsep)):
            setup_filterpackage_from_argstr(fp)

class AddFilterPackageAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setup_filterpackage_from_argstr(values)
    

def get_args_parser():

    parser = argparse.ArgumentParser(description='Collect bibliographic entries from BibTeX files and'
                                     ' apply rules or filters to them.',
                                     prog='bibolamazi',
                                     add_help=False);

    parser.add_argument('-N', '--new', action=opt_init_empty_template, nargs=1, metavar="[new_filename.bib]",
                        help="Create a new bibolamazi file with a template configuration.");
    parser.add_argument('-F', '--list-filters', action=opt_list_filters, dest='list_filters',
                        help="Show a list of available filters along with their description, and exit.");
    parser.add_argument('-C', '--no-cache', action='store_false', dest='use_cache', default=True,
                        help="Bypass and ignore any existing cache file, and regenerate the cache. If "
                        "the cache file exists, it will be overwritten.");
    parser.add_argument('-z', '--cache-timeout', dest='cache_timeout', type=butils.parse_timedelta,
                        help="The default timeout after which to consider items in cache to be invalid. "
                        "Not all cache items honor this. Format: '<N><unit>' with unit=w/d/m/s");

    parser.add_argument('--help', '-h', action=opt_action_help, nargs='?', metavar='filter',
                        help='Show this help message and exit. If filter is given, show information and '
                        'help text for that filter. See --list-filters for a list of available filters.')
    parser.add_argument('--version', action=opt_action_version, nargs=0,
                        help='Show bibolamazi version number and exit.')

    parser.add_argument('--filterpackage', action=AddFilterPackageAction,
                        help="Add a package name in which to search for filters. Optionally you may also"
                        " add a corresponding python path where to find the package, in the format"
                        " 'filterpackage=/path/to/it'. You may specify this option multiple times; last"
                        " specified filter packages are searched first.")

    parser.add_argument('--verbosity', action='store', dest='verbosity', nargs=1, default=1,
                        help="Set verbosity level (0=quiet, 1=info (default), 2=verbose, 3=long debug)")
    parser.add_argument('-q', '-v0', '--quiet', action='store_const', dest='verbosity', const=0,
                        help="Don't display any messages (same as --verbosity=0)");
    parser.add_argument('-v1', action='store_const', dest='verbosity', default=1, const=1,
                        help='Set normal verbosity mode (same as --verbosity=1)')
    parser.add_argument('-v', '-v2', '--verbose', action='store_const', dest='verbosity', const=2,
                        help='Set verbose mode (same as --verbosity=2)')
    parser.add_argument('-vv', '-v3', '--long-verbose', action='store_const', dest='verbosity', const=3,
                        help='Set very verbose mode, with long debug messages (same as --verbosity=3)')

    parser.add_argument('outputbibfile',
                        help='The .bib file to update, i.e. that contains the %%%%%%-BIB-OLA-MAZI '
                        'configuration tags.');

    return parser



def main(argv=sys.argv[1:]):

    # set up extra filter packages from environment variables
    # -------------------------------------------------------

    setup_filterpackages_from_env()

    # parse the command line arguments
    # --------------------------------

    parser = get_args_parser()

    args = parser.parse_args(args=argv);

    return run_bibolamazi_args(args)


ArgsStruct = namedtuple('ArgsStruct', ('outputbibfile', 'verbosity', 'use_cache', 'cache_timeout' ));

def run_bibolamazi(outputbibfile, verbosity=1, use_cache=True, cache_timeout=None):
    args = ArgsStruct(outputbibfile, verbosity, use_cache, cache_timeout)
    return run_bibolamazi_args(args)


def run_bibolamazi_args(args):
    #
    # args is supposed to be the parsed arguments from main()
    #

    logger.setVerbosity(args.verbosity);
    logger.longdebug('Set verbosity: %d' %(args.verbosity));

    logger.debug(textwrap.dedent("""
    Bibolamazi Version %(ver)s by Philippe Faist (C) 2014

    Use option --help for help information.
    """         %   {
                     'ver': version.version_str
                     }));


    # open the bibolamazifile, which is the output bibtex file
    # -------------------------------------------------------

    # open the outputbibfile and create the BibolamaziFile object. This will parse the rules
    # and the entries, as well as keep some information on how to re-write to the file.
    bfile = BibolamaziFile(args.outputbibfile, use_cache=args.use_cache);

    #
    # If given a cache_timeout, set it
    #
    if args.cache_timeout:
        bfile.set_default_cache_invalidation_time(args.cache_timeout)
    

    bibdata = bfile.bibliographydata();
    if (bibdata is None or not len(bibdata.entries)):
        logger.critical("No source entries found. Stopping before we overwrite the bibolamazi file.");
        raise BibolamaziNoSourceEntriesError()


    # now, run the selected filters in the corresponding order.
    # ---------------------------------------------------------

    for filtr in bfile.filters():
        #
        # See how the filter acts. It can act on the full bibolamazifile object, it can act on the
        # full list of entries (possibly adding/deleting entries etc.), or it can act on a single
        # entry.
        #
        action = filtr.action();

        logger.info("Filter: %s" %(filtr.getRunningMessage()));

        #
        # pass the whole bibolamazifile to the filter. the filter can actually do
        # whatever it wants with it (!!)
        #
        if (action == BibFilter.BIB_FILTER_BIBOLAMAZIFILE):
            filtr.filter_bibolamazifile(bfile);

            logger.debug('filter '+filtr.name()+' filtered the full bibolamazifile.');
            continue

        #
        # filter all the bibligraphy data in batch
        #
        if (action == BibFilter.BIB_FILTER_BIBLIOGRAPHYDATA):
            bibliographydata = filtr.filter_bibliographydata(bfile.bibliographydata());
            bfile.setBibliographyData(bibliographydata);

            logger.debug('filter '+filtr.name()+' filtered the bibliography data.');
            continue

        #
        # filter all the bibentries one by one throught the filter. The filter can only
        # process a single bibentry at a time.
        #
        if (action == BibFilter.BIB_FILTER_SINGLE_ENTRY):

            bibdata = bfile.bibliographydata();

            for k,v in bibdata.entries.iteritems():
                bibdata.entries[k] = filtr.filter_bibentry(v);

            bfile.setBibliographyData(bibdata);

            logger.debug('filter '+filtr.name()+' filtered each of the the bibentries one by one.');
            continue

        raise ValueError("Bad value for BibFilter.action(): "+repr(action));

    # and output everything back to the original file.
    bfile.save_to_file();


    logger.debug('Done.');

    return None
