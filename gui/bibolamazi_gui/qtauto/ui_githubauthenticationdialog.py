# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'githubauthenticationdialog.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_GithubAuthenticationDialog(object):
    def setupUi(self, GithubAuthenticationDialog):
        GithubAuthenticationDialog.setObjectName("GithubAuthenticationDialog")
        GithubAuthenticationDialog.resize(511, 535)
        self.verticalLayout = QtWidgets.QVBoxLayout(GithubAuthenticationDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtWidgets.QSpacerItem(20, 189, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.lbl = QtWidgets.QLabel(GithubAuthenticationDialog)
        self.lbl.setTextFormat(QtCore.Qt.RichText)
        self.lbl.setWordWrap(True)
        self.lbl.setOpenExternalLinks(True)
        self.lbl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextSelectableByMouse)
        self.lbl.setObjectName("lbl")
        self.verticalLayout.addWidget(self.lbl)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.txtToken = QtWidgets.QLineEdit(GithubAuthenticationDialog)
        self.txtToken.setObjectName("txtToken")
        self.verticalLayout.addWidget(self.txtToken)
        spacerItem2 = QtWidgets.QSpacerItem(20, 188, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.btns = QtWidgets.QDialogButtonBox(GithubAuthenticationDialog)
        self.btns.setOrientation(QtCore.Qt.Horizontal)
        self.btns.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.btns.setObjectName("btns")
        self.verticalLayout.addWidget(self.btns)

        self.retranslateUi(GithubAuthenticationDialog)
        self.btns.rejected.connect(GithubAuthenticationDialog.reject)
        self.btns.accepted.connect(GithubAuthenticationDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(GithubAuthenticationDialog)

    def retranslateUi(self, GithubAuthenticationDialog):
        _translate = QtCore.QCoreApplication.translate
        GithubAuthenticationDialog.setWindowTitle(_translate("GithubAuthenticationDialog", "Github Authentication"))
        self.lbl.setText(_translate("GithubAuthenticationDialog", "Instructions to authenticate: ....."))


