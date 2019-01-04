# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpbrowser.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_HelpBrowser(object):
    def setupUi(self, HelpBrowser):
        HelpBrowser.setObjectName("HelpBrowser")
        HelpBrowser.resize(600, 600)
        self.lyt = QtWidgets.QGridLayout(HelpBrowser)
        self.lyt.setContentsMargins(0, 0, 0, 0)
        self.lyt.setObjectName("lyt")
        self.tabs = QtWidgets.QTabWidget(HelpBrowser)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setObjectName("tabs")
        self.lyt.addWidget(self.tabs, 0, 0, 1, 1)

        self.retranslateUi(HelpBrowser)
        self.tabs.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(HelpBrowser)

    def retranslateUi(self, HelpBrowser):
        _translate = QtCore.QCoreApplication.translate
        HelpBrowser.setWindowTitle(_translate("HelpBrowser", "Bibolamazi Help & Reference"))

