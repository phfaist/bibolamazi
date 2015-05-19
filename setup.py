from setuptools import setup, find_packages

import sys

#import bibolamazi.init # -- don't make the setup.py crash because some packages
#e.g. pybtex aren't available
from bibolamazi.core.version import version_str as bibolamaziversion_str

sys.stderr.write("""
Welcome to the setup.py script for Bibolamazi. This setup.py script will only
take care of compiling/installing the basic bibolamazi package and command-line
utility. For the graphical interface, use the `setup.py` script located in the
`gui/` directory, or download a precompiled version from
`https://github.com/phfaist/bibolamazi/releases/`.

NOTE: the `citeinspirehep` filter requires two additional packages, `requests`
and `beautifulsoup4`. Make sure you have installed these packages if you wish to
use this filter. (These packages are not listed as a requirement in the
`setup.py` because the rest of bibolamazi runs fine without.)

""")

setup(
    name = "bibolamazi",
    version = bibolamaziversion_str,

    # metadata for upload to PyPI
    author = "Philippe Faist",
    author_email = "philippe.faist@bluewin.ch",
    description = "Prepare consistent BibTeX files for your LaTeX documents",
    license = "GPL v3+",
    keywords = "bibtex latex bibliography consistent tidy formatting",
    url = "https://github.com/phfaist/bibolamazi/",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Editors :: Text Processing',
        'Topic :: Text Processing :: General',
    ],

    # could also include long_description, download_url, classifiers, etc.

    packages = find_packages(exclude=['bibolamazi_gui', 'bibolamazi_gui.*']),
    zip_safe = True,
    scripts = ['bin/bibolamazi'],

    install_requires = ['pybtex>=0.16', 'arxiv2bib>=1.0.2', 'pylatexenc>=0.9'],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    
)
