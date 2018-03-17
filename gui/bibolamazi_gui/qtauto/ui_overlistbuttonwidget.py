# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'overlistbuttonwidget.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_OverListButtonWidget(object):
    def setupUi(self, OverListButtonWidget):
        OverListButtonWidget.setObjectName("OverListButtonWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(OverListButtonWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnAdd = QtWidgets.QToolButton(OverListButtonWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/lstbtnadd.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAdd.setIcon(icon)
        self.btnAdd.setIconSize(QtCore.QSize(10, 16))
        self.btnAdd.setObjectName("btnAdd")
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnEdit = QtWidgets.QToolButton(OverListButtonWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/pic/lstbtnedit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEdit.setIcon(icon1)
        self.btnEdit.setIconSize(QtCore.QSize(10, 16))
        self.btnEdit.setObjectName("btnEdit")
        self.horizontalLayout.addWidget(self.btnEdit)
        self.btnRemove = QtWidgets.QToolButton(OverListButtonWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/pic/lstbtnremove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRemove.setIcon(icon2)
        self.btnRemove.setIconSize(QtCore.QSize(10, 16))
        self.btnRemove.setObjectName("btnRemove")
        self.horizontalLayout.addWidget(self.btnRemove)

        self.retranslateUi(OverListButtonWidget)
        QtCore.QMetaObject.connectSlotsByName(OverListButtonWidget)

    def retranslateUi(self, OverListButtonWidget):
        pass

from . import bibolamazi_res_rc
