# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingswidget.ui'
#
# Created: Tue Jul 15 16:13:49 2014
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

class Ui_SettingsWidget(object):
    def setupUi(self, SettingsWidget):
        SettingsWidget.setObjectName(_fromUtf8("SettingsWidget"))
        SettingsWidget.resize(498, 394)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SettingsWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.gbxFilterPackages = QtGui.QGroupBox(SettingsWidget)
        self.gbxFilterPackages.setObjectName(_fromUtf8("gbxFilterPackages"))
        self.gridLayout = QtGui.QGridLayout(self.gbxFilterPackages)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.btnFilterPackageAdd = QtGui.QPushButton(self.gbxFilterPackages)
        self.btnFilterPackageAdd.setObjectName(_fromUtf8("btnFilterPackageAdd"))
        self.horizontalLayout.addWidget(self.btnFilterPackageAdd)
        self.btnFilterPackageRemove = QtGui.QPushButton(self.gbxFilterPackages)
        self.btnFilterPackageRemove.setObjectName(_fromUtf8("btnFilterPackageRemove"))
        self.horizontalLayout.addWidget(self.btnFilterPackageRemove)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.lstFilterPackages = QtGui.QTreeView(self.gbxFilterPackages)
        self.lstFilterPackages.setIndentation(0)
        self.lstFilterPackages.setObjectName(_fromUtf8("lstFilterPackages"))
        self.gridLayout.addWidget(self.lstFilterPackages, 0, 0, 1, 1)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.btnFilterPackageMoveUp = QtGui.QToolButton(self.gbxFilterPackages)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnFilterPackageMoveUp.sizePolicy().hasHeightForWidth())
        self.btnFilterPackageMoveUp.setSizePolicy(sizePolicy)
        self.btnFilterPackageMoveUp.setObjectName(_fromUtf8("btnFilterPackageMoveUp"))
        self.verticalLayout_3.addWidget(self.btnFilterPackageMoveUp)
        self.btnFilterPackageMoveDown = QtGui.QToolButton(self.gbxFilterPackages)
        self.btnFilterPackageMoveDown.setObjectName(_fromUtf8("btnFilterPackageMoveDown"))
        self.verticalLayout_3.addWidget(self.btnFilterPackageMoveDown)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 1, 1, 1)
        self.verticalLayout_2.addWidget(self.gbxFilterPackages)
        self.frmUpdates = QtGui.QGroupBox(SettingsWidget)
        self.frmUpdates.setObjectName(_fromUtf8("frmUpdates"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frmUpdates)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.chkUpdates = QtGui.QCheckBox(self.frmUpdates)
        self.chkUpdates.setObjectName(_fromUtf8("chkUpdates"))
        self.verticalLayout.addWidget(self.chkUpdates)
        self.chkDevelUpdates = QtGui.QCheckBox(self.frmUpdates)
        self.chkDevelUpdates.setObjectName(_fromUtf8("chkDevelUpdates"))
        self.verticalLayout.addWidget(self.chkDevelUpdates)
        self.btnCheckNow = QtGui.QPushButton(self.frmUpdates)
        self.btnCheckNow.setObjectName(_fromUtf8("btnCheckNow"))
        self.verticalLayout.addWidget(self.btnCheckNow)
        self.verticalLayout_2.addWidget(self.frmUpdates)
        spacerItem1 = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.btns = QtGui.QDialogButtonBox(SettingsWidget)
        self.btns.setOrientation(QtCore.Qt.Horizontal)
        self.btns.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.btns.setObjectName(_fromUtf8("btns"))
        self.verticalLayout_2.addWidget(self.btns)

        self.retranslateUi(SettingsWidget)
        QtCore.QObject.connect(self.btns, QtCore.SIGNAL(_fromUtf8("accepted()")), SettingsWidget.accept)
        QtCore.QObject.connect(self.btns, QtCore.SIGNAL(_fromUtf8("rejected()")), SettingsWidget.reject)
        QtCore.QObject.connect(self.chkUpdates, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.chkDevelUpdates.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(SettingsWidget)

    def retranslateUi(self, SettingsWidget):
        SettingsWidget.setWindowTitle(_translate("SettingsWidget", "Settings", None))
        self.gbxFilterPackages.setTitle(_translate("SettingsWidget", "Filter Packages", None))
        self.btnFilterPackageAdd.setText(_translate("SettingsWidget", "Add filter package ...", None))
        self.btnFilterPackageRemove.setText(_translate("SettingsWidget", "Forget package", None))
        self.btnFilterPackageMoveUp.setText(_translate("SettingsWidget", "Up", None))
        self.btnFilterPackageMoveDown.setText(_translate("SettingsWidget", "Down", None))
        self.frmUpdates.setTitle(_translate("SettingsWidget", "Software Updates", None))
        self.chkUpdates.setText(_translate("SettingsWidget", "Check for software updates", None))
        self.chkDevelUpdates.setText(_translate("SettingsWidget", "Include development (beta) versions", None))
        self.btnCheckNow.setText(_translate("SettingsWidget", "Check Now", None))

