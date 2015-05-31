# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'overlistbuttonwidget.ui'
#
# Created: Sun May 31 15:09:07 2015
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

class Ui_OverListButtonWidget(object):
    def setupUi(self, OverListButtonWidget):
        OverListButtonWidget.setObjectName(_fromUtf8("OverListButtonWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(OverListButtonWidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnAdd = QtGui.QToolButton(OverListButtonWidget)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/lstbtnadd.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAdd.setIcon(icon)
        self.btnAdd.setIconSize(QtCore.QSize(10, 16))
        self.btnAdd.setObjectName(_fromUtf8("btnAdd"))
        self.horizontalLayout.addWidget(self.btnAdd)
        self.btnEdit = QtGui.QToolButton(OverListButtonWidget)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/lstbtnedit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEdit.setIcon(icon1)
        self.btnEdit.setIconSize(QtCore.QSize(10, 16))
        self.btnEdit.setObjectName(_fromUtf8("btnEdit"))
        self.horizontalLayout.addWidget(self.btnEdit)
        self.btnRemove = QtGui.QToolButton(OverListButtonWidget)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/lstbtnremove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRemove.setIcon(icon2)
        self.btnRemove.setIconSize(QtCore.QSize(10, 16))
        self.btnRemove.setObjectName(_fromUtf8("btnRemove"))
        self.horizontalLayout.addWidget(self.btnRemove)

        self.retranslateUi(OverListButtonWidget)
        QtCore.QMetaObject.connectSlotsByName(OverListButtonWidget)

    def retranslateUi(self, OverListButtonWidget):
        pass

from . import bibolamazi_res_rc
