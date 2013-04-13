#!/usr/bin/python

import os
import os.path
import sys


# setup python path correctly first.
# ----------------------------------
thisdir = os.path.dirname(os.path.realpath(__file__));
sys.path += [thisdir,
             thisdir + '/3rdparty/pybtex'];


if __name__ == "__main__":
    try:

        # run main program
        import core.main
        
    except:
        
        print
        print " -- ERROR --"
        print

        import traceback
        traceback.print_exc()

        # debugging post-mortem
        import pdb

        pdb.post_mortem();

