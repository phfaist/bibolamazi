#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import os.path

sys.path += [os.path.realpath(os.path.join(os.path.dirname(__file__),'..'))]
import bibolamazi_init


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import openbibfile

from qtauto.ui_mainwidget import Ui_MainWidget

class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        self.openbibfiles = []

        QObject.connect(self.ui.btnQuit, SIGNAL('clicked()'), app.quit)


    def on_btnOpenFile_clicked(self):
        #fname = QFileDialog.getOpenFileName(self)
        w = openbibfile.OpenBibFile()
        w.setOpenFile('../test/output.bib')
        w.show()
        w.raise_()
        self.openbibfiles.append(w)
        

    def closeEvent(self, event):
        print "Close!!"
        super(MainWidget, self).closeEvent(event)



if __name__ == '__main__':

    app = QApplication(sys.argv)

    w = MainWidget()
    w.show()
    w.raise_()

    sys.exit(app.exec_())
