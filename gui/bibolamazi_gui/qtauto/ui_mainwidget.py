# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwidget.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        MainWidget.setObjectName("MainWidget")
        MainWidget.resize(491, 545)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(MainWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.lblMain = QtWidgets.QLabel(MainWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblMain.sizePolicy().hasHeightForWidth())
        self.lblMain.setSizePolicy(sizePolicy)
        self.lblMain.setPixmap(QtGui.QPixmap(":/pic/bibolamazi.svg"))
        self.lblMain.setObjectName("lblMain")
        self.horizontalLayout.addWidget(self.lblMain)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.groupBox = QtWidgets.QGroupBox(MainWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnOpenFile = QtWidgets.QPushButton(self.groupBox)
        self.btnOpenFile.setObjectName("btnOpenFile")
        self.verticalLayout.addWidget(self.btnOpenFile)
        self.btnNewFile = QtWidgets.QPushButton(self.groupBox)
        self.btnNewFile.setObjectName("btnNewFile")
        self.verticalLayout.addWidget(self.btnNewFile)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(MainWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.btnSettings = QtWidgets.QPushButton(self.groupBox_2)
        self.btnSettings.setObjectName("btnSettings")
        self.verticalLayout_2.addWidget(self.btnSettings)
        self.btnHelp = QtWidgets.QPushButton(self.groupBox_2)
        self.btnHelp.setObjectName("btnHelp")
        self.verticalLayout_2.addWidget(self.btnHelp)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.btnQuit = QtWidgets.QPushButton(MainWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/closehide.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnQuit.setIcon(icon)
        self.btnQuit.setObjectName("btnQuit")
        self.verticalLayout_3.addWidget(self.btnQuit)

        self.retranslateUi(MainWidget)
        QtCore.QMetaObject.connectSlotsByName(MainWidget)

    def retranslateUi(self, MainWidget):
        _translate = QtCore.QCoreApplication.translate
        MainWidget.setWindowTitle(_translate("MainWidget", "Bibolamazi"))
        self.groupBox.setTitle(_translate("MainWidget", "Open bibolamazi file or create new bibolamazi file"))
        self.btnOpenFile.setText(_translate("MainWidget", "Open Bibolamazi File ..."))
        self.btnNewFile.setText(_translate("MainWidget", "Create New Bibolamazi File ..."))
        self.groupBox_2.setTitle(_translate("MainWidget", "Settings && Help"))
        self.btnSettings.setText(_translate("MainWidget", "Settings"))
        self.btnHelp.setText(_translate("MainWidget", "Help && Reference Browser"))
        self.btnQuit.setText(_translate("MainWidget", "Quit"))

from . import bibolamazi_res_rc
