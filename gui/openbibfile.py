
# -*- coding: utf-8 -*-

import sys


import core.main;


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qtauto.ui_openbibfile import Ui_OpenBibFile

class OpenBibFile(QWidget):
    def __init__(self):
        super(OpenBibFile, self).__init__()

        print "open file widget constructor!"

        self.u = Ui_OpenBibFile()
        self.u.setupUi(self)

        self.bibolamaziFile = None


    def setOpenFile(self, filename):
        self.bibolamaziFile = filename
        

    def on_btnGo_clicked(self):
        print "btnGo!"
        if (not self.bibolamaziFile):
            QMessageBox.critical(self, "No open file", "No file selected!")

        QMessageBox.information(self, "No open file", "File is %r!"%(self.bibolamaziFile))

        return None
