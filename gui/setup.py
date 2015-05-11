from setuptools import setup, find_packages

import sys
import os.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.realpath(os.path.dirname(__file__)), '..')))

#import bibolamazi.init # -- don't make the setup.py crash because some packages
#e.g. pybtex aren't available
from bibolamazi.core import version as bibolamaziversion


setup(
    name = "bibolamazi_gui",
    version = bibolamaziversion.version_str,

    # metadata for upload to PyPI
    author = "Philippe Faist",
    author_email = "philippe.faist@bluewin.ch",
    description = "Prepare consistent BibTeX files for your LaTeX documents",
    license = "GPL v3+",
    keywords = "bibtex latex bibliography consistent tidy formatting",
    url = "https://github.com/phfaist/bibolamazi",
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

    packages = ['bibolamazi_gui', 'bibolamazi_gui.qtauto'],
    zip_safe = True,
    scripts = ['bin/bibolamazi_gui'],

    # make sure we have the same bibolamazi version. Since the GUI uses (some internals?)
    # of the bibolamazi library, make sure we have the same version.
    install_requires = ['PyQt4', 'bibolamazi=='+bibolamaziversion.version_str],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    
)
