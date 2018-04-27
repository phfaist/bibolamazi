# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filterinstanceeditor.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FilterInstanceEditor(object):
    def setupUi(self, FilterInstanceEditor):
        FilterInstanceEditor.setObjectName("FilterInstanceEditor")
        FilterInstanceEditor.resize(403, 474)
        self.gridLayout = QtWidgets.QGridLayout(FilterInstanceEditor)
        self.gridLayout.setObjectName("gridLayout")
        self.lstOptions = QtWidgets.QTreeView(FilterInstanceEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstOptions.sizePolicy().hasHeightForWidth())
        self.lstOptions.setSizePolicy(sizePolicy)
        self.lstOptions.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.lstOptions.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.lstOptions.setIndentation(0)
        self.lstOptions.setItemsExpandable(False)
        self.lstOptions.setAllColumnsShowFocus(True)
        self.lstOptions.setObjectName("lstOptions")
        self.gridLayout.addWidget(self.lstOptions, 3, 0, 1, 2)
        self.lblOptionHelp = QtWidgets.QLabel(FilterInstanceEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblOptionHelp.sizePolicy().hasHeightForWidth())
        self.lblOptionHelp.setSizePolicy(sizePolicy)
        self.lblOptionHelp.setMinimumSize(QtCore.QSize(0, 25))
        self.lblOptionHelp.setText("")
        self.lblOptionHelp.setTextFormat(QtCore.Qt.PlainText)
        self.lblOptionHelp.setWordWrap(True)
        self.lblOptionHelp.setObjectName("lblOptionHelp")
        self.gridLayout.addWidget(self.lblOptionHelp, 4, 0, 1, 2)
        self.lblErrorMsg = QtWidgets.QLabel(FilterInstanceEditor)
        self.lblErrorMsg.setStyleSheet("color: rgb(198, 0, 0)")
        self.lblErrorMsg.setTextFormat(QtCore.Qt.PlainText)
        self.lblErrorMsg.setWordWrap(True)
        self.lblErrorMsg.setObjectName("lblErrorMsg")
        self.gridLayout.addWidget(self.lblErrorMsg, 1, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(FilterInstanceEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cbxFilter = QtWidgets.QComboBox(FilterInstanceEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(2)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.cbxFilter.sizePolicy().hasHeightForWidth())
        self.cbxFilter.setSizePolicy(sizePolicy)
        self.cbxFilter.setEditable(True)
        self.cbxFilter.setInsertPolicy(QtWidgets.QComboBox.NoInsert)
        self.cbxFilter.setObjectName("cbxFilter")
        self.horizontalLayout.addWidget(self.cbxFilter)
        self.btnFilterHelp = QtWidgets.QToolButton(FilterInstanceEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/question.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnFilterHelp.setIcon(icon)
        self.btnFilterHelp.setObjectName("btnFilterHelp")
        self.horizontalLayout.addWidget(self.btnFilterHelp)
        self.btnAddFavorite = QtWidgets.QToolButton(FilterInstanceEditor)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/pic/bookmark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddFavorite.setIcon(icon1)
        self.btnAddFavorite.setObjectName("btnAddFavorite")
        self.horizontalLayout.addWidget(self.btnAddFavorite)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 2)

        self.retranslateUi(FilterInstanceEditor)
        QtCore.QMetaObject.connectSlotsByName(FilterInstanceEditor)

    def retranslateUi(self, FilterInstanceEditor):
        _translate = QtCore.QCoreApplication.translate
        FilterInstanceEditor.setWindowTitle(_translate("FilterInstanceEditor", "Form"))
        self.lblErrorMsg.setText(_translate("FilterInstanceEditor", "Error: this and that"))
        self.label.setText(_translate("FilterInstanceEditor", "Filter:"))
        self.btnFilterHelp.setText(_translate("FilterInstanceEditor", "?"))
        self.btnAddFavorite.setToolTip(_translate("FilterInstanceEditor", "Add this full command line to your favorites"))

from . import bibolamazi_res_rc
