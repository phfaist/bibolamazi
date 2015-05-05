################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2015 by Philippe Faist                                       #
#   philippe.faist@bluewin.ch                                                  #
#                                                                              #
#   Bibolamazi is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   Bibolamazi is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with Bibolamazi.  If not, see <http://www.gnu.org/licenses/>.        #
#                                                                              #
################################################################################


"""
Initialization module

This module is imported before any other bibolamazi module, just to make sure we have
all the proper dependent modules set up, or to include our pre-packaged versions if need
be.

In fact, all bibolamazi modules import this module, so you don't even have to worry
about importing it first.
"""


import sys

if sys.hexversion < 0x02070000:
    sys.stderr.write("FATAL ERROR: Python 2.7 or later is required to run bibolamazi.\n")
    sys.exit(254);


import os.path
import importlib


# subfolders of 3rdparty/ which we add to sys.path
third_party = [
    'pybtex',
    'arxiv2bib',
    'pylatexenc',
]

# This base dir of bibolamazi
base_dir = os.path.dirname(__file__)


# setup python path correctly.
# ----------------------------
for mod in third_party:
    try:
        importlib.import_module(mod)
        continue
    except ImportError:
        # no such package--attempt to use pre-packaged version
        sys.path += [os.path.abspath(os.path.join(base_dir, '..', '3rdparty', mod))]
        importlib.import_module(mod)


#
# Patch for pybtex. Add __delitem__ to a OrderedCaseInsensitiveDict so that we can erase
# fields in entry.fields
#
import pybtex.utils as _pybtex_utils
def _OrderedCaseInsensitiveDict_delitem(self, key):
    # find item
    key_match = [k for k in self.order if k.lower() == key.lower()]
    if len(key_match) == 0:
        raise KeyError(key)
    assert (len(key_match) == 1), "Multiple instances of same key in dictionary: %s"%(key)
    # now we have the key with the right case
    key_ok = key_match[0]
    self.order.remove(key_ok)
    super(_pybtex_utils.OrderedCaseInsensitiveDict, self).__delitem__(key_ok)
    
_pybtex_utils.OrderedCaseInsensitiveDict.__delitem__ = _OrderedCaseInsensitiveDict_delitem;


# add the LONGDEBUG level, and set our custom logger class
# --------------------------------------------------------
from .core import blogger as _blogger

