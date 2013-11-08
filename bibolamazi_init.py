
import sys
import os.path


if sys.hexversion < 0x02070000:
    sys.stderr.write("FATAL ERROR: Python 2.7 or later is required.\n")
    exit(254);

    
# setup python path correctly first.
# ----------------------------------
thisdir = os.path.dirname(os.path.realpath(__file__));
sys.path += [thisdir,
             thisdir + '/3rdparty/pybtex',
             thisdir + '/3rdparty/arxiv2bib',
             ];

