#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path

sys.path += [os.path.realpath(os.path.join(os.path.dirname(__file__),'..'))]
import bibolamazi_init

from core import bibfilterfile


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

        self.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))

        #QObject.connect(self.ui.btnOpenFile, SIGNAL('clicked()'), self.btnOpenFile_clicked)
        QObject.connect(self.ui.btnQuit, SIGNAL('clicked()'), app.quit)


    @pyqtSlot()
    def on_btnOpenFile_clicked(self):
        fname = str(QFileDialog.getOpenFileName(self))
        if (fname):
            self.openFile(fname)
        
    def openFile(self, fname):
        w = openbibfile.OpenBibFile()
        w.setOpenFile(fname)
        w.show()
        w.raise_()
        self.openbibfiles.append(w)

    @pyqtSlot()
    def on_btnNewFile_clicked(self):
        newfilename = str(QFileDialog.getSaveFileName(self))

        if (os.path.exists(newfilename)):
            QMessageBox.critical(self, "File Exists",
                                 "Cowardly refusing to overwrite existing file `%s'. Remove it first."
                                 %(newfilename))
            return

        bfile = bibfilterfile.BibFilterFile(newfilename, create=True);
        bfile.save_to_file();

        self.openFile(newfilename)

    @pyqtSlot()
    def on_btnHelp_clicked(self):
        if (not self.helpbrowser):
            self.helpbrowser = helpbrowser.HelpBrowser()
        self.helpbrowser.show()
        self.helpbrowser.raise_()


    def closeEvent(self, event):
        print "Close!!"
        super(MainWidget, self).closeEvent(event)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))

    w = MainWidget()
    w.show()
    w.raise_()

    sys.exit(app.exec_())
