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

from qtauto.ui_settingswidget import Ui_SettingsWidget


class SettingsWidget(QDialog):
    def __init__(self, swu_interface, swu_sourcefilter_devel, parent=None):
        super(SettingsWidget, self).__init__(parent=parent)

        print "swu_interface=%r, swu_sourcefilter_devel=%r" %(swu_interface, swu_sourcefilter_devel)

        self.swu_interface = swu_interface
        self.swu_sourcefilter_devel = swu_sourcefilter_devel

        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        if (self.swu_interface is None or self.swu_sourcefilter_devel is None):
            self.ui.frmUpdates.setEnabled(False)
        else:
            self.ui.frmUpdates.setEnabled(True)
            self.ui.chkUpdates.setChecked(self.swu_interface.checkForUpdatesEnabled())
            self.ui.chkDevelUpdates.setChecked(self.swu_sourcefilter_devel.includeDevelReleases())
            self.swu_interface.checkForUpdatesEnabledChanged.connect(self.ui.chkUpdates.setChecked)


    @pyqtSlot(bool)
    def on_chkUpdates_toggled(self, val):
        if self.swu_interface:
            self.swu_interface.setCheckForUpdatesEnabled(val)

    @pyqtSlot(bool)
    def on_chkDevelUpdates_toggled(self, val):
        if self.swu_sourcefilter_devel:
            self.swu_sourcefilter_devel.setIncludeDevelReleases(val)
