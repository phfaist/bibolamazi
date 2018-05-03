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


# see http://stackoverflow.com/a/14399775/1694896
def _parse_requires(fn):
    """
    Parse PIP requirements given in that file.  Nothing special, just splits lines and
    ignores those which start by '#'.
    """
    with open(fn) as f:
        required = f.read().splitlines()
    return [ r
             for r in required
             if r.strip() and r.lstrip()[:1] != '#'
    ]


install_requires = _parse_requires('pip_requirements.txt'),
#
sys.stderr.write("(Requirements: %s)\n\n\n" % (install_requires))


packages = find_packages(include=['bibolamazi', 'bibolamazi.*'],
                         exclude=['bibolamazi_gui', 'bibolamazi_gui.*'])
#print("packages = %r"%packages)

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

    packages = packages,
    zip_safe = True,

    #scripts = ['bin/bibolamazi'],
    entry_points = {
        'console_scripts': ['bibolamazi=bibolamazi.core.main:main'],
    },

    install_requires = install_requires,

    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        #'': ['*.txt', '*.rst'],
        # And include any *.msg files found in the 'hello' package, too:
        #'hello': ['*.msg'],
    },

    
)
