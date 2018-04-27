
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2018 by Philippe Faist                                       #
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

import os
import os.path
import re
import logging
import textwrap
from html import escape as htmlescape

import bibolamazi.init

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .qtauto.ui_filterpackagepatheditor import Ui_FilterPackagePathEditor

logger = logging.getLogger(__name__)



# ------------------------------------------------------------------------------



class FilterPackagePathEditor(QWidget):
    def __init__(self, parent):
        super(FilterPackagePathEditor, self).__init__(parent)

        self.ui = Ui_FilterPackagePathEditor()
        self.ui.setupUi(self)

    filterPackagePathChanged = pyqtSignal(str)

    @pyqtSlot(str, str)
    def setFilterPackageInfo(self, filterpkg, filterdir):
        self.ui.lblInfo.setText("<b>{}:</b> {}".format(htmlescape(str(filterpkg)),
                                                       htmlescape(str(filterdir))))

    @pyqtSlot()
    def on_btnChange_clicked(self):
        fpath = str(QFileDialog.getExistingDirectory(self, "Locate Filter Package", str()))
        HOME = os.path.expanduser("~/")
        fpath = re.sub(r'^'+re.escape(HOME), "~/", fpath)
        logger.debug("User selected fpath = %r", fpath)
        self.filterPackagePathChanged.emit(fpath)

        
    
