# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'githubreposelector.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GithubRepoSelector(object):
    def setupUi(self, GithubRepoSelector):
        GithubRepoSelector.setObjectName("GithubRepoSelector")
        GithubRepoSelector.resize(430, 138)
        self.gridLayout = QtWidgets.QGridLayout(GithubRepoSelector)
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 2, 0, 1, 1)
        self.stk = QtWidgets.QStackedWidget(GithubRepoSelector)
        self.stk.setObjectName("stk")
        self.pageUsername = QtWidgets.QWidget()
        self.pageUsername.setObjectName("pageUsername")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.pageUsername)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.txtUser = QtWidgets.QLineEdit(self.pageUsername)
        self.txtUser.setObjectName("txtUser")
        self.gridLayout_2.addWidget(self.txtUser, 1, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.pageUsername)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.stk.addWidget(self.pageUsername)
        self.pageRepo = QtWidgets.QWidget()
        self.pageRepo.setObjectName("pageRepo")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.pageRepo)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.lblPromptRepo = QtWidgets.QLabel(self.pageRepo)
        self.lblPromptRepo.setObjectName("lblPromptRepo")
        self.gridLayout_3.addWidget(self.lblPromptRepo, 0, 0, 1, 1)
        self.cbxRepos = QtWidgets.QComboBox(self.pageRepo)
        self.cbxRepos.setEditable(True)
        self.cbxRepos.setObjectName("cbxRepos")
        self.gridLayout_3.addWidget(self.cbxRepos, 1, 0, 1, 1)
        self.stk.addWidget(self.pageRepo)
        self.gridLayout.addWidget(self.stk, 1, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnCancel = QtWidgets.QPushButton(GithubRepoSelector)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout.addWidget(self.btnCancel)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.btnBack = QtWidgets.QPushButton(GithubRepoSelector)
        self.btnBack.setObjectName("btnBack")
        self.horizontalLayout.addWidget(self.btnBack)
        self.btnNext = QtWidgets.QPushButton(GithubRepoSelector)
        self.btnNext.setObjectName("btnNext")
        self.horizontalLayout.addWidget(self.btnNext)
        self.btnOk = QtWidgets.QPushButton(GithubRepoSelector)
        self.btnOk.setObjectName("btnOk")
        self.horizontalLayout.addWidget(self.btnOk)
        self.gridLayout.addLayout(self.horizontalLayout, 3, 0, 1, 1)

        self.retranslateUi(GithubRepoSelector)
        self.stk.setCurrentIndex(1)
        self.btnCancel.clicked.connect(GithubRepoSelector.reject)
        QtCore.QMetaObject.connectSlotsByName(GithubRepoSelector)

    def retranslateUi(self, GithubRepoSelector):
        _translate = QtCore.QCoreApplication.translate
        GithubRepoSelector.setWindowTitle(_translate("GithubRepoSelector", "Dialog"))
        self.label.setText(_translate("GithubRepoSelector", "Github user name / organization:"))
        self.lblPromptRepo.setText(_translate("GithubRepoSelector", "Repositories for user %s"))
        self.btnCancel.setText(_translate("GithubRepoSelector", "cancel"))
        self.btnBack.setText(_translate("GithubRepoSelector", "◀ back"))
        self.btnNext.setText(_translate("GithubRepoSelector", "next ▶"))
        self.btnOk.setText(_translate("GithubRepoSelector", "OK"))


