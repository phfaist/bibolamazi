

import os
import os.path
import sys
import argparse


# import all the parts we need from our own application.
# ------------------------------------------------------

from core.bibfilterfile import BibFilterFile
from core.bibfilter import BibFilter
from core.blogger import logger
from core.butils import store_or_count, opt_action_help

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
parser.add_argument('-q', '--quiet', action='store_const', dest='verbosity', const=0);
parser.add_argument('-h', '--help', action=opt_action_help, nargs='?', metavar='filter',
                    help='Show this help message and exit. If filter is given, shows information and '+
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
