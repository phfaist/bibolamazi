# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openbibfile.ui'
#
# Created: Sun May 10 16:04:08 2015
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

class Ui_OpenBibFile(object):
    def setupUi(self, OpenBibFile):
        OpenBibFile.setObjectName(_fromUtf8("OpenBibFile"))
        OpenBibFile.resize(787, 501)
        self.lyt = QtGui.QGridLayout(OpenBibFile)
        self.lyt.setObjectName(_fromUtf8("lyt"))
        self.btnGo = QtGui.QPushButton(OpenBibFile)
        self.btnGo.setMinimumSize(QtCore.QSize(0, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/ok.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnGo.setIcon(icon)
        self.btnGo.setObjectName(_fromUtf8("btnGo"))
        self.lyt.addWidget(self.btnGo, 1, 0, 1, 1)
        self.tabs = QtGui.QTabWidget(OpenBibFile)
        self.tabs.setTabPosition(QtGui.QTabWidget.South)
        self.tabs.setObjectName(_fromUtf8("tabs"))
        self.pageConfig = QtGui.QWidget()
        self.pageConfig.setObjectName(_fromUtf8("pageConfig"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.pageConfig)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 8)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.splitEditConfig = QtGui.QSplitter(self.pageConfig)
        self.splitEditConfig.setOrientation(QtCore.Qt.Horizontal)
        self.splitEditConfig.setObjectName(_fromUtf8("splitEditConfig"))
        self.txtConfig = QtGui.QTextEdit(self.splitEditConfig)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(9)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtConfig.sizePolicy().hasHeightForWidth())
        self.txtConfig.setSizePolicy(sizePolicy)
        self.txtConfig.setAcceptRichText(False)
        self.txtConfig.setObjectName(_fromUtf8("txtConfig"))
        self.stackEditTools = QtGui.QStackedWidget(self.splitEditConfig)
        self.stackEditTools.setFrameShape(QtGui.QFrame.StyledPanel)
        self.stackEditTools.setFrameShadow(QtGui.QFrame.Raised)
        self.stackEditTools.setObjectName(_fromUtf8("stackEditTools"))
        self.toolspageBase = QtGui.QWidget()
        self.toolspageBase.setObjectName(_fromUtf8("toolspageBase"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.toolspageBase)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.lblFavorites = QtGui.QLabel(self.toolspageBase)
        self.lblFavorites.setPixmap(QtGui.QPixmap(_fromUtf8(":/pic/bookmark.png")))
        self.lblFavorites.setAlignment(QtCore.Qt.AlignCenter)
        self.lblFavorites.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.lblFavorites.setObjectName(_fromUtf8("lblFavorites"))
        self.verticalLayout_3.addWidget(self.lblFavorites)
        self.treeFavorites = QtGui.QTreeView(self.toolspageBase)
        font = QtGui.QFont()
        font.setItalic(True)
        self.treeFavorites.setFont(font)
        self.treeFavorites.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.treeFavorites.setRootIsDecorated(False)
        self.treeFavorites.setObjectName(_fromUtf8("treeFavorites"))
        self.treeFavorites.header().setVisible(False)
        self.verticalLayout_3.addWidget(self.treeFavorites)
        self.line = QtGui.QFrame(self.toolspageBase)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.verticalLayout_3.addWidget(self.line)
        self.btnAddSourceList = QtGui.QPushButton(self.toolspageBase)
        self.btnAddSourceList.setObjectName(_fromUtf8("btnAddSourceList"))
        self.verticalLayout_3.addWidget(self.btnAddSourceList)
        self.btnAddFilter = QtGui.QPushButton(self.toolspageBase)
        self.btnAddFilter.setObjectName(_fromUtf8("btnAddFilter"))
        self.verticalLayout_3.addWidget(self.btnAddFilter)
        self.stackEditTools.addWidget(self.toolspageBase)
        self.toolspageSource = QtGui.QWidget()
        self.toolspageSource.setObjectName(_fromUtf8("toolspageSource"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.toolspageSource)
        self.verticalLayout_4.setMargin(0)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.sourceListEditor = SourceListEditor(self.toolspageSource)
        self.sourceListEditor.setObjectName(_fromUtf8("sourceListEditor"))
        self.verticalLayout_4.addWidget(self.sourceListEditor)
        self.stackEditTools.addWidget(self.toolspageSource)
        self.toolspageFilter = QtGui.QWidget()
        self.toolspageFilter.setObjectName(_fromUtf8("toolspageFilter"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.toolspageFilter)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.filterInstanceEditor = FilterInstanceEditor(self.toolspageFilter)
        self.filterInstanceEditor.setObjectName(_fromUtf8("filterInstanceEditor"))
        self.verticalLayout_5.addWidget(self.filterInstanceEditor)
        self.stackEditTools.addWidget(self.toolspageFilter)
        self.verticalLayout_2.addWidget(self.splitEditConfig)
        self.tabs.addTab(self.pageConfig, _fromUtf8(""))
        self.pageInfo = QtGui.QWidget()
        self.pageInfo.setObjectName(_fromUtf8("pageInfo"))
        self.verticalLayout = QtGui.QVBoxLayout(self.pageInfo)
        self.verticalLayout.setContentsMargins(0, 0, 0, 8)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.txtInfo = QtGui.QTextBrowser(self.pageInfo)
        self.txtInfo.setTabChangesFocus(True)
        self.txtInfo.setOpenLinks(False)
        self.txtInfo.setObjectName(_fromUtf8("txtInfo"))
        self.verticalLayout.addWidget(self.txtInfo)
        self.tabs.addTab(self.pageInfo, _fromUtf8(""))
        self.pageBibEntries = QtGui.QWidget()
        self.pageBibEntries.setObjectName(_fromUtf8("pageBibEntries"))
        self.gridLayout_2 = QtGui.QGridLayout(self.pageBibEntries)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 8)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.txtBibEntries = QtGui.QTextBrowser(self.pageBibEntries)
        font = QtGui.QFont()
        font.setFamily(_fromUtf8("Courier 10 Pitch"))
        self.txtBibEntries.setFont(font)
        self.txtBibEntries.setTabChangesFocus(True)
        self.txtBibEntries.setOpenLinks(False)
        self.txtBibEntries.setObjectName(_fromUtf8("txtBibEntries"))
        self.gridLayout_2.addWidget(self.txtBibEntries, 0, 0, 1, 1)
        self.tabs.addTab(self.pageBibEntries, _fromUtf8(""))
        self.pageLog = QtGui.QWidget()
        self.pageLog.setObjectName(_fromUtf8("pageLog"))
        self.gridLayout = QtGui.QGridLayout(self.pageLog)
        self.gridLayout.setContentsMargins(0, 0, 0, 8)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.txtLog = QtGui.QTextBrowser(self.pageLog)
        self.txtLog.setTabChangesFocus(True)
        self.txtLog.setHtml(_fromUtf8("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier 10 Pitch\';\"><br /></p></body></html>"))
        self.txtLog.setAcceptRichText(False)
        self.txtLog.setOpenLinks(False)
        self.txtLog.setObjectName(_fromUtf8("txtLog"))
        self.gridLayout.addWidget(self.txtLog, 0, 0, 1, 2)
        self.lblVerbosity = QtGui.QLabel(self.pageLog)
        self.lblVerbosity.setObjectName(_fromUtf8("lblVerbosity"))
        self.gridLayout.addWidget(self.lblVerbosity, 1, 0, 1, 1)
        self.cbxVerbosity = QtGui.QComboBox(self.pageLog)
        self.cbxVerbosity.setObjectName(_fromUtf8("cbxVerbosity"))
        self.cbxVerbosity.addItem(_fromUtf8(""))
        self.cbxVerbosity.addItem(_fromUtf8(""))
        self.cbxVerbosity.addItem(_fromUtf8(""))
        self.cbxVerbosity.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.cbxVerbosity, 1, 1, 1, 1)
        self.tabs.addTab(self.pageLog, _fromUtf8(""))
        self.lyt.addWidget(self.tabs, 2, 0, 1, 1)
        self.wHead = QtGui.QWidget(OpenBibFile)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wHead.sizePolicy().hasHeightForWidth())
        self.wHead.setSizePolicy(sizePolicy)
        self.wHead.setObjectName(_fromUtf8("wHead"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.wHead)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lblFileName = QtGui.QLabel(self.wHead)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFileName.sizePolicy().hasHeightForWidth())
        self.lblFileName.setSizePolicy(sizePolicy)
        self.lblFileName.setFrameShape(QtGui.QFrame.StyledPanel)
        self.lblFileName.setFrameShadow(QtGui.QFrame.Sunken)
        self.lblFileName.setMidLineWidth(1)
        self.lblFileName.setTextFormat(QtCore.Qt.PlainText)
        self.lblFileName.setAlignment(QtCore.Qt.AlignCenter)
        self.lblFileName.setObjectName(_fromUtf8("lblFileName"))
        self.horizontalLayout.addWidget(self.lblFileName)
        self.btnRefresh = QtGui.QToolButton(self.wHead)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/refresh.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRefresh.setIcon(icon1)
        self.btnRefresh.setIconSize(QtCore.QSize(22, 22))
        self.btnRefresh.setObjectName(_fromUtf8("btnRefresh"))
        self.horizontalLayout.addWidget(self.btnRefresh)
        self.btnSave = QtGui.QToolButton(self.wHead)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/pic/save.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSave.setIcon(icon2)
        self.btnSave.setIconSize(QtCore.QSize(22, 22))
        self.btnSave.setObjectName(_fromUtf8("btnSave"))
        self.horizontalLayout.addWidget(self.btnSave)
        self.lyt.addWidget(self.wHead, 0, 0, 1, 1)

        self.retranslateUi(OpenBibFile)
        self.tabs.setCurrentIndex(0)
        self.stackEditTools.setCurrentIndex(0)
        self.cbxVerbosity.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(OpenBibFile)

    def retranslateUi(self, OpenBibFile):
        self.btnGo.setText(_translate("OpenBibFile", "Run Bibolamazi !", None))
        self.btnAddSourceList.setText(_translate("OpenBibFile", "add source list ...", None))
        self.btnAddFilter.setText(_translate("OpenBibFile", "insert filter ...", None))
        self.tabs.setTabText(self.tabs.indexOf(self.pageConfig), _translate("OpenBibFile", "Edit Bibolamazi Confguration", None))
        self.txtInfo.setHtml(_translate("OpenBibFile", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Lucida Grande\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:20px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-style:italic; color:#b1311d;\">&lt;no file open&gt;</span></p></body></html>", None))
        self.tabs.setTabText(self.tabs.indexOf(self.pageInfo), _translate("OpenBibFile", "BIbolamazi File Info", None))
        self.tabs.setTabText(self.tabs.indexOf(self.pageBibEntries), _translate("OpenBibFile", "Preview Bib Entries", None))
        self.lblVerbosity.setText(_translate("OpenBibFile", "Log verbosity level (for next run):", None))
        self.cbxVerbosity.setItemText(0, _translate("OpenBibFile", "Quiet", None))
        self.cbxVerbosity.setItemText(1, _translate("OpenBibFile", "Information", None))
        self.cbxVerbosity.setItemText(2, _translate("OpenBibFile", "Verbose", None))
        self.cbxVerbosity.setItemText(3, _translate("OpenBibFile", "Very Verbose (for debugging)", None))
        self.tabs.setTabText(self.tabs.indexOf(self.pageLog), _translate("OpenBibFile", "Messages", None))
        self.lblFileName.setText(_translate("OpenBibFile", "some text here", None))

from ..filterinstanceeditor import FilterInstanceEditor
from ..sourcelisteditor import SourceListEditor
from . import bibolamazi_res_rc
