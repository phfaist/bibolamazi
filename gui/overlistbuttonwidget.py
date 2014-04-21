
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


from PyQt4.QtCore import *
from PyQt4.QtGui import *


from qtauto.ui_overlistbuttonwidget import Ui_OverListButtonWidget


ROLE_OVERBUTTON = Qt.UserRole + 137

OVERBUTTON_NONE = 0
OVERBUTTON_ADD = 1
OVERBUTTON_REMOVE = 2

ROLE_ARGNAME = Qt.UserRole + 138


class OverListButtonWidgetBase(QWidget):
    def __init__(self, itemview):
        super(OverListButtonWidgetBase, self).__init__(itemview.viewport())
        self.hide()

        self._view = itemview
        self._view_viewport = self._view.viewport()
        self._view_viewport.setMouseTracking(True)
        self._view_viewport.installEventFilter(self)

        self._lastpos = None
        self._curidx = None

    def curIndex(self):
        return self._curidx

    def itemView(self):
        return self._view

    def eventFilter(self, obj, event):

        if (obj == self._view_viewport):
            if (event.type() == QEvent.FocusOut):
                self.hide()
            if (event.type() == QEvent.MouseMove):
                self.updateDisplay(event.pos())
            if (event.type() == QEvent.Leave):
                self.updateDisplay(False)

        return super(OverListButtonWidgetBase, self).eventFilter(obj, event)

    @pyqtSlot()
    def updateDisplay(self, pos=None):
        if (pos is None):
            pos = self._lastpos
        elif pos is False:
            pos = None
        self._lastpos = pos

        if pos is None:
            self._disappear()
            return
            
        idx = self._view.indexAt(pos)
        if (self.show_status(idx)):
            self._appear(idx)
            return True
        # else:
        self._disappear()
        return False


    def show_status(self, index):
        return False

    def _disappear(self):
        self._curidx = None
        self.hide()

    def _appear(self, idx):
        self.show()
        rect = self._view.visualRect(idx)
        sh = self.minimumSizeHint()
        rect.setLeft(rect.right()-sh.width())
        self.setGeometry(rect)
        self._curidx = idx






class OverListButtonWidget(OverListButtonWidgetBase):
    def __init__(self, itemview):
        super(OverListButtonWidget, self).__init__(itemview)

        self.ui = Ui_OverListButtonWidget()
        self.ui.setupUi(self)


    addClicked = pyqtSignal('QString')
    editClicked = pyqtSignal('QString')
    removeClicked = pyqtSignal('QString')
    addIndexClicked = pyqtSignal('QModelIndex')
    editIndexClicked = pyqtSignal('QModelIndex')
    removeIndexClicked = pyqtSignal('QModelIndex')
    

    def show_status(self, idx):
        if (not idx.isValid()):
            return False
        
        v = idx.data(ROLE_OVERBUTTON)
        if (not v.isValid()):
            return False
        
        whichbtn = v.toPyObject()

        if (whichbtn == OVERBUTTON_ADD):
            self.ui.btnAdd.show()
            self.ui.btnEdit.hide()
            self.ui.btnRemove.hide()
            return True
        if (whichbtn == OVERBUTTON_REMOVE):
            self.ui.btnAdd.hide()
            self.ui.btnEdit.show()
            self.ui.btnRemove.show()
            return True

        return False
    

    @pyqtSlot()
    def on_btnAdd_clicked(self):
        curidx = self.curIndex()
        if (curidx is None):
            return
        self.addIndexClicked.emit(curidx)
        self.addClicked.emit(curidx.data(ROLE_ARGNAME).toString())

    @pyqtSlot()
    def on_btnEdit_clicked(self):
        curidx = self.curIndex()
        if (curidx is None):
            return
        self.editIndexClicked.emit(curidx)
        self.editClicked.emit(curidx.data(ROLE_ARGNAME).toString())

    @pyqtSlot()
    def on_btnRemove_clicked(self):
        curidx = self.curIndex()
        if (curidx is None):
            return
        self.removeIndexClicked.emit(curidx)
        self.removeClicked.emit(curidx.data(ROLE_ARGNAME).toString())


    
        
