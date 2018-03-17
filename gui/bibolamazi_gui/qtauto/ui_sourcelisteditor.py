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
        SourceListEditor.resize(368, 457)
        self.gridLayout = QtWidgets.QGridLayout(SourceListEditor)
        self.gridLayout.setObjectName("gridLayout")
        self.lstSources = QtWidgets.QListWidget(SourceListEditor)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstSources.sizePolicy().hasHeightForWidth())
        self.lstSources.setSizePolicy(sizePolicy)
        self.lstSources.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.lstSources.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.lstSources.setObjectName("lstSources")
        self.gridLayout.addWidget(self.lstSources, 2, 0, 1, 2)
        self.gbxEditSource = QtWidgets.QGroupBox(SourceListEditor)
        self.gbxEditSource.setObjectName("gbxEditSource")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.gbxEditSource)
        self.gridLayout_2.setVerticalSpacing(12)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.lblFile = QtWidgets.QLabel(self.gbxEditSource)
        self.lblFile.setObjectName("lblFile")
        self.gridLayout_2.addWidget(self.lblFile, 0, 0, 1, 1)
        self.txtFile = QtWidgets.QLineEdit(self.gbxEditSource)
        self.txtFile.setObjectName("txtFile")
        self.gridLayout_2.addWidget(self.txtFile, 1, 0, 1, 2)
        self.btnBrowse = QtWidgets.QPushButton(self.gbxEditSource)
        self.btnBrowse.setObjectName("btnBrowse")
        self.gridLayout_2.addWidget(self.btnBrowse, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.gbxEditSource, 9, 0, 1, 2)
        spacerItem = QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(SourceListEditor)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 7, 0, 1, 2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(SourceListEditor)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.btnAddFavorite = QtWidgets.QToolButton(SourceListEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/bookmark.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddFavorite.setIcon(icon)
        self.btnAddFavorite.setObjectName("btnAddFavorite")
        self.horizontalLayout.addWidget(self.btnAddFavorite)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.btnAddSourceAltLoc = QtWidgets.QPushButton(SourceListEditor)
        self.btnAddSourceAltLoc.setObjectName("btnAddSourceAltLoc")
        self.gridLayout.addWidget(self.btnAddSourceAltLoc, 4, 0, 1, 1)
        self.btnRemoveSourceAltLoc = QtWidgets.QPushButton(SourceListEditor)
        self.btnRemoveSourceAltLoc.setObjectName("btnRemoveSourceAltLoc")
        self.gridLayout.addWidget(self.btnRemoveSourceAltLoc, 4, 1, 1, 1)
        self.btnAddSource = QtWidgets.QPushButton(SourceListEditor)
        self.btnAddSource.setObjectName("btnAddSource")
        self.gridLayout.addWidget(self.btnAddSource, 3, 0, 1, 2)

        self.retranslateUi(SourceListEditor)
        QtCore.QMetaObject.connectSlotsByName(SourceListEditor)

    def retranslateUi(self, SourceListEditor):
        _translate = QtCore.QCoreApplication.translate
        SourceListEditor.setWindowTitle(_translate("SourceListEditor", "Form"))
        self.lstSources.setToolTip(_translate("SourceListEditor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of sources to collect bibliographic entries. Reorder entries by <span style=\" font-weight:600;\">Drag&amp;Drop</span>. Remember that the <em>first</em> existing file of <em>each</em> source list will be read.</p></body></html>"))
        self.gbxEditSource.setTitle(_translate("SourceListEditor", "Edit this source"))
        self.lblFile.setText(_translate("SourceListEditor", "File or URL:"))
        self.btnBrowse.setText(_translate("SourceListEditor", "browse file ..."))
        self.label_2.setText(_translate("SourceListEditor", "(reorder alt. source locations by drag and drop)"))
        self.label.setText(_translate("SourceListEditor", "Source List: (first accessible will be used)"))
        self.btnAddFavorite.setToolTip(_translate("SourceListEditor", "Add this source list to your favorites"))
        self.btnAddSourceAltLoc.setText(_translate("SourceListEditor", "Add Alternative Location"))
        self.btnRemoveSourceAltLoc.setText(_translate("SourceListEditor", "Remove Alt. Loc."))
        self.btnAddSource.setText(_translate("SourceListEditor", "Add Source"))

from . import bibolamazi_res_rc
