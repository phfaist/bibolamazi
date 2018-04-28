# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'favoritesoverbtns.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FavoritesOverBtns(object):
    def setupUi(self, FavoritesOverBtns):
        FavoritesOverBtns.setObjectName("FavoritesOverBtns")
        FavoritesOverBtns.resize(197, 32)
        FavoritesOverBtns.setWindowOpacity(0.8)
        self.horizontalLayout = QtWidgets.QHBoxLayout(FavoritesOverBtns)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(5, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.btnEndEdit = QtWidgets.QToolButton(FavoritesOverBtns)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEndEdit.setIcon(icon)
        self.btnEndEdit.setIconSize(QtCore.QSize(10, 16))
        self.btnEndEdit.setObjectName("btnEndEdit")
        self.horizontalLayout.addWidget(self.btnEndEdit)
        self.btnEdit = QtWidgets.QToolButton(FavoritesOverBtns)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnEdit.sizePolicy().hasHeightForWidth())
        self.btnEdit.setSizePolicy(sizePolicy)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/pic/lstbtnedit.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnEdit.setIcon(icon1)
        self.btnEdit.setIconSize(QtCore.QSize(10, 16))
        self.btnEdit.setObjectName("btnEdit")
        self.horizontalLayout.addWidget(self.btnEdit)
        self.btnDelete = QtWidgets.QToolButton(FavoritesOverBtns)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/pic/lstbtnremove.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnDelete.setIcon(icon2)
        self.btnDelete.setIconSize(QtCore.QSize(10, 16))
        self.btnDelete.setObjectName("btnDelete")
        self.horizontalLayout.addWidget(self.btnDelete)
        spacerItem1 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btnInsert = QtWidgets.QPushButton(FavoritesOverBtns)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnInsert.sizePolicy().hasHeightForWidth())
        self.btnInsert.setSizePolicy(sizePolicy)
        self.btnInsert.setAutoFillBackground(True)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(":/pic/rightarrow.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnInsert.setIcon(icon3)
        self.btnInsert.setIconSize(QtCore.QSize(30, 16))
        self.btnInsert.setFlat(True)
        self.btnInsert.setObjectName("btnInsert")
        self.horizontalLayout.addWidget(self.btnInsert)

        self.retranslateUi(FavoritesOverBtns)
        QtCore.QMetaObject.connectSlotsByName(FavoritesOverBtns)

    def retranslateUi(self, FavoritesOverBtns):
        _translate = QtCore.QCoreApplication.translate
        self.btnEndEdit.setToolTip(_translate("FavoritesOverBtns", "Finish editing"))
        self.btnEdit.setToolTip(_translate("FavoritesOverBtns", "Edit favorite commands"))
        self.btnDelete.setToolTip(_translate("FavoritesOverBtns", "Delete this favorite command"))
        self.btnInsert.setToolTip(_translate("FavoritesOverBtns", "Insert this favorite command at current position in config"))
        self.btnInsert.setText(_translate("FavoritesOverBtns", "insert"))

from . import bibolamazi_res_rc
