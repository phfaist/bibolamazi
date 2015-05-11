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

import sys
import os.path
import logging
logger = logging.getLogger(__name__)

from PyQt4.QtCore import *
from PyQt4.QtGui import *

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
            return QVariant()

        if role == Qt.BackgroundRole:
            valid = filters_factory.validate_filter_package(str(self._dic.item_at(row)[0]),
                                                            str(self._dic.item_at(row)[1]),
                                                            raise_exception=False)
            if not valid:
                return QVariant(QBrush(QColor(255,200,200)))
            return QVariant()

        if (col == 0):
            # argument name
            if (role == Qt.DisplayRole):
                return QVariant(QString(self._dic.item_at(row)[0]))

            # tool-tip documentation
            if (role == Qt.ToolTipRole):
                return QVariant(QString(self._dic.item_at(row)[0]))

            return QVariant()
        
        if (col == 1):
            # argument value

            if (role == Qt.DisplayRole or role == Qt.EditRole):
                val = self._dic.item_at(row)[1]
                if (val is None):
                    return QVariant()
                return QVariant(QString(str(val)))

            return QVariant()

        return QVariant()


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if (orientation == Qt.Vertical):
            return QVariant()

        if (section == 0):
            if (role == Qt.DisplayRole):
                return QVariant(QString(u"Filter Package"))
            return QVariant()

        if (section == 1):
            if (role == Qt.DisplayRole):
                return QVariant(QString(u"Path"))
            return QVariant()

        return QVariant()


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

        value = value.toPyObject()
        
        if (isinstance(value, QString)):
            value = unicode(value); # make sure we're dealing with Python strings and not Qt strings

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

    fpstr = str(s.value("filterpath").toString())

    for fp in reversed(fpstr.split(os.pathsep)):
        # if we had 'filters=' from some old version, then replace that by 'bibolamazi.filters='
        if fp == 'filters=':
            fp = 'bibolamazi.filters='

        main.setup_filterpackage_from_argstr(fp)

    s.endGroup()




class SettingsWidget(QDialog):
    def __init__(self, swu_interface, swu_sourcefilter_devel, mainwin=None):
        super(SettingsWidget, self).__init__(parent=mainwin)

        logger.debug("swu_interface=%r, swu_sourcefilter_devel=%r", swu_interface, swu_sourcefilter_devel)

        self.swu_interface = swu_interface
        self.swu_sourcefilter_devel = swu_sourcefilter_devel

        self.mainwin = mainwin

        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)

        # filter packages

        self.fpmodel = MyOrderedDictModel(filters_factory.filterpath)
        self.ui.lstFilterPackages.setModel(self.fpmodel)

        self.ui.lstFilterPackages.selectionModel().selectionChanged.connect(
            self.slot_lstFilterPackages_selectionChanged
            )
        self.slot_lstFilterPackages_selectionChanged()
        self.fpmodel.dicChanged.connect(self.save_settings)

        # software updates

        if (self.swu_interface is None or self.swu_sourcefilter_devel is None):
            self.ui.tabUpdates.setEnabled(False)
        else:
            self.ui.tabUpdates.setEnabled(True)
            self.ui.chkUpdates.setChecked(self.swu_interface.checkForUpdatesEnabled())
            self.ui.chkDevelUpdates.setChecked(self.swu_sourcefilter_devel.includeDevelReleases())
            self.swu_interface.checkForUpdatesEnabledChanged.connect(self.ui.chkUpdates.setChecked)


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

        thedir = str(QFileDialog.getExistingDirectory(self, "Locate Filter Package", QString()))

        thekey = os.path.basename(thedir)
        thedir = os.path.dirname(thedir)

        if thekey in filters_factory.filterpath:
            QMessageBox.critical(self, "There is already an existing filter package `%s'!", thekey)

        if thekey and thedir:
            filters_factory.filterpath[thekey] = str(thedir)
            self.ui.lstFilterPackages.reset();
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

        fpitems = filters_factory.filterpath.items()
        filters_factory.filterpath.clear()
        filters_factory.filterpath.update(reversed( fpitems[:row-1] + [fpitems[row], fpitems[row-1]] + fpitems[row+1:] ))
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

        fpitems = filters_factory.filterpath.items()
        filters_factory.filterpath.clear()
        filters_factory.filterpath.update(reversed( fpitems[:row] + [fpitems[row+1], fpitems[row]] + fpitems[row+2:] ))
        self.ui.lstFilterPackages.reset()
        self.save_settings()


    @pyqtSlot(bool)
    def on_chkUpdates_toggled(self, val):
        if self.swu_interface:
            self.swu_interface.setCheckForUpdatesEnabled(val)

    @pyqtSlot(bool)
    def on_chkDevelUpdates_toggled(self, val):
        if self.swu_sourcefilter_devel:
            self.swu_sourcefilter_devel.setIncludeDevelReleases(val)

    @pyqtSlot()
    def on_btnCheckNow_clicked(self):
        self.mainwin.doCheckForUpdates()



    @pyqtSlot()
    def save_settings(self):

        s = QSettings()

        s.beginGroup("BibolamaziCore")

        s.setValue("filterpath",
                   QVariant(QString(os.pathsep.join(( "%s=%s"%(k,v if v else "")
                                                      for k,v in filters_factory.filterpath.items() ))))
                   )
        # reset the filter cache.
        filters_factory.reset_filters_cache()

        s.endGroup()
        s.sync()
