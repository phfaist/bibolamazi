# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filterpackagepatheditor.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FilterPackagePathEditor(object):
    def setupUi(self, FilterPackagePathEditor):
        FilterPackagePathEditor.setObjectName("FilterPackagePathEditor")
        FilterPackagePathEditor.resize(309, 390)
        self.verticalLayout = QtWidgets.QVBoxLayout(FilterPackagePathEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(FilterPackagePathEditor)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.lblInfo = QtWidgets.QLabel(FilterPackagePathEditor)
        self.lblInfo.setMinimumSize(QtCore.QSize(0, 50))
        self.lblInfo.setStyleSheet("background-color: rgba(0, 0, 120, 25);")
        self.lblInfo.setTextFormat(QtCore.Qt.RichText)
        self.lblInfo.setWordWrap(True)
        self.lblInfo.setObjectName("lblInfo")
        self.verticalLayout.addWidget(self.lblInfo)
        self.btnSetLocalPackage = QtWidgets.QPushButton(FilterPackagePathEditor)
        self.btnSetLocalPackage.setObjectName("btnSetLocalPackage")
        self.verticalLayout.addWidget(self.btnSetLocalPackage)
        self.btnSetGithubRepo = QtWidgets.QPushButton(FilterPackagePathEditor)
        self.btnSetGithubRepo.setObjectName("btnSetGithubRepo")
        self.verticalLayout.addWidget(self.btnSetGithubRepo)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(FilterPackagePathEditor)
        QtCore.QMetaObject.connectSlotsByName(FilterPackagePathEditor)

    def retranslateUi(self, FilterPackagePathEditor):
        _translate = QtCore.QCoreApplication.translate
        FilterPackagePathEditor.setWindowTitle(_translate("FilterPackagePathEditor", "Form"))
        self.label.setText(_translate("FilterPackagePathEditor", "Imported filter package"))
        self.lblInfo.setText(_translate("FilterPackagePathEditor", "path"))
        self.btnSetLocalPackage.setText(_translate("FilterPackagePathEditor", "set local python package ..."))
        self.btnSetGithubRepo.setText(_translate("FilterPackagePathEditor", "set github repository ..."))


