#!/usr/bin/env python
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
import os
import os.path
import re
import logging
import subprocess
import datetime

logger = logging.getLogger(__name__)

import bibolamazi.init

from bibolamazi.core import bibolamazifile
from bibolamazi.core import main
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core.bibfilter import argtypes
from bibolamazi.core import version as bibolamaziversion



from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#print("loaded Qt. executable=", sys.executable, ' meipass=', sys._MEIPASS)

from . import openbibfile
from . import helpbrowser
from . import settingswidget

from .favorites import FavoriteCmdsList
from .newbibolamazifiledialog import NewBibolamazifileDialog

from .qtauto.ui_startupwidget import Ui_StartupWidget


class StartupWidget(QWidget):
    def __init__(self, bibapp):
        super(StartupWidget, self).__init__()

        self.bibapp = bibapp

        self.ui = Ui_StartupWidget()
        self.ui.setupUi(self)

        # set up nice vector graphics on retina displays
        if sys.platform.startswith("darwin"):
            # use high-res SVG for retina displays
            retinaresolution = find_retina_resolution()
            if retinaresolution is not None:
                mydesktop = QApplication.desktop()
                # seems that myratio is not reliable (I get 1.77777..), so just use 2x
                #myratio = float(retinaresolution[0]) / mydesktop.width()
                myratio = 2
                logger.debug('myratio=%r', myratio)
                #if myratio > 1.01:
                self.mypict = QPicture()
                mypaint = QPainter(self.mypict)
                self.myicon = QIcon(":/pic/bibolamazi.svg")
                mysize = QSize(375, 150)
                mypaint.drawPixmap(QRect(QPoint(0,0),mysize), self.myicon.pixmap(myratio*mysize))
                self.ui.lblMain.setPicture(self.mypict)

        self.ui.btnOpenFile.clicked.connect(bibapp.selectOpenFile)
        self.ui.btnNewFile.clicked.connect(bibapp.createNewFile)

        self.recentfilesbtnmenu = QMenu(parent=self)
        self.bibapp.setRecentFilesMenu(self.recentfilesbtnmenu)
        self.bibapp.recentFilesAvailable.connect(self.ui.btnOpenRecent.setEnabled)
        self.ui.btnOpenRecent.setMenu(self.recentfilesbtnmenu)
        self.ui.btnOpenRecent.clicked.connect(self.ui.btnOpenRecent.showMenu)

        self.ui.btnSettings.clicked.connect(bibapp.openSettings)
        self.ui.btnHelp.clicked.connect(bibapp.openHelpBrowser)

        self.ui.btnQuit.clicked.connect(bibapp.quit_app)

        for a in bibapp.myactions.values():
            self.addAction(a)

        if not sys.platform.startswith('darwin'):
            # NOT mac OS X, no application menu bar.
            # Simply set up the shortcuts
            for a in bibapp.myactions.values():
                a.setShortcutContext(Qt.ApplicationShortcut)

        self.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))

    def showAndRaise(self):
        self.show()
        self.raise_()

    def closeEvent(self, event):
        # Initiate an application quit if either:
        # - there are no files open any more OR 
        # - if we're not on a mac (and hence there is no app menu bar)
        if not self.bibapp.hasOpenFiles() or not sys.platform.startswith('darwin'):
            event.ignore()
            # get out of event loop first, though -> QTimer
            QTimer.singleShot(100, self.bibapp.quit_app)
            return

        super(StartupWidget, self).closeEvent(event)

#


def find_retina_resolution():
    try:
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
    except Exception as e:
        logger.info("Couldn't check for retina display: %s", e)
        return
    logger.debug("Got display information:\n%s", output)

    mres = re.search(r'Resolution:\s*(?P<resX>\d+)\s*x\s*(?P<resY>\d+)\s*(?P<retina>.*Retina)',
                     output, flags=re.IGNORECASE)

    if not mres.group('retina'):
        # couldn't confirm it's Retina, try "Retina: Yes/No" field
        mretina = re.search(r'Retina:\s*(?P<answer>Yes|No)', output, flags=re.IGNORECASE)
        if not mretina:
            return None

    # yes, retina
    logger.debug('got res=(%d,%d)', int(mres.group('resX')), int(mres.group('resY')))

    return (int(mres.group('resX')), int(mres.group('resY')))

