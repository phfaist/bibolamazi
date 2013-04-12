#!/usr/bin/python

import os
import os.path
import sys
import argparse

# setup python path correctly first.
# ----------------------------------
thisdir = os.path.dirname(os.path.realpath(__file__));
sys.path += [thisdir,
             thisdir + '/3rdparty/pybtex'];


# import all the parts we need from our own application.
# ------------------------------------------------------

from core.bibfilterfile import BibFilterFile
from core.bibfilter import BibFilter
from core.blogger import logger



# parse the command line arguments
# --------------------------------

parser = argparse.ArgumentParser(description='Clean up LaTeX bibliography, with specific configurable rules'+
                                 ' for use in specific documents. Use --help for more info.');
parser.add_argument('-I', '--interactive', action='store_true',
                    help='Create a new bibfilter configuration, or modify current one interactively.');
parser.add_argument('outputbibfile',
                    help='The .bib file *to generate*, that contains the %BIBFILTER: tags.');

args = parser.parse_args();



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
    if (action == BibFilter.BIB_FILTER_FILE):
        bfile = filtr.filter_bibfilterfile(bfile);

        logger.debug('filter '+filtr.name()+' filtered the full bibfilterfile.');
        continue
        
    #
    # filter all the bibentries in batch
    #
    if (action == BibFilter.BIB_FILTER_ENTRY_LIST):
        bibentries = filtr.filter_bibentry_list(bfile.bibentries());
        bfile.setEntries(bibentries);

        logger.debug('filter '+filtr.name()+' filtered the bibentries list.');
        continue
    
    #
    # filter all the bibentries one by one throught the filter. The filter can only
    # process a single bibentry at a time.
    #
    if (action == BibFilter.BIB_FILTER_SINGLE_ENTRY):

        bibentries = bfile.bibentries().entries;

        for k,v in bibentries.iteritems():
            bibentries[k] = filtr.filter_bibentry(v);

        bfile.setentries(bibentries);

        logger.debug('filter '+filtr.name()+' filtered each of the the bibentries one by one.');
        continue

    raise ValueError("Bad value for BFilter.action(): "+repr(action));


# and output everything back to the original file.
bfile.save_to_file();


logger.debug('Done.');

