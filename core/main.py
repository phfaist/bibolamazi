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


# import all the parts we need from our own application.
# ------------------------------------------------------

from core.bibfilterfile import BibFilterFile
from core.bibfilter import BibFilter
from core.blogger import logger
from core.butils import store_or_count, opt_list_filters, opt_action_help

# for list of filters
import filters




# parse the command line arguments
# --------------------------------

parser = argparse.ArgumentParser(description='Collect bibliographic entries from BibTeX files and'+
                                 ' apply rules or filters to them.',
                                 prog='bibolamazi',
                                 add_help=False);

#parser.add_argument('-I', '--interactive', action='store_true',
#                    help='Create a new bibfilter configuration, or modify current one interactively.');
parser.add_argument('-v', '--verbose', action=store_or_count, dest='verbosity', default=1,
                    help='Increase or set verbosity (0=quiet,1=info,2=verbose)')
parser.add_argument('-q', '--quiet', action='store_const', dest='verbosity', const=0,
                    help="Don't display any messages. Same as `-v 0'");
parser.add_argument('-F', '--list-filters', action=opt_list_filters, dest='list_filters',
                    help="Show a list of available filters along with their description, and exit.");
parser.add_argument('-h', '--help', action=opt_action_help, nargs='?', metavar='filter',
                    help='Show this help message and exit. If filter is given, show information and '+
                    'help text for that filter. Available filters are: '+", ".join(filters.__all__))
parser.add_argument('outputbibfile',
                    help='The .bib file to update, i.e. that contains the %%%%%%BIB-OLA-MAZI configuration tags.');

args = parser.parse_args();

logger.setVerbosity(args.verbosity);
logger.debug('Set verbosity to level '+repr(args.verbosity));



# open the bibfilterfile, which is the output bibtex file
# -------------------------------------------------------

# open the outputbibfile and create the BibFilterFile object. This will parse the rules
# and the entries, as well as keep some information on how to re-write to the file.
bfile = BibFilterFile(args.outputbibfile);



# now, run the selected filters in the corresponding order.
# ---------------------------------------------------------

for filtr in bfile.filters():
    #
    # See how the filter acts. It can act on the full bibfilterfile object, it can act on the
    # full list of entries (possibly adding/deleting entries etc.), or it can act on a single
    # entry.
    #
    action = filtr.action();
    
    logger.info("Filter: %s" %(filtr.name()));

    #
    # pass the whole bibfilterfile to the filter. the filter can actually do
    # whatever it wants with it (!!)
    #
    if (action == BibFilter.BIB_FILTER_BIBFILTERFILE):
        filtr.filter_bibfilterfile(bfile);

        logger.debug('filter '+filtr.name()+' filtered the full bibfilterfile.');
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

