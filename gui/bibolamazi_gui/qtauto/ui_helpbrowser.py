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
        HelpBrowser.resize(857, 550)
        self.lyt = QtWidgets.QGridLayout(HelpBrowser)
        self.lyt.setContentsMargins(0, 0, 0, 0)
        self.lyt.setObjectName("lyt")
        self.tabs = QtWidgets.QTabWidget(HelpBrowser)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setObjectName("tabs")
        self.tabHome = QtWidgets.QWidget()
        self.tabHome.setStyleSheet("")
        self.tabHome.setObjectName("tabHome")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tabHome)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.scrlFilters = QtWidgets.QScrollArea(self.tabHome)
        self.scrlFilters.setStyleSheet("")
        self.scrlFilters.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.scrlFilters.setFrameShadow(QtWidgets.QFrame.Plain)
        self.scrlFilters.setLineWidth(0)
        self.scrlFilters.setWidgetResizable(True)
        self.scrlFilters.setObjectName("scrlFilters")
        self.wFilters = QtWidgets.QWidget()
        self.wFilters.setGeometry(QtCore.QRect(0, 0, 857, 527))
        self.wFilters.setStyleSheet("")
        self.wFilters.setObjectName("wFilters")
        self.lytHomeButtons = QtWidgets.QGridLayout(self.wFilters)
        self.lytHomeButtons.setContentsMargins(0, 0, 0, 0)
        self.lytHomeButtons.setObjectName("lytHomeButtons")
        self.btnWelcome = QtWidgets.QPushButton(self.wFilters)
        self.btnWelcome.setProperty("helppath", "general/welcome")
        self.btnWelcome.setObjectName("btnWelcome")
        self.lytHomeButtons.addWidget(self.btnWelcome, 0, 0, 1, 1)
        self.btnFilterList = QtWidgets.QPushButton(self.wFilters)
        self.btnFilterList.setProperty("helppath", "general/filter-list")
        self.btnFilterList.setObjectName("btnFilterList")
        self.lytHomeButtons.addWidget(self.btnFilterList, 0, 1, 1, 1)
        self.btnCmdLineHelp = QtWidgets.QPushButton(self.wFilters)
        self.btnCmdLineHelp.setProperty("helppath", "general/cmdline")
        self.btnCmdLineHelp.setObjectName("btnCmdLineHelp")
        self.lytHomeButtons.addWidget(self.btnCmdLineHelp, 1, 0, 1, 1)
        self.btnVersion = QtWidgets.QPushButton(self.wFilters)
        self.btnVersion.setProperty("helppath", "general/version")
        self.btnVersion.setObjectName("btnVersion")
        self.lytHomeButtons.addWidget(self.btnVersion, 1, 1, 1, 1)
        self.scrlFilters.setWidget(self.wFilters)
        self.horizontalLayout.addWidget(self.scrlFilters)
        self.tabs.addTab(self.tabHome, "")
        self.lyt.addWidget(self.tabs, 0, 0, 1, 1)

        self.retranslateUi(HelpBrowser)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(HelpBrowser)

    def retranslateUi(self, HelpBrowser):
        _translate = QtCore.QCoreApplication.translate
        HelpBrowser.setWindowTitle(_translate("HelpBrowser", "Bibolamazi Help & Reference"))
        self.btnWelcome.setText(_translate("HelpBrowser", "Welcome - basic Bibolamazi usage"))
        self.btnWelcome.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "intro"))
        self.btnFilterList.setText(_translate("HelpBrowser", "Annotated Filter List"))
        self.btnFilterList.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "intro"))
        self.btnCmdLineHelp.setText(_translate("HelpBrowser", "Bibolamazi command-line help"))
        self.btnCmdLineHelp.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "epilog"))
        self.btnVersion.setText(_translate("HelpBrowser", "Bibolamazi Version"))
        self.btnVersion.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "epilog"))
        self.tabs.setTabText(self.tabs.indexOf(self.tabHome), _translate("HelpBrowser", "Home"))

