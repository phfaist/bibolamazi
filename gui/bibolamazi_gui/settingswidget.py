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
import os.path
import logging
logger = logging.getLogger(__name__)

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import bibolamazi.init
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core import main

from .qtauto.ui_settingswidget import Ui_SettingsWidget


def get_typewriter_font(widget):
    """
    Return a `QFont` with a typewriter font such as Courier. Use some educated guesses for
    choosing a nice font.
    """
    font = widget.font() # default widget font
    font.setStyleHint(QFont.TypeWriter)
    if sys.platform.startswith("darwin"):
        font.setFamily("Menlo")
        font.setPointSize(12)
    else:
        font.setFamily("Monospace")

    return font


# Model to interface a python dictionary with a `set_at()' method, like our
# `filters.PrependOrderedDict`.
#
class MyOrderedDictModel(QAbstractTableModel):
    def __init__(self, dic, parent=None):
        super(MyOrderedDictModel, self).__init__(parent)
        self._dic = dic

    dicChanged = pyqtSignal()

    def rowCount(self, parent):
        if parent.isValid():
            return 0
        return len(self._dic)

    def columnCount(self, parent):
        if parent.isValid():
            return 0
        return 2

    def data(self, index, role=Qt.DisplayRole):

        col = index.column()
        row = index.row()

        if (row < 0 or row >= len(self._dic)):
            return None

        if role == Qt.BackgroundRole:
            valid = filters_factory.validate_filter_package(str(self._dic.item_at(row)[0]),
                                                            str(self._dic.item_at(row)[1]),
                                                            raise_exception=False)
            if not valid:
                return QBrush(QColor(255,200,200))
            return None

        if (col == 0):
            # argument name
            if (role == Qt.DisplayRole):
                return self._dic.item_at(row)[0]

            # tool-tip documentation
            if (role == Qt.ToolTipRole):
                return self._dic.item_at(row)[0]

            return None
        
        if (col == 1):
            # argument value

            if (role == Qt.DisplayRole or role == Qt.EditRole):
                val = self._dic.item_at(row)[1]
                if (val is None):
                    return None
                return str(val)

            return None

        return None


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if (orientation == Qt.Vertical):
            return None

        if (section == 0):
            if (role == Qt.DisplayRole):
                return u"Filter Package"
            return None

        if (section == 1):
            if (role == Qt.DisplayRole):
                return u"Path"
            return None

        return None


    def flags(self, index):
        col = index.column()
        row = index.row()

        if col in (0,1,):
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

        logger.warning("MyOrderedDictModel.flags(): MyOrderedDictModel.flags(): BAD COLUMN: %d", col)
        return 0
    

    def setData(self, index, value, role=Qt.EditRole):
        
        col = index.column()
        row = index.row()

        if col not in (0,1):
            return False

        if (role != Qt.EditRole):
            return False

        if (row < 0 or row >= len(filters_factory.filterpath)):
            return False

        logger.debug("Got value: %r", value)

        if col == 0:
            self._dic.set_at(row, value, self._dic.item_at(row)[1])
        if col == 1:
            self._dic.set_at(row, self._dic.item_at(row)[0], value)

        self.dataChanged.emit(index, index)

        self.dicChanged.emit()

        return True





def setup_filterpackages_from_settings(s):

    s.beginGroup("BibolamaziCore")

    sval = s.value("filterpath")
    if sval is None:
        fpstr = ''
    else:
        fpstr = str(sval)

    for fp in reversed(fpstr.split(os.pathsep)):
        # if we had 'filters=' from some old version, then replace that by 'bibolamazi.filters='
        if fp == 'filters=':
            fp = 'bibolamazi.filters='

        if not fp: # ignore truly empty entries
            continue

        logger.debug("Adding filter package from settings: fp=\"%s\"", fp)
        main.setup_filterpackage_from_argstr(fp)

    s.endGroup()




