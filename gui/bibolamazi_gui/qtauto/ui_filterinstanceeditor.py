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
        FilterInstanceEditor.resize(368, 361)
        self.gridLayout = QtWidgets.QGridLayout(FilterInstanceEditor)
        self.gridLayout.setObjectName("gridLayout")
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
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)
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
        self.hlytButtons = QtWidgets.QHBoxLayout()
        self.hlytButtons.setObjectName("hlytButtons")
        self.btnFilterHelp = QtWidgets.QPushButton(FilterInstanceEditor)
        self.btnFilterHelp.setObjectName("btnFilterHelp")
        self.hlytButtons.addWidget(self.btnFilterHelp)
        self.btnAddFavorite = QtWidgets.QToolButton(FilterInstanceEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/bookmark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddFavorite.setIcon(icon)
        self.btnAddFavorite.setObjectName("btnAddFavorite")
        self.hlytButtons.addWidget(self.btnAddFavorite)
        self.gridLayout.addLayout(self.hlytButtons, 4, 0, 1, 2)

        self.retranslateUi(FilterInstanceEditor)
        QtCore.QMetaObject.connectSlotsByName(FilterInstanceEditor)

    def retranslateUi(self, FilterInstanceEditor):
        _translate = QtCore.QCoreApplication.translate
        FilterInstanceEditor.setWindowTitle(_translate("FilterInstanceEditor", "Form"))
        self.label.setText(_translate("FilterInstanceEditor", "Filter:"))
        self.btnFilterHelp.setText(_translate("FilterInstanceEditor", "Help: Filter Reference"))
        self.btnAddFavorite.setToolTip(_translate("FilterInstanceEditor", "Add this full command line to your favorites"))

from . import bibolamazi_res_rc
