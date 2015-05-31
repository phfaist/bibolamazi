# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwidget.ui'
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

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        MainWidget.setObjectName(_fromUtf8("MainWidget"))
        MainWidget.resize(491, 545)
        self.verticalLayout_3 = QtGui.QVBoxLayout(MainWidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lblMain = QtGui.QLabel(MainWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMain.sizePolicy().hasHeightForWidth())
        self.lblMain.setSizePolicy(sizePolicy)
        self.lblMain.setPixmap(QtGui.QPixmap(_fromUtf8(":/pic/bibolamazi.png")))
        self.lblMain.setObjectName(_fromUtf8("lblMain"))
        self.horizontalLayout.addWidget(self.lblMain)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.groupBox = QtGui.QGroupBox(MainWidget)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.btnOpenFile = QtGui.QPushButton(self.groupBox)
        self.btnOpenFile.setObjectName(_fromUtf8("btnOpenFile"))
        self.verticalLayout.addWidget(self.btnOpenFile)
        self.btnNewFile = QtGui.QPushButton(self.groupBox)
        self.btnNewFile.setObjectName(_fromUtf8("btnNewFile"))
        self.verticalLayout.addWidget(self.btnNewFile)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(MainWidget)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.btnSettings = QtGui.QPushButton(self.groupBox_2)
        self.btnSettings.setObjectName(_fromUtf8("btnSettings"))
        self.verticalLayout_2.addWidget(self.btnSettings)
        self.btnHelp = QtGui.QPushButton(self.groupBox_2)
        self.btnHelp.setObjectName(_fromUtf8("btnHelp"))
        self.verticalLayout_2.addWidget(self.btnHelp)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.btnQuit = QtGui.QPushButton(MainWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/closehide.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnQuit.setIcon(icon)
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.verticalLayout_3.addWidget(self.btnQuit)

        self.retranslateUi(MainWidget)
        QtCore.QMetaObject.connectSlotsByName(MainWidget)

    def retranslateUi(self, MainWidget):
        MainWidget.setWindowTitle(_translate("MainWidget", "Bibolamazi", None))
        self.groupBox.setTitle(_translate("MainWidget", "Open bibolamazi file or create new bibolamazi file", None))
        self.btnOpenFile.setText(_translate("MainWidget", "Open Bibolamazi File ...", None))
        self.btnNewFile.setText(_translate("MainWidget", "Create New Bibolamazi File ...", None))
        self.groupBox_2.setTitle(_translate("MainWidget", "Settings && Help", None))
        self.btnSettings.setText(_translate("MainWidget", "Settings", None))
        self.btnHelp.setText(_translate("MainWidget", "Help && Reference Browser", None))
        self.btnQuit.setText(_translate("MainWidget", "Quit", None))

from . import bibolamazi_res_rc
