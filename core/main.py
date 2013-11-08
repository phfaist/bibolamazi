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


import os
import os.path
import sys
import argparse
import textwrap
from collections import namedtuple


# import all the parts we need from our own application.
# ------------------------------------------------------

from core import version
from core.bibolamazifile import BibolamaziFile
from core.bibfilter import BibFilter
from core.blogger import logger
from core.argparseactions import store_or_count, opt_list_filters, opt_action_help, opt_action_version, opt_init_empty_template
from core.butils import BibolamaziError

# for list of filters
import filters



class BibolamaziNoSourceEntriesError(BibolamaziError):
    def __init__(self):
        msg = "Error: No source entries found. Stopping before we overwrite the bibolamazi file.";
        BibolamaziError.__init__(self, msg);




def get_args_parser():

    parser = argparse.ArgumentParser(description='Collect bibliographic entries from BibTeX files and'+
                                     ' apply rules or filters to them.',
                                     prog='bibolamazi',
                                     add_help=False);

    #parser.add_argument('-I', '--interactive', action='store_true',
    #                    help='Create a new bibfilter configuration, or modify current one interactively.');
    parser.add_argument('-v', '--verbose', action=store_or_count, dest='verbosity', default=1,
                        help='Increase or set verbosity (0=quiet,1=info,2=verbose,3=long debug)')
    parser.add_argument('-q', '--quiet', action='store_const', dest='verbosity', const=0,
                        help="Don't display any messages. Same as `-v 0'");
    parser.add_argument('-N', '--new', action=opt_init_empty_template, nargs=1, metavar="[new_filename.bib]",
                        help="Create a new bibolamazi file with a template configuration.");
    parser.add_argument('-F', '--list-filters', action=opt_list_filters, dest='list_filters',
                        help="Show a list of available filters along with their description, and exit.");
    parser.add_argument('-h', '--help', action=opt_action_help, nargs='?', metavar='filter',
                        help='Show this help message and exit. If filter is given, show information and '+
                        'help text for that filter. See --list-filters for a list of available filters.')
    parser.add_argument('--version', action=opt_action_version, nargs=0,
                        help='Show bibolamazi version number and exit.')
    parser.add_argument('outputbibfile',
                        help='The .bib file to update, i.e. that contains the %%%%%%BIB-OLA-MAZI configuration tags.');

    return parser


def main(argv=sys.argv[1:]):

    # parse the command line arguments
    # --------------------------------

    parser = get_args_parser()

    args = parser.parse_args(args=argv);

    return run_bibolamazi_args(args)


ArgsStruct = namedtuple('ArgsStruct', ('outputbibfile', 'verbosity', ));

def run_bibolamazi(outputbibfile, verbosity=1):
    args = ArgsStruct(outputbibfile, verbosity)
    return run_bibolamazi_args(args)


def run_bibolamazi_args(args):
    #
    # args is supposed to be the parsed arguments from main()
    #


    logger.setVerbosity(args.verbosity);
    logger.longdebug('Set verbosity: %d' %(args.verbosity));

    logger.debug(textwrap.dedent("""
    Bibolamazi Version %(ver)s by Philippe Faist (C) 2013

    Use option --help for help information.
    """         %   {
                     'ver': version.version_str
                     }));



    # open the bibolamazifile, which is the output bibtex file
    # -------------------------------------------------------

    # open the outputbibfile and create the BibolamaziFile object. This will parse the rules
    # and the entries, as well as keep some information on how to re-write to the file.
    bfile = BibolamaziFile(args.outputbibfile);


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

        raise ValueError("Bad value for BFilter.action(): "+repr(action));


    # and output everything back to the original file.
    bfile.save_to_file();


    logger.debug('Done.');

    return None
