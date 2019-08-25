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

from .uiutils import ContextAttributeSetter


class ButtonTabsManager(QObject):
    def __init__(self, container, parent=None):
        super().__init__()
    
        self.container = container
        self.buttons = []

        self._updating_buttons = False

        self.btngroup = QButtonGroup(self)
        self.btngroup.setExclusive(True)

        self.container.currentChanged.connect(self.containerCurrentChanged)


    def registerButton(self, btn, widgetInContainer):

        self.btngroup.addButton(btn)

        self.buttons.append( (btn, widgetInContainer) )

        btn_id = len(self.buttons)-1
        btn.setProperty("_flatbuttontabsmanager_id", btn_id)
        widgetInContainer.setProperty("_flatbuttontabsmanager_id", btn_id)

        cur_btn_id = self._get_cur_btn_id()
        btn.setChecked(cur_btn_id is not None and cur_btn_id == btn_id)

        btn.toggled.connect(self.tabButtonToggled)


    def _get_cur_btn_id(self):
        cur_w = self.container.currentWidget()
        if cur_w is None:
            return None
        cur_btn_id = cur_w.property("_flatbuttontabsmanager_id")
        if cur_btn_id is None:
            return None
        return int(cur_btn_id)


    @pyqtSlot()
    def containerCurrentChanged(self):
        btn_id = self._get_cur_btn_id()
        # for j in range(len(self.buttons)):
        #     b, w = self.buttons[j]
        #     with ContextAttributeSetter( (b.signalsBlocked,
        #                                   b.blockSignals, True) ):
        #         b.setChecked(btn_id is not None and j == btn_id)
        if btn_id is not None:
            b = self.buttons[btn_id][0]
            with ContextAttributeSetter( (lambda: self._updating_buttons,
                                          self._set_updating_buttons, True) ):

                # the button group will make sure the others get unchecked
                b.setChecked(True)

    def _set_updating_buttons(self, yn):
        self._updating_buttons = yn

    @pyqtSlot(bool)
    def tabButtonToggled(self, on):
        if self._updating_buttons:
            return

        btn = self.sender()
        btn_id = int(btn.property("_flatbuttontabsmanager_id"))

        if btn_id < 0 or btn_id >= len(self.buttons):
            logger.warning("button id %d out of range (%d)", btn_id, len(self.buttons))

        with ContextAttributeSetter( (self.container.signalsBlocked,
                                      self.container.blockSignals, True) ):
            self.container.setCurrentWidget(self.buttons[btn_id][1])
            self.containerCurrentChanged()
