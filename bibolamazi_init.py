
import sys
import os.path


if sys.hexversion < 0x02070000:
    sys.stderr.write("FATAL ERROR: Python 2.7 or later is required.\n")
    exit(254);


# subfolders of 3rdparty/ which we add to sys.path
third_party = ['pybtex',
               'arxiv2bib']

    
# setup python path correctly first.
# ----------------------------------
thisdir = os.path.dirname(os.path.realpath(__file__));
sys.path += [thisdir]
sys.path += [os.path.join(thisdir, '3rdparty', x) for x in third_party]