class SettingsWidget(QDialog):
    def __init__(self, bibapp=None):
        super(SettingsWidget, self).__init__()

        self.bibapp = bibapp

        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        # general

        self.ui.spnMaxRecentFiles.setValue(bibapp.recentFilesList.max_recent_files)

        # filter packages

        self.fpmodel = MyOrderedDictModel(filters_factory.filterpath)
        self.ui.lstFilterPackages.setModel(self.fpmodel)

        self.ui.lstFilterPackages.selectionModel().selectionChanged.connect(
            self.slot_lstFilterPackages_selectionChanged
            )
        self.slot_lstFilterPackages_selectionChanged()
        self.fpmodel.dicChanged.connect(self.save_settings)


    def filterpackages_selected_rows(self):
        idxlist = self.ui.lstFilterPackages.selectedIndexes()
        rows = set([i.row() for i in idxlist])
        return list(rows)

    @pyqtSlot()
    def slot_lstFilterPackages_selectionChanged(self):
        if not self.ui.lstFilterPackages.selectionModel().hasSelection():
            self.ui.btnFilterPackageRemove.setEnabled(False)
            self.ui.btnFilterPackageMoveUp.setEnabled(False)
            self.ui.btnFilterPackageMoveDown.setEnabled(False)
            return

        self.ui.btnFilterPackageRemove.setEnabled(True)
        idx = self.filterpackages_selected_rows()
        if len(idx) == 1:
            self.ui.btnFilterPackageMoveUp.setEnabled(idx[0] > 0)
            self.ui.btnFilterPackageMoveDown.setEnabled(idx[0] < len(filters_factory.filterpath)-1)
        else:
            self.ui.btnFilterPackageMoveUp.setEnabled(False)
            self.ui.btnFilterPackageMoveDown.setEnabled(False)
        

    @pyqtSlot()
    def on_btnFilterPackageAdd_clicked(self):

        thedir = str(QFileDialog.getExistingDirectory(self, "Locate Filter Package", str()))

        thekey = os.path.basename(thedir)
        thedir = os.path.dirname(thedir)

        if thekey in filters_factory.filterpath:
            QMessageBox.critical(self, "There is already an existing filter package `%s'!", thekey)

        if thekey and thedir:
            filters_factory.filterpath[thekey] = str(thedir)
            self.ui.lstFilterPackages.reset()
            self.save_settings()

    @pyqtSlot()
    def on_btnFilterPackageRemove_clicked(self):
        idxlist = self.filterpackages_selected_rows()
        if not len(idxlist):
            return

        for idx in idxlist:
            yn = QMessageBox.question(self, "Remove filter package?",
                                      ("Unset filter package %s? The files will not be removed, "
                                      "they will just be ignored by bibolamazi.") % (
                                          filters_factory.filterpath.item_at(idx)[0]
                                          ),
                                      QMessageBox.Yes|QMessageBox.Cancel, QMessageBox.Cancel)
            if yn != QMessageBox.Yes:
                continue
            
            del filters_factory.filterpath[filters_factory.filterpath.item_at(idx)[0]]
            self.ui.lstFilterPackages.reset()
            self.save_settings()

    @pyqtSlot()
    def on_btnFilterPackageMoveUp_clicked(self):
        idxlist = self.filterpackages_selected_rows()
        if len(idxlist) != 1:
            return
        row = idxlist[0]

        if row == 0:
            return

        fpitems = list(filters_factory.filterpath.items())
        filters_factory.filterpath.clear()
        filters_factory.filterpath.update(reversed( fpitems[:row-1] + [fpitems[row], fpitems[row-1]]
                                                    + fpitems[row+1:] ))
        self.ui.lstFilterPackages.reset()
        self.save_settings()
        
    @pyqtSlot()
    def on_btnFilterPackageMoveDown_clicked(self):
        idxlist = self.filterpackages_selected_rows()
        if len(idxlist) != 1:
            return
        row = idxlist[0]

        if row >= len(filters_factory.filterpath)-1:
            return

        fpitems = list(filters_factory.filterpath.items())
        filters_factory.filterpath.clear()
        filters_factory.filterpath.update(reversed( fpitems[:row] + [fpitems[row+1], fpitems[row]]
                                                    + fpitems[row+2:] ))
        self.ui.lstFilterPackages.reset()
        self.save_settings()


    @pyqtSlot(int)
    def on_spnMaxRecentFiles_valueChanged(self, num):
        self.bibapp.recentFilesList.max_recent_files = int(num)

    @pyqtSlot()
    def save_settings(self):

        s = QSettings()

        # max_recent_files is saved along with the recent files themselves

        s.beginGroup("BibolamaziCore")

        s.setValue("filterpath",
                   os.pathsep.join(( "%s=%s"%(k, v if v else "")
                                     for k,v in filters_factory.filterpath.items() ))
                   )
        # reset the filter cache.
        filters_factory.reset_filters_cache()

        s.endGroup()
        s.sync()
