
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


import os
import os.path
import logging
logger = logging.getLogger(__name__)


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import bibolamazi.init
from .qtauto.ui_sourcelisteditor import Ui_SourceListEditor


class SourceListEditor(QWidget):
    def __init__(self, parent):
        super(SourceListEditor, self).__init__(parent)

        self.ui = Ui_SourceListEditor()
        self.ui.setupUi(self)
        
        self.ui.btnAddFavorite.clicked.connect(self.requestAddToFavorites)

        QObject.connect(self.ui.lstSources.model(), SIGNAL('layoutChanged()'), self.update_stuff_moved)

        self._is_updating = False

        self._ref_dir = None


    sourceListChanged = pyqtSignal('QStringList')

    requestAddToFavorites = pyqtSignal()
    requestAddSourceList = pyqtSignal()
    

    def sourceList(self):
        return [str(self.ui.lstSources.item(i).text())  for i in xrange(self.ui.lstSources.count())]


    def setRefDir(self, refdir):
        """Sets the \"reference\" directory, which is the directory in which the bibolamazi
        file being edited resides. This is used to decide on whether to refer to a file with
        an absolute or a relative path.
        """
        self._ref_dir = refdir;
        

    @pyqtSlot(QStringList, bool)
    @pyqtSlot(QStringList)
    def setSourceList(self, sourcelist, noemit=False):
        sourcelist = [str(x) for x in list(sourcelist)];
        
        # don't reset source list if it's the same. In particular, don't emit the changed signal.
        if (sourcelist == self.sourceList()):
            return
        
        self._is_updating = True
        self.ui.lstSources.clear()
        for src in sourcelist:
            self.ui.lstSources.addItem(src)

        # refresh current row
        if len(sourcelist):
            self.ui.lstSources.setCurrentRow(0)
        else:
            self.on_lstSources_currentRowChanged(self.ui.lstSources.currentRow())

        self._is_updating = False
        if (not noemit):
            self.emitSourceListChanged()

    @pyqtSlot(int)
    def selectSourceAltLoc(self, index):
        """
        Select and focus input field for the alt loc identified by `index` in the list. Starts
        with zero.
        """
        self.ui.lstSources.setCurrentRow(index)
        self.ui.txtFile.setFocus()

    @pyqtSlot()
    def emitSourceListChanged(self):
        if (self._is_updating):
            return
        logger.debug("emitting sourceListChanged()!")
        self.sourceListChanged.emit(QStringList(self.sourceList()))


    @pyqtSlot()
    def on_btnAddSourceAltLoc_clicked(self):
        self.ui.lstSources.addItem("")
        self.ui.lstSources.setCurrentRow(self.ui.lstSources.count()-1)
        self.ui.txtFile.setFocus()
        self.emitSourceListChanged()

    @pyqtSlot()
    def on_btnRemoveSourceAltLoc_clicked(self):
        row = self.ui.lstSources.currentRow()
        if (row < 0):
            logger.debug("No row selected")
            return

        logger.debug('removing row %d', row)
        item = self.ui.lstSources.takeItem(row)
        # ###TODO: FIXME: delete item?!?

        self.emitSourceListChanged()

    @pyqtSlot()
    def on_btnAddSource_clicked(self):
        self.requestAddSourceList.emit()

    @pyqtSlot()
    def update_stuff_moved(self):
        # user moved stuff around
        logger.debug("Stuff moved around!")

        self.emitSourceListChanged()
        
    @pyqtSlot('QListWidgetItem*')
    def on_lstSources_itemDoubleClicked(self, item):
        logger.debug('double-clicked!!')
        self.ui.txtFile.setFocus()

    @pyqtSlot(int)
    def on_lstSources_currentRowChanged(self, row):
        logger.debug("current row changed.. row=%d", row)
        if (self.ui.lstSources.count() == 0  or  row < 0):
            self.ui.txtFile.setText("")
            self.ui.btnRemoveSourceAltLoc.setEnabled(False)
            self.ui.gbxEditSource.setEnabled(False)
        else:
            self.ui.btnRemoveSourceAltLoc.setEnabled(True)
            self.ui.gbxEditSource.setEnabled(True)
            self.ui.txtFile.setText(self.ui.lstSources.item(row).text())


    @pyqtSlot(QString)
    def on_txtFile_textChanged(self, text):
        row = self.ui.lstSources.currentRow()
        if (row < 0):
            logger.debug("No row selected")
            return

        item = self.ui.lstSources.item(row);
        if (item.text() != text):
            item.setText(text)
            self.emitSourceListChanged()

    @pyqtSlot()
    def on_btnBrowse_clicked(self):
        row = self.ui.lstSources.currentRow()
        if (row < 0):
            logger.debug("No row selected")
            return
        
        fname = str(QFileDialog.getOpenFileName(self, 'Select BibTeX File', QString(),
                                                'BibTeX Files (*.bib);;All Files (*)'))
        logger.debug("fname=%r.", fname)
        if (not fname):
            return

        # decide on whether to refer to file in absolute or relative fashion
        if (self._ref_dir):
            relpath = os.path.relpath(os.path.realpath(fname), os.path.realpath(self._ref_dir))
            if '..' in relpath.split(os.sep) or '..' in relpath.split(os.altsep):
                # out of scope, so use absolute.
                pass
            else:
                # can easily be referred to by relative path (in same or sub directory), use relative.
                fname = relpath

        self.ui.txtFile.setText(fname)
        
