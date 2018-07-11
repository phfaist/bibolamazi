# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sourcelisteditor.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SourceListEditor(object):
    def setupUi(self, SourceListEditor):
        SourceListEditor.setObjectName("SourceListEditor")
        SourceListEditor.resize(382, 462)
        self.gridLayout = QtWidgets.QGridLayout(SourceListEditor)
        self.gridLayout.setVerticalSpacing(20)
        self.gridLayout.setObjectName("gridLayout")
        self.btnAddSource = QtWidgets.QPushButton(SourceListEditor)
        self.btnAddSource.setObjectName("btnAddSource")
        self.gridLayout.addWidget(self.btnAddSource, 2, 0, 1, 2)
        self.btnAddFavorite = QtWidgets.QPushButton(SourceListEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/bookmark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddFavorite.setIcon(icon)
        self.btnAddFavorite.setObjectName("btnAddFavorite")
        self.gridLayout.addWidget(self.btnAddFavorite, 5, 0, 1, 2)
        self.lbl = QtWidgets.QLabel(SourceListEditor)
        self.lbl.setMinimumSize(QtCore.QSize(0, 100))
        self.lbl.setText("")
        self.lbl.setTextFormat(QtCore.Qt.RichText)
        self.lbl.setWordWrap(True)
        self.lbl.setObjectName("lbl")
        self.gridLayout.addWidget(self.lbl, 0, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 3, 0, 1, 1)
        self.lblLinkInfo = QtWidgets.QLabel(SourceListEditor)
        self.lblLinkInfo.setAutoFillBackground(False)
        self.lblLinkInfo.setStyleSheet("QLabel { font-style: italic; background-color: rgba(0,0,0,10%); }")
        self.lblLinkInfo.setText("")
        self.lblLinkInfo.setWordWrap(True)
        self.lblLinkInfo.setObjectName("lblLinkInfo")
        self.gridLayout.addWidget(self.lblLinkInfo, 1, 0, 1, 2)

        self.retranslateUi(SourceListEditor)
        QtCore.QMetaObject.connectSlotsByName(SourceListEditor)

    def retranslateUi(self, SourceListEditor):
        _translate = QtCore.QCoreApplication.translate
        SourceListEditor.setWindowTitle(_translate("SourceListEditor", "Form"))
        self.btnAddSource.setText(_translate("SourceListEditor", "Add Independent Source"))
        self.btnAddFavorite.setToolTip(_translate("SourceListEditor", "Add this source list to your favorites"))
        self.btnAddFavorite.setText(_translate("SourceListEditor", "add souce && alternatives to favorites"))

from . import bibolamazi_res_rc
