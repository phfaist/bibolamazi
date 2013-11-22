# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'helpbrowser.ui'
#
# Created: Fri Nov 22 22:51:19 2013
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
        self.tabHome.setObjectName(_fromUtf8("tabHome"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.tabHome)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(80, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lytHomeButtons = QtGui.QVBoxLayout()
        self.lytHomeButtons.setObjectName(_fromUtf8("lytHomeButtons"))
        self.btnWelcome = QtGui.QPushButton(self.tabHome)
        self.btnWelcome.setProperty("helppath", _fromUtf8("general/welcome"))
        self.btnWelcome.setObjectName(_fromUtf8("btnWelcome"))
        self.lytHomeButtons.addWidget(self.btnWelcome)
        self.btnFilterList = QtGui.QPushButton(self.tabHome)
        self.btnFilterList.setProperty("helppath", _fromUtf8("general/filter-list"))
        self.btnFilterList.setObjectName(_fromUtf8("btnFilterList"))
        self.lytHomeButtons.addWidget(self.btnFilterList)
        self.line_2 = QtGui.QFrame(self.tabHome)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.lytHomeButtons.addWidget(self.line_2)
        self.scrollArea = QtGui.QScrollArea(self.tabHome)
        self.scrollArea.setFrameShape(QtGui.QFrame.NoFrame)
        self.scrollArea.setFrameShadow(QtGui.QFrame.Plain)
        self.scrollArea.setLineWidth(0)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName(_fromUtf8("scrollArea"))
        self.wFilters = QtGui.QWidget()
        self.wFilters.setGeometry(QtCore.QRect(0, 0, 585, 242))
        self.wFilters.setObjectName(_fromUtf8("wFilters"))
        self.lytHomeFilterButtons = QtGui.QVBoxLayout(self.wFilters)
        self.lytHomeFilterButtons.setContentsMargins(50, -1, 50, -1)
        self.lytHomeFilterButtons.setObjectName(_fromUtf8("lytHomeFilterButtons"))
        self.scrollArea.setWidget(self.wFilters)
        self.lytHomeButtons.addWidget(self.scrollArea)
        self.line = QtGui.QFrame(self.tabHome)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.lytHomeButtons.addWidget(self.line)
        spacerItem1 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.lytHomeButtons.addItem(spacerItem1)
        self.btnCmdLineHelp = QtGui.QPushButton(self.tabHome)
        self.btnCmdLineHelp.setProperty("helppath", _fromUtf8("general/cmdline"))
        self.btnCmdLineHelp.setObjectName(_fromUtf8("btnCmdLineHelp"))
        self.lytHomeButtons.addWidget(self.btnCmdLineHelp)
        self.btnVersion = QtGui.QPushButton(self.tabHome)
        self.btnVersion.setProperty("helppath", _fromUtf8("general/version"))
        self.btnVersion.setObjectName(_fromUtf8("btnVersion"))
        self.lytHomeButtons.addWidget(self.btnVersion)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.lytHomeButtons.addItem(spacerItem2)
        self.horizontalLayout.addLayout(self.lytHomeButtons)
        spacerItem3 = QtGui.QSpacerItem(120, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.tabs.addTab(self.tabHome, _fromUtf8(""))
        self.lyt.addWidget(self.tabs, 0, 0, 1, 1)

        self.retranslateUi(HelpBrowser)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(HelpBrowser)

    def retranslateUi(self, HelpBrowser):
        HelpBrowser.setWindowTitle(_translate("HelpBrowser", "Bibolamazi Help & Reference", None))
        self.btnWelcome.setText(_translate("HelpBrowser", "Welcome - basic Bibolamazi usage", None))
        self.btnFilterList.setText(_translate("HelpBrowser", "Annotated Filter List", None))
        self.btnCmdLineHelp.setText(_translate("HelpBrowser", "Bibolamazi command-line help", None))
        self.btnVersion.setText(_translate("HelpBrowser", "Bibolamazi Version", None))
        self.tabs.setTabText(self.tabs.indexOf(self.tabHome), _translate("HelpBrowser", "Home", None))

