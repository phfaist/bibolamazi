from setuptools import setup, find_packages

import sys

import bibolamazi.init
from bibolamazi.core import version as bibolamaziversion

sys.stderr.write("""

Welcome to the setup.py script for Bibolamazi. This setup.py script will only
take care of compiling/installing the basic bibolamazi package and command-line
utility. For the graphical interface, download a precompiled version from
https://github.com/phfaist/bibolamazi/releases/ or use the `setup.py` script
located in the gui/ directory.

""")

setup(
    name = "bibolamazi",
    version = bibolamaziversion.version_str,

    # metadata for upload to PyPI
    author = "Philippe Faist",
    author_email = "philippe.faist@bluewin.ch",
    description = "Prepare consistent BibTeX files for your LaTeX documents",
    license = "GPL v3+",
    keywords = "bibtex latex bibliography consistent tidy formatting",
    url = "https://github.com/phfaist/bibolamazi",
    classifiers=[
        'Development Status :: 5 - Stable',
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

    install_requires = [],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    
)
