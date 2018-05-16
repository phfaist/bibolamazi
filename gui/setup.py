from setuptools import setup, find_packages

import sys
import os.path
sys.path.insert(0, os.path.realpath(os.path.join(os.path.realpath(os.path.dirname(__file__)), '..')))

#import bibolamazi.init # -- don't make the setup.py crash because some packages
#e.g. pybtex aren't available
#from bibolamazi.core import version as bibolamaziversion
from bibolamazi_gui import version as bibolamaziversion

sys.stderr.write("""
NOTE: You'll have to make sure that `PyQt5` is installed in order to use
`bibolamazi_gui`. We unfortunately can't install this requirement automatically
when you run `pip install` because of technical issues.

""") # "technical issues" == https://stackoverflow.com/a/4628806/1694896


try:
    import PyQt5
except ImportError:
    sys.stderr.write("Please install PyQt5, for instance by running:\n\n    pip install pyqt5\n\n")
    raise RuntimeError("PyQt5 required")


setup(
    name = "bibolamazigui",
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
    #scripts = ['bin/bibolamazi_gui'],
    entry_points = {
        'console_scripts': ['bibolamazi_gui=bibolamazi_gui.bibolamazi_gui:main'],
    },


    # make sure we have the same bibolamazi version. Since the GUI uses (some internals?)
    # of the bibolamazi library, make sure we have the same version.
    #
    # we should NOT list PyQt5 here, because of https://stackoverflow.com/a/4628806/1694896 .
    install_requires = [
        'bibolamazi=='+bibolamaziversion.version_str,
        'markdown2',
    ],

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    
)
