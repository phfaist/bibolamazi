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


import sys
import os
import os.path

sys.path += [os.path.realpath(os.path.join(os.path.dirname(__file__),'..'))]
import bibolamazi_init

from core import bibolamazifile
import core.version

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import openbibfile
import helpbrowser

from qtauto.ui_mainwidget import Ui_MainWidget

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        self.openbibfiles = []

        self.helpbrowser = None

        self.menubar = None
        self.shortcuts = []
        
        if (sys.platform == 'darwin'):
            # Mac OS X
            self.menubar = QMenuBar(None)
            filemenu = self.menubar.addMenu("File")
            filemenu.addAction("New", self, SLOT('on_btnNewFile_clicked()'),
                               QKeySequence("Ctrl+N"))
            filemenu.addAction("Open", self, SLOT('on_btnOpenFile_clicked()'),
                               QKeySequence("Ctrl+O"))
            helpmenu = self.menubar.addMenu("Help")
            helpmenu.addAction("Open Help Browser", self, SLOT('on_btnHelp_clicked()'),
                               QKeySequence("Ctrl+R"))
        else:
            self.shortcuts += [
                (QAction("New", self), "Ctrl+N", self.on_btnNewFile_clicked),
                (QAction("Open", self), "Ctrl+O", self.on_btnOpenFile_clicked),
                (QAction("Help", self), "Ctrl+R", self.on_btnHelp_clicked),
                (QAction("Quit", self), "Ctrl+Q", self.on_btnQuit_clicked),
                #
                # PyQt Bug: these shortcuts cause segfaults!! workaround: use QAction's instead.
                #
                #QShortcut(QKeySequence('Ctrl+N'), self, self.on_btnNewFile_clicked, self.on_btnNewFile_clicked,
                #          Qt.ApplicationShortcut),
                #QShortcut(QKeySequence('Ctrl+O'), self, self.on_btnOpenFile_clicked, self.on_btnOpenFile_clicked,
                #          Qt.ApplicationShortcut),
                #QShortcut(QKeySequence('Ctrl+R'), self, self.on_btnHelp_clicked, self.on_btnHelp_clicked,
                #          Qt.ApplicationShortcut),
                #QShortcut(QKeySequence('Ctrl+Q'), self, self.on_btnQuit_clicked, self.on_btnQuit_clicked,
                #          Qt.ApplicationShortcut),
                ]
            for (a, key, slot) in self.shortcuts:
                print 'adding action with key %s' %(key)
                a.setShortcut(QKeySequence(key))
                a.triggered.connect(slot)
                a.setShortcutContext(Qt.ApplicationShortcut)
                self.addAction(a)

        self.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))


    def openFile(self, fname):
        w = openbibfile.OpenBibFile()
        w.setOpenFile(fname)
        w.show()
        w.raise_()
        w.fileClosed.connect(self.bibFileClosed)
        self.openbibfiles.append(w)

        w.requestHelpTopic.connect(self.openHelpTopic)


    @pyqtSlot(QString)
    def openHelpTopic(self, path):
        self.on_btnHelp_clicked()
        self.helpbrowser.openHelpTopic(path)


    @pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fname = str(QFileDialog.getOpenFileName(self, 'Open Bibolamazi File', QString(),
                                                'Bibolamazi Files (*.bib);;All Files (*)'))
        if (fname):
            self.openFile(fname)
        
    @pyqtSlot()
    def on_btnNewFile_clicked(self):
        newfilename = str(QFileDialog.getSaveFileName(self, 'Create Bibolamazi File', QString(),
                                                      'Bibolamazi Files (*.bib);;All Files (*)'))
        if (not newfilename):
            # cancelled
            return

        if (os.path.exists(newfilename)):
            QMessageBox.critical(self, "File Exists",
                                 "Cowardly refusing to overwrite existing file `%s'. Remove it first."
                                 %(newfilename))
            return

        bfile = bibolamazifile.BibolamaziFile(newfilename, create=True);
        bfile.save_to_file();

        self.openFile(newfilename)

    @pyqtSlot()
    def on_btnHelp_clicked(self):
        if (not self.helpbrowser):
            self.helpbrowser = helpbrowser.HelpBrowser()
        self.helpbrowser.show()
        self.helpbrowser.raise_()

    @pyqtSlot()
    def on_btnQuit_clicked(self):
        self.close()


    @pyqtSlot()
    def bibFileClosed(self):
        sender = self.sender()
        if (not sender in self.openbibfiles):
            print "WARNING: Widget sender of fileClosed() not in our openbibfiles list!!"
            return
        print "file is closed."
        self.openbibfiles.remove(sender)

    def closeEvent(self, event):
        print "Close!!"

        for w in self.openbibfiles:
            ans = w.close()
            if not ans:
                # if the widget cancels the close, then abort
                event.ignore()
                return

        if (self.helpbrowser):
            self.helpbrowser.close()

        super(MainWidget, self).closeEvent(event)




def run_main():

    print "starting application"

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))
    app.setApplicationName('Bibolamazi')
    app.setApplicationVersion(core.version.version_str)
    app.setOrganizationDomain('org.bibolamazi')
    app.setOrganizationName('Bibolamazi Project')

    w = MainWidget()
    w.show()
    w.raise_()

    sys.exit(app.exec_())
    

if __name__ == '__main__':
    run_main()
