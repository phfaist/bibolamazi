#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path

sys.path += [os.path.realpath(os.path.join(os.path.dirname(__file__),'..'))]
import bibolamazi_init

from core import bibolamazifile


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
        if (True):
            ### TODO: check if is a mac
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
                QShortcut(QKeySequence('Ctrl+N'), self, self.on_btnNewFile_clicked, self.on_btnNewFile_clicked,
                          Qt.ApplicationShortcut),
                QShortcut(QKeySequence('Ctrl+O'), self, self.on_btnOpenFile_clicked, self.on_btnOpenFile_clicked,
                          Qt.ApplicationShortcut),
                QShortcut(QKeySequence('Ctrl+R'), self, self.on_btnHelp_clicked, self.on_btnHelp_clicked,
                          Qt.ApplicationShortcut),
                QShortcut(QKeySequence('Ctrl+Q'), self, self.on_btnQuit_clicked, self.on_btnQuit_clicked,
                          Qt.ApplicationShortcut),
                ]
        

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
        QApplication.instance().quit()


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

##         modified_w = []
##         for w in self.openbibfiles:
##             if (w.hasUnsavedModifications()):
##                 modified_w.append( (w, w.fileName()) )
##         if (len(modified_w)):
##             ans = QMessageBox.question(self, "Save Changes", "Save  .............

        super(MainWidget, self).closeEvent(event)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))
    app.setApplicationName('Bibolamazi')
    app.setApplicationVersion('0.1')
    app.setOrganizationDomain('org.bibolamazi')
    app.setOrganizationName('Bibolamazi Project')

    w = MainWidget()
    w.show()
    w.raise_()

    sys.exit(app.exec_())
