# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settingswidget.ui'
#
# Created: Fri Jun 27 15:11:40 2014
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
        SettingsWidget.resize(388, 189)
        self.verticalLayout_2 = QtGui.QVBoxLayout(SettingsWidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
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
        spacerItem = QtGui.QSpacerItem(20, 16, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
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
        self.frmUpdates.setTitle(_translate("SettingsWidget", "Software Updates", None))
        self.chkUpdates.setText(_translate("SettingsWidget", "Check for software updates", None))
        self.chkDevelUpdates.setText(_translate("SettingsWidget", "Include development (beta) versions", None))
        self.btnCheckNow.setText(_translate("SettingsWidget", "Check Now", None))

