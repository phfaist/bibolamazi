# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'startupwidget.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_StartupWidget(object):
    def setupUi(self, StartupWidget):
        StartupWidget.setObjectName("StartupWidget")
        StartupWidget.resize(421, 441)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(StartupWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lblMain = QtWidgets.QLabel(StartupWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMain.sizePolicy().hasHeightForWidth())
        self.lblMain.setSizePolicy(sizePolicy)
        self.lblMain.setPixmap(QtGui.QPixmap(":/pic/bibolamazi.png"))
        self.lblMain.setObjectName("lblMain")
        self.horizontalLayout.addWidget(self.lblMain)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        spacerItem2 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem2)
        self.frame = QtWidgets.QFrame(StartupWidget)
        self.frame.setObjectName("frame")
        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.gridLayout.setHorizontalSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.btnOpenFile = QtWidgets.QPushButton(self.frame)
        self.btnOpenFile.setObjectName("btnOpenFile")
        self.gridLayout.addWidget(self.btnOpenFile, 0, 0, 1, 1)
        self.btnNewFile = QtWidgets.QPushButton(self.frame)
        self.btnNewFile.setObjectName("btnNewFile")
        self.gridLayout.addWidget(self.btnNewFile, 1, 0, 1, 2)
        self.btnOpenRecent = QtWidgets.QPushButton(self.frame)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnOpenRecent.sizePolicy().hasHeightForWidth())
        self.btnOpenRecent.setSizePolicy(sizePolicy)
        self.btnOpenRecent.setObjectName("btnOpenRecent")
        self.gridLayout.addWidget(self.btnOpenRecent, 0, 1, 1, 1)
        self.verticalLayout_3.addWidget(self.frame)
        spacerItem3 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem3)
        self.frame_2 = QtWidgets.QFrame(StartupWidget)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.btnSettings = QtWidgets.QPushButton(self.frame_2)
        self.btnSettings.setObjectName("btnSettings")
        self.gridLayout_2.addWidget(self.btnSettings, 0, 0, 1, 1)
        self.btnHelp = QtWidgets.QPushButton(self.frame_2)
        self.btnHelp.setObjectName("btnHelp")
        self.gridLayout_2.addWidget(self.btnHelp, 1, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.frame_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_3.addItem(spacerItem4)
        spacerItem5 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem5)
        self.btnQuit = QtWidgets.QPushButton(StartupWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/closehide.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnQuit.setIcon(icon)
        self.btnQuit.setObjectName("btnQuit")
        self.verticalLayout_3.addWidget(self.btnQuit)

        self.retranslateUi(StartupWidget)
        QtCore.QMetaObject.connectSlotsByName(StartupWidget)

    def retranslateUi(self, StartupWidget):
        _translate = QtCore.QCoreApplication.translate
        StartupWidget.setWindowTitle(_translate("StartupWidget", "Bibolamazi"))
        self.btnOpenFile.setText(_translate("StartupWidget", "Open Bibolamazi File"))
        self.btnNewFile.setText(_translate("StartupWidget", "Create New Bibolamazi File ..."))
        self.btnOpenRecent.setText(_translate("StartupWidget", "..."))
        self.btnSettings.setText(_translate("StartupWidget", "Settings"))
        self.btnHelp.setText(_translate("StartupWidget", "Help && Reference Browser"))
        self.btnQuit.setText(_translate("StartupWidget", "Quit"))


from . import bibolamazi_res_rc
