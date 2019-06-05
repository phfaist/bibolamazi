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


import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *



class ContextAttributeSetter:
    """
    Context manager that temporarily sets some attributes and restores them to
    their original value after the context is finished.

    Give a list of pairs of method and value to set.

    For example::

        with ContextAttributeSetter( (object.isEnabled, object.setEnabled, False), ):
            ...

    will retreive the current state of if the object is enabled with
    `object.isEnabled()`, then will disable the object with
    `object.setEnabled(False)`. Upon exiting the with block, the state is
    restored to its original state with `object.setEnabled(..)`.
    """

    def __init__(self, *args):
        """
        Constructor. Does initializations. The \"enter\" statement is done with
        __enter__().

        The arguments `*args` are one or more 3-tuples `(get_method, set_method,
        set_to_value)`.  The current state of the property is queried with
        `get_method()`, the new state is set with `set_method(<value>)`, and
        `set_to_value` is the value that the property should be set to upon
        entering the execution context.
        """
        super().__init__()
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
    Context manager that temporarily block signals from Qt objects::

        with BlockedSignals(object1, object2, ...):
            # The Qt objects object1, object2, ... have their signals
            # temporarily blocked within this "with" statement
    """

    def __init__(self, *args):
        attrlist = [
            (obj.signalsBlocked, obj.blockSignals, True)
            for obj in args
        ]
        super().__init__( *attrlist )






def is_dark_mode(widget):
    """
    Return True if the given `widget` appears to be rendered in dark mode.

    Dark mode interface is determined by examining the brightness of the palette
    background color ("Base").
    """
    if widget is None:
        return False
    p = widget.palette()
    if p is None:
        return False
    if p.color(QPalette.Active, QPalette.Base).value() < 127:
        # dark Base color -> dark mode
        return True
    return False
