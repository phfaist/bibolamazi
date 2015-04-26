
import sys
import os.path


if sys.hexversion < 0x02070000:
    sys.stderr.write("FATAL ERROR: Python 2.7 or later is required.\n")
    exit(254);


# subfolders of 3rdparty/ which we add to sys.path
third_party = ['pybtex',
               'arxiv2bib']


# This base dir of bibolamazi
base_dir = os.path.dirname(os.path.realpath(__file__));

# setup python path correctly first.
# ----------------------------------
sys.path += [base_dir]
sys.path += [os.path.join(base_dir, '3rdparty', x) for x in third_party]


# Make sure logging mechanism is set up (logger class correct)
# ------------------------------------------------------------
import core.blogger
