# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'favoritesoverbtns.ui'
#
# Created: Tue Apr 22 10:45:39 2014
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

class Ui_FavoritesOverBtns(object):
    def setupUi(self, FavoritesOverBtns):
        FavoritesOverBtns.setObjectName(_fromUtf8("FavoritesOverBtns"))
        FavoritesOverBtns.resize(143, 26)
        self.horizontalLayout = QtGui.QHBoxLayout(FavoritesOverBtns)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(5, 10, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnEndEdit = QtGui.QToolButton(FavoritesOverBtns)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/ok.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEndEdit.setIcon(icon)
        self.btnEndEdit.setIconSize(QtCore.QSize(10, 16))
        self.btnEndEdit.setObjectName(_fromUtf8("btnEndEdit"))
        self.horizontalLayout.addWidget(self.btnEndEdit)
        self.btnEdit = QtGui.QToolButton(FavoritesOverBtns)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/lstbtnedit.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEdit.setIcon(icon1)
        self.btnEdit.setIconSize(QtCore.QSize(10, 16))
        self.btnEdit.setObjectName(_fromUtf8("btnEdit"))
        self.horizontalLayout.addWidget(self.btnEdit)
        spacerItem1 = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btnDelete = QtGui.QToolButton(FavoritesOverBtns)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/lstbtnremove.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnDelete.setIcon(icon2)
        self.btnDelete.setIconSize(QtCore.QSize(10, 16))
        self.btnDelete.setObjectName(_fromUtf8("btnDelete"))
        self.horizontalLayout.addWidget(self.btnDelete)
        self.btnInsert = QtGui.QToolButton(FavoritesOverBtns)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/rightarrow.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnInsert.setIcon(icon3)
        self.btnInsert.setIconSize(QtCore.QSize(30, 16))
        self.btnInsert.setObjectName(_fromUtf8("btnInsert"))
        self.horizontalLayout.addWidget(self.btnInsert)

        self.retranslateUi(FavoritesOverBtns)
        QtCore.QMetaObject.connectSlotsByName(FavoritesOverBtns)

    def retranslateUi(self, FavoritesOverBtns):
        self.btnEndEdit.setToolTip(_translate("FavoritesOverBtns", "Finish editing", None))
        self.btnEdit.setToolTip(_translate("FavoritesOverBtns", "Edit favorite commands", None))
        self.btnDelete.setToolTip(_translate("FavoritesOverBtns", "Delete this favorite command", None))
        self.btnInsert.setToolTip(_translate("FavoritesOverBtns", "Insert this favorite command at current position in config", None))

import bibolamazi_res_rc
