# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sourcelisteditor.ui'
#
# Created: Wed Dec 16 13:50:55 2015
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

class Ui_SourceListEditor(object):
    def setupUi(self, SourceListEditor):
        SourceListEditor.setObjectName(_fromUtf8("SourceListEditor"))
        SourceListEditor.resize(368, 457)
        self.gridLayout = QtGui.QGridLayout(SourceListEditor)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lstSources = QtGui.QListWidget(SourceListEditor)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lstSources.sizePolicy().hasHeightForWidth())
        self.lstSources.setSizePolicy(sizePolicy)
        self.lstSources.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.lstSources.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.lstSources.setObjectName(_fromUtf8("lstSources"))
        self.gridLayout.addWidget(self.lstSources, 2, 0, 1, 2)
        self.gbxEditSource = QtGui.QGroupBox(SourceListEditor)
        self.gbxEditSource.setObjectName(_fromUtf8("gbxEditSource"))
        self.gridLayout_2 = QtGui.QGridLayout(self.gbxEditSource)
        self.gridLayout_2.setVerticalSpacing(12)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.lblFile = QtGui.QLabel(self.gbxEditSource)
        self.lblFile.setObjectName(_fromUtf8("lblFile"))
        self.gridLayout_2.addWidget(self.lblFile, 0, 0, 1, 1)
        self.txtFile = QtGui.QLineEdit(self.gbxEditSource)
        self.txtFile.setObjectName(_fromUtf8("txtFile"))
        self.gridLayout_2.addWidget(self.txtFile, 1, 0, 1, 2)
        self.btnBrowse = QtGui.QPushButton(self.gbxEditSource)
        self.btnBrowse.setObjectName(_fromUtf8("btnBrowse"))
        self.gridLayout_2.addWidget(self.btnBrowse, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.gbxEditSource, 9, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(10, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.gridLayout.addItem(spacerItem, 8, 0, 1, 1)
        self.label_2 = QtGui.QLabel(SourceListEditor)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 7, 0, 1, 2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.label = QtGui.QLabel(SourceListEditor)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.btnAddFavorite = QtGui.QToolButton(SourceListEditor)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/bookmark.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnAddFavorite.setIcon(icon)
        self.btnAddFavorite.setObjectName(_fromUtf8("btnAddFavorite"))
        self.horizontalLayout.addWidget(self.btnAddFavorite)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 2)
        self.btnAddSourceAltLoc = QtGui.QPushButton(SourceListEditor)
        self.btnAddSourceAltLoc.setObjectName(_fromUtf8("btnAddSourceAltLoc"))
        self.gridLayout.addWidget(self.btnAddSourceAltLoc, 4, 0, 1, 1)
        self.btnRemoveSourceAltLoc = QtGui.QPushButton(SourceListEditor)
        self.btnRemoveSourceAltLoc.setObjectName(_fromUtf8("btnRemoveSourceAltLoc"))
        self.gridLayout.addWidget(self.btnRemoveSourceAltLoc, 4, 1, 1, 1)
        self.btnAddSource = QtGui.QPushButton(SourceListEditor)
        self.btnAddSource.setObjectName(_fromUtf8("btnAddSource"))
        self.gridLayout.addWidget(self.btnAddSource, 3, 0, 1, 2)

        self.retranslateUi(SourceListEditor)
        QtCore.QMetaObject.connectSlotsByName(SourceListEditor)

    def retranslateUi(self, SourceListEditor):
        SourceListEditor.setWindowTitle(_translate("SourceListEditor", "Form", None))
        self.lstSources.setToolTip(_translate("SourceListEditor", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">List of sources to collect bibliographic entries. Reorder entries by <span style=\" font-weight:600;\">Drag&amp;Drop</span>. Remember that the <em>first</em> existing file of <em>each</em> source list will be read.</p></body></html>", None))
        self.gbxEditSource.setTitle(_translate("SourceListEditor", "Edit this source", None))
        self.lblFile.setText(_translate("SourceListEditor", "File or URL:", None))
        self.btnBrowse.setText(_translate("SourceListEditor", "browse file ...", None))
        self.label_2.setText(_translate("SourceListEditor", "(reorder alt. source locations by drag and drop)", None))
        self.label.setText(_translate("SourceListEditor", "Source List: (first accessible will be used)", None))
        self.btnAddFavorite.setToolTip(_translate("SourceListEditor", "Add this source list to your favorites", None))
        self.btnAddSourceAltLoc.setText(_translate("SourceListEditor", "Add Alternative Location", None))
        self.btnRemoveSourceAltLoc.setText(_translate("SourceListEditor", "Remove Alt. Loc.", None))
        self.btnAddSource.setText(_translate("SourceListEditor", "Add Source", None))

from . import bibolamazi_res_rc
