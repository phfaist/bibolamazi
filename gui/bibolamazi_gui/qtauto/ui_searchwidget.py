# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'searchwidget.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SearchWidget(object):
    def setupUi(self, SearchWidget):
        SearchWidget.setObjectName("SearchWidget")
        SearchWidget.resize(438, 28)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SearchWidget.sizePolicy().hasHeightForWidth())
        SearchWidget.setSizePolicy(sizePolicy)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SearchWidget)
        self.horizontalLayout.setContentsMargins(3, 3, 3, 3)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lbl = QtWidgets.QLabel(SearchWidget)
        self.lbl.setObjectName("lbl")
        self.horizontalLayout.addWidget(self.lbl)
        self.txt = QtWidgets.QLineEdit(SearchWidget)
        self.txt.setObjectName("txt")
        self.horizontalLayout.addWidget(self.txt)
        self.btnNext = QtWidgets.QToolButton(SearchWidget)
        self.btnNext.setObjectName("btnNext")
        self.horizontalLayout.addWidget(self.btnNext)
        self.btnPrev = QtWidgets.QToolButton(SearchWidget)
        self.btnPrev.setObjectName("btnPrev")
        self.horizontalLayout.addWidget(self.btnPrev)
        self.btnDone = QtWidgets.QToolButton(SearchWidget)
        self.btnDone.setObjectName("btnDone")
        self.horizontalLayout.addWidget(self.btnDone)

        self.retranslateUi(SearchWidget)
        QtCore.QMetaObject.connectSlotsByName(SearchWidget)

    def retranslateUi(self, SearchWidget):
        _translate = QtCore.QCoreApplication.translate
        SearchWidget.setWindowTitle(_translate("SearchWidget", "Form"))
        self.lbl.setText(_translate("SearchWidget", "find: "))
        self.btnNext.setText(_translate("SearchWidget", "▼"))
        self.btnPrev.setText(_translate("SearchWidget", "▲"))
        self.btnDone.setText(_translate("SearchWidget", "done"))

