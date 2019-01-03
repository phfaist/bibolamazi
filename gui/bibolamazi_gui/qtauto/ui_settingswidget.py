# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingswidget.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SettingsWidget(object):
    def setupUi(self, SettingsWidget):
        SettingsWidget.setObjectName("SettingsWidget")
        SettingsWidget.resize(483, 331)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(SettingsWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.wGeneral = QtWidgets.QGroupBox(SettingsWidget)
        self.wGeneral.setObjectName("wGeneral")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.wGeneral)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.spnMaxRecentFiles = QtWidgets.QSpinBox(self.wGeneral)
        self.spnMaxRecentFiles.setMaximum(31)
        self.spnMaxRecentFiles.setObjectName("spnMaxRecentFiles")
        self.gridLayout_2.addWidget(self.spnMaxRecentFiles, 0, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.wGeneral)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.verticalLayout_2.addWidget(self.wGeneral)
        spacerItem = QtWidgets.QSpacerItem(20, 2, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)
        self.tabs = QtWidgets.QGroupBox(SettingsWidget)
        self.tabs.setObjectName("tabs")
        self.gridLayout = QtWidgets.QGridLayout(self.tabs)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.btnFilterPackageAdd = QtWidgets.QPushButton(self.tabs)
        self.btnFilterPackageAdd.setObjectName("btnFilterPackageAdd")
        self.horizontalLayout.addWidget(self.btnFilterPackageAdd)
        self.btnFilterPackageRemove = QtWidgets.QPushButton(self.tabs)
        self.btnFilterPackageRemove.setObjectName("btnFilterPackageRemove")
        self.horizontalLayout.addWidget(self.btnFilterPackageRemove)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.lstFilterPackages = QtWidgets.QTreeView(self.tabs)
        self.lstFilterPackages.setIndentation(0)
        self.lstFilterPackages.setObjectName("lstFilterPackages")
        self.gridLayout.addWidget(self.lstFilterPackages, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.btnFilterPackageMoveUp = QtWidgets.QToolButton(self.tabs)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFilterPackageMoveUp.sizePolicy().hasHeightForWidth())
        self.btnFilterPackageMoveUp.setSizePolicy(sizePolicy)
        self.btnFilterPackageMoveUp.setObjectName("btnFilterPackageMoveUp")
        self.verticalLayout_3.addWidget(self.btnFilterPackageMoveUp)
        self.btnFilterPackageMoveDown = QtWidgets.QToolButton(self.tabs)
        self.btnFilterPackageMoveDown.setObjectName("btnFilterPackageMoveDown")
        self.verticalLayout_3.addWidget(self.btnFilterPackageMoveDown)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.tabs)
        self.btns = QtWidgets.QDialogButtonBox(SettingsWidget)
        self.btns.setOrientation(QtCore.Qt.Horizontal)
        self.btns.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.btns.setObjectName("btns")
        self.verticalLayout_2.addWidget(self.btns)

        self.retranslateUi(SettingsWidget)
        self.btns.accepted.connect(SettingsWidget.accept)
        self.btns.rejected.connect(SettingsWidget.reject)
        QtCore.QMetaObject.connectSlotsByName(SettingsWidget)

    def retranslateUi(self, SettingsWidget):
        _translate = QtCore.QCoreApplication.translate
        SettingsWidget.setWindowTitle(_translate("SettingsWidget", "Settings"))
        self.wGeneral.setTitle(_translate("SettingsWidget", "General"))
        self.label.setText(_translate("SettingsWidget", "Remember recent files:"))
        self.tabs.setTitle(_translate("SettingsWidget", "Filter packages"))
        self.btnFilterPackageAdd.setText(_translate("SettingsWidget", "Add filter package ..."))
        self.btnFilterPackageRemove.setText(_translate("SettingsWidget", "Forget package"))
        self.btnFilterPackageMoveUp.setText(_translate("SettingsWidget", "▲"))
        self.btnFilterPackageMoveDown.setText(_translate("SettingsWidget", "▼"))

