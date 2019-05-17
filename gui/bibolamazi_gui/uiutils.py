# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2013 by Philippe Faist                                       #
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

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr
import sys
def to_native_str(x): return x.encode('utf-8') if sys.version_info[0] <= 2 else x
def from_native_str(x): return x.decode('utf-8') if sys.version_info[0] <= 2 else x
from imp import reload

import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class ContextAttributeSetter(object):
    """Give a list of pairs of method and value to set.

    For example:

    >>> with ContextAttributeSetter( (object.isEnabled, object.setEnabled, False), ):
            ...

    will retreive the current state of if the object is enabled with `object.isEnabled()`, then
    will disable the object with `object.setEnabled(False)`. Upon exiting the with block, the
    state is restored to its original state with `object.setEnabled(..)`.

    """

    def __init__(self, *args):
        """Constructor. Does initializations. The \"enter\" statement is done with __enter__().

        Note: the argument are a list of 3-tuples `(get_method, set_method, set_to_value)`.
        """
        super(ContextAttributeSetter, self).__init__()
        self.attribpairs = args
        self.initvals = None

    def __enter__(self):
        self.initvals = []
        for (getm, setm, v) in self.attribpairs:
            self.initvals.append(getm())
            setm(v)
            
        return self

    def __exit__(self, type, value, traceback):
        # clean-up, go in reverse order
        N = len(self.attribpairs)
        for i in range(N):
            (getm, setm, v) = self.attribpairs[N-i-1]
            setm(self.initvals[N-i-1])




class BlockedSignals(ContextAttributeSetter):
    """
    with BlockedSignals(object1, object2, ...):
       # those Qt object's signals are temporarily blocked in this with statement.
    """

    def __init__(self, *args):
        attrlist = [
            (obj.signalsBlocked, obj.blockSignals, True)
            for obj in args
        ]
        super(BlockedSignals, self).__init__( *attrlist )






def is_dark_mode(widget):
    if widget is None:
        return False
    p = widget.palette()
    if p is None:
        return False
    if p.color(QPalette.Active, QPalette.Base).value() < 127:
        # dark Base color -> dark mode
        return True
    return False
