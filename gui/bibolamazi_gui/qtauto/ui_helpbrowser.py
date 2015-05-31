# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpbrowser.ui'
#
# Created: Sun May 31 15:09:06 2015
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_HelpBrowser(object):
    def setupUi(self, HelpBrowser):
        HelpBrowser.setObjectName(_fromUtf8("HelpBrowser"))
        HelpBrowser.resize(857, 550)
        self.lyt = QtGui.QGridLayout(HelpBrowser)
        self.lyt.setMargin(0)
        self.lyt.setObjectName(_fromUtf8("lyt"))
        self.tabs = QtGui.QTabWidget(HelpBrowser)
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setMovable(True)
        self.tabs.setObjectName(_fromUtf8("tabs"))
        self.tabHome = QtGui.QWidget()
        self.tabHome.setStyleSheet(_fromUtf8(""))
        self.tabHome.setObjectName(_fromUtf8("tabHome"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tabHome)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.scrlFilters = QtGui.QScrollArea(self.tabHome)
        self.scrlFilters.setStyleSheet(_fromUtf8(""))
        self.scrlFilters.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrlFilters.setFrameShadow(QtGui.QFrame.Plain)
        self.scrlFilters.setLineWidth(0)
        self.scrlFilters.setWidgetResizable(True)
        self.scrlFilters.setObjectName(_fromUtf8("scrlFilters"))
        self.wFilters = QtGui.QWidget()
        self.wFilters.setGeometry(QtCore.QRect(0, 0, 857, 527))
        self.wFilters.setStyleSheet(_fromUtf8(""))
        self.wFilters.setObjectName(_fromUtf8("wFilters"))
        self.lytHomeButtons = QtGui.QGridLayout(self.wFilters)
        self.lytHomeButtons.setObjectName(_fromUtf8("lytHomeButtons"))
        self.btnWelcome = QtGui.QPushButton(self.wFilters)
        self.btnWelcome.setProperty("helppath", _fromUtf8("general/welcome"))
        self.btnWelcome.setObjectName(_fromUtf8("btnWelcome"))
        self.lytHomeButtons.addWidget(self.btnWelcome, 0, 0, 1, 1)
        self.btnFilterList = QtGui.QPushButton(self.wFilters)
        self.btnFilterList.setProperty("helppath", _fromUtf8("general/filter-list"))
        self.btnFilterList.setObjectName(_fromUtf8("btnFilterList"))
        self.lytHomeButtons.addWidget(self.btnFilterList, 0, 1, 1, 1)
        self.btnCmdLineHelp = QtGui.QPushButton(self.wFilters)
        self.btnCmdLineHelp.setProperty("helppath", _fromUtf8("general/cmdline"))
        self.btnCmdLineHelp.setObjectName(_fromUtf8("btnCmdLineHelp"))
        self.lytHomeButtons.addWidget(self.btnCmdLineHelp, 1, 0, 1, 1)
        self.btnVersion = QtGui.QPushButton(self.wFilters)
        self.btnVersion.setProperty("helppath", _fromUtf8("general/version"))
        self.btnVersion.setObjectName(_fromUtf8("btnVersion"))
        self.lytHomeButtons.addWidget(self.btnVersion, 1, 1, 1, 1)
        self.scrlFilters.setWidget(self.wFilters)
        self.horizontalLayout.addWidget(self.scrlFilters)
        self.tabs.addTab(self.tabHome, _fromUtf8(""))
        self.lyt.addWidget(self.tabs, 0, 0, 1, 1)

        self.retranslateUi(HelpBrowser)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(HelpBrowser)

    def retranslateUi(self, HelpBrowser):
        HelpBrowser.setWindowTitle(_translate("HelpBrowser", "Bibolamazi Help & Reference", None))
        self.btnWelcome.setText(_translate("HelpBrowser", "Welcome - basic Bibolamazi usage", None))
        self.btnWelcome.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "intro", None))
        self.btnFilterList.setText(_translate("HelpBrowser", "Annotated Filter List", None))
        self.btnFilterList.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "intro", None))
        self.btnCmdLineHelp.setText(_translate("HelpBrowser", "Bibolamazi command-line help", None))
        self.btnCmdLineHelp.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "epilog", None))
        self.btnVersion.setText(_translate("HelpBrowser", "Bibolamazi Version", None))
        self.btnVersion.setProperty("bibolamaziHelpButtonType", _translate("HelpBrowser", "epilog", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tabHome), _translate("HelpBrowser", "Home", None))

