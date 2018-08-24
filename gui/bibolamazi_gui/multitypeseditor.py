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

import logging


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#import bibolamazi.init

logger = logging.getLogger(__name__)




class MultiTypesEditorWidget(QWidget):
    def __init__(self, multitypesargtype, parent):
        super(MultiTypesEditorWidget, self).__init__(parent)

        from .filterinstanceeditor import RegisteredArgInputType

        self.setFocusPolicy(Qt.NoFocus)

        self.multitypesargtype = multitypesargtype
        self.typelist = multitypesargtype.typelist

        self.stk = QStackedWidget(self)

        self.typbtn = QToolButton(self)
        self.typbtn.setText("more")
        self.typbtn.setFocusPolicy(Qt.NoFocus)

        self.typmenu = QMenu(self.typbtn)

        factory = QItemEditorFactory()

        self.w = []
        self.wpropnames = []

        self.actiongroup = QActionGroup(self)
        self.actions = []

        for i, T in enumerate(self.typelist):
            t, s = T

            ww = None
            if hasattr(t, 'type_arg_input'):
                rr = RegisteredArgInputType(t, t())
                ww = rr.createWidget(self)
            else:
                qttypeid = QVariant(t()).userType()
                ww = factory.createEditor(qttypeid, self)
            self.stk.addWidget(ww)

            self.w.append(ww)
            self.wpropnames.append(factory.valuePropertyName(qttypeid))

            a = self.typmenu.addAction(s)
            a.setCheckable(True)
            a.setProperty('tindex', i)
            a.triggered.connect(self._set_typ_from_menu)
            self.actiongroup.addAction(a)
            self.actions.append(a)

        self.typbtn.setMenu(self.typmenu)
        self.typbtn.clicked.connect(self.typbtn.showMenu)

        self.tindex = 0

        self.hboxlayout = QHBoxLayout()
        self.hboxlayout.setContentsMargins(1,1,1,1)
        self.hboxlayout.setSpacing(2)
        self.hboxlayout.addWidget(self.stk)
        self.hboxlayout.addWidget(self.typbtn)
        self.hboxlayout.setStretch(0, 99)
        self.hboxlayout.setStretch(1, 0)

        self.setLayout(self.hboxlayout)


    @pyqtSlot()
    def _set_typ_from_menu(self):
        i = self.sender().property('tindex')
        self.tindex = i

        self.stk.setCurrentIndex(i)
        self.w[i].setFocus()


    def setTypeValue(self, typeobj, value):
        from .filterinstanceeditor import RegisteredArgInputType

        for i, T in enumerate(self.typelist):
            t, s = T

            if t is typeobj:
                # found type
                logger.debug("setTypeValue: %r, %r", typeobj, value)

                self.tindex = i
                self.stk.setCurrentIndex(i)
                self.actions[i].setChecked(True)

                if hasattr(t, 'type_arg_input'):
                    rr = RegisteredArgInputType(t, value)
                    rr.setEditorData(self.w[i])
                    self.w[i]
                else:
                    self.w[i].setProperty(self.wpropnames[i], value)

                self.w[i].setFocus()
                return

        raise ValueError("Invalid type: %r"%(typeobj))

    def setValue(self, value):
        t, v = self.multitypesargtype.parse_value_fn(value)
        self.setTypeValue(t, v)
        

    def getTypeValue(self):
        from .filterinstanceeditor import RegisteredArgInputType

        t = self.typelist[self.tindex][0]
        w = self.w[self.tindex]
        if hasattr(t, 'type_arg_input'):
            rr = RegisteredArgInputType(t, t())
            v = rr.valueOf(self.w[self.tindex])
        else:
            v = w.property(self.wpropnames[self.tindex])

        return (t, t(v))


