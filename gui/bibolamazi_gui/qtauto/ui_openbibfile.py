# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'openbibfile.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_OpenBibFile(object):
    def setupUi(self, OpenBibFile):
        OpenBibFile.setObjectName("OpenBibFile")
        OpenBibFile.resize(787, 501)
        self.lyt = QtWidgets.QGridLayout(OpenBibFile)
        self.lyt.setObjectName("lyt")
        self.btnGo = QtWidgets.QPushButton(OpenBibFile)
        self.btnGo.setMinimumSize(QtCore.QSize(0, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/pic/ok.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnGo.setIcon(icon)
        self.btnGo.setObjectName("btnGo")
        self.lyt.addWidget(self.btnGo, 1, 0, 1, 1)
        self.tabs = QtWidgets.QTabWidget(OpenBibFile)
        self.tabs.setTabPosition(QtWidgets.QTabWidget.South)
        self.tabs.setObjectName("tabs")
        self.pageConfig = QtWidgets.QWidget()
        self.pageConfig.setObjectName("pageConfig")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.pageConfig)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 8)
        self.verticalLayout_2.setSpacing(3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitEditConfig = QtWidgets.QSplitter(self.pageConfig)
        self.splitEditConfig.setOrientation(QtCore.Qt.Horizontal)
        self.splitEditConfig.setObjectName("splitEditConfig")
        self.txtConfig = QtWidgets.QTextEdit(self.splitEditConfig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.txtConfig.sizePolicy().hasHeightForWidth())
        self.txtConfig.setSizePolicy(sizePolicy)
        self.txtConfig.setAcceptRichText(False)
        self.txtConfig.setObjectName("txtConfig")
        self.stackEditTools = QtWidgets.QStackedWidget(self.splitEditConfig)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stackEditTools.sizePolicy().hasHeightForWidth())
        self.stackEditTools.setSizePolicy(sizePolicy)
        self.stackEditTools.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.stackEditTools.setFrameShadow(QtWidgets.QFrame.Raised)
        self.stackEditTools.setObjectName("stackEditTools")
        self.toolspageBase = QtWidgets.QWidget()
        self.toolspageBase.setObjectName("toolspageBase")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.toolspageBase)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.lblFavorites = QtWidgets.QLabel(self.toolspageBase)
        self.lblFavorites.setPixmap(QtGui.QPixmap(":/pic/bookmark.png"))
        self.lblFavorites.setAlignment(QtCore.Qt.AlignCenter)
        self.lblFavorites.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
        self.lblFavorites.setObjectName("lblFavorites")
        self.verticalLayout_3.addWidget(self.lblFavorites)
        self.treeFavorites = QtWidgets.QTreeView(self.toolspageBase)
        font = QtGui.QFont()
        font.setItalic(True)
        self.treeFavorites.setFont(font)
        self.treeFavorites.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.treeFavorites.setRootIsDecorated(False)
        self.treeFavorites.setObjectName("treeFavorites")
        self.treeFavorites.header().setVisible(False)
        self.verticalLayout_3.addWidget(self.treeFavorites)
        self.line = QtWidgets.QFrame(self.toolspageBase)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_3.addWidget(self.line)
        self.btnAddSourceList = QtWidgets.QPushButton(self.toolspageBase)
        self.btnAddSourceList.setObjectName("btnAddSourceList")
        self.verticalLayout_3.addWidget(self.btnAddSourceList)
        self.btnAddFilter = QtWidgets.QPushButton(self.toolspageBase)
        self.btnAddFilter.setObjectName("btnAddFilter")
        self.verticalLayout_3.addWidget(self.btnAddFilter)
        self.stackEditTools.addWidget(self.toolspageBase)
        self.toolspageSource = QtWidgets.QWidget()
        self.toolspageSource.setObjectName("toolspageSource")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.toolspageSource)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.sourceListEditor = SourceListEditor(self.toolspageSource)
        self.sourceListEditor.setObjectName("sourceListEditor")
        self.verticalLayout_4.addWidget(self.sourceListEditor)
        self.stackEditTools.addWidget(self.toolspageSource)
        self.toolspageFilter = QtWidgets.QWidget()
        self.toolspageFilter.setObjectName("toolspageFilter")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.toolspageFilter)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.filterInstanceEditor = FilterInstanceEditor(self.toolspageFilter)
        self.filterInstanceEditor.setObjectName("filterInstanceEditor")
        self.verticalLayout_5.addWidget(self.filterInstanceEditor)
        self.stackEditTools.addWidget(self.toolspageFilter)
        self.toolspagePackage = QtWidgets.QWidget()
        self.toolspagePackage.setObjectName("toolspagePackage")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.toolspagePackage)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.filterPackagePathEditor = FilterPackagePathEditor(self.toolspagePackage)
        self.filterPackagePathEditor.setObjectName("filterPackagePathEditor")
        self.verticalLayout_6.addWidget(self.filterPackagePathEditor)
        self.stackEditTools.addWidget(self.toolspagePackage)
        self.verticalLayout_2.addWidget(self.splitEditConfig)
        self.tabs.addTab(self.pageConfig, "")
        self.pageInfo = QtWidgets.QWidget()
        self.pageInfo.setObjectName("pageInfo")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.pageInfo)
        self.verticalLayout.setContentsMargins(0, 0, 0, 8)
        self.verticalLayout.setObjectName("verticalLayout")
        self.txtInfo = QtWidgets.QTextBrowser(self.pageInfo)
        self.txtInfo.setTabChangesFocus(True)
        self.txtInfo.setOpenLinks(False)
        self.txtInfo.setObjectName("txtInfo")
        self.verticalLayout.addWidget(self.txtInfo)
        self.tabs.addTab(self.pageInfo, "")
        self.pageBibEntries = QtWidgets.QWidget()
        self.pageBibEntries.setObjectName("pageBibEntries")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.pageBibEntries)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 8)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.txtBibEntries = QtWidgets.QTextBrowser(self.pageBibEntries)
        font = QtGui.QFont()
        font.setFamily("Courier 10 Pitch")
        self.txtBibEntries.setFont(font)
        self.txtBibEntries.setTabChangesFocus(True)
        self.txtBibEntries.setOpenLinks(False)
        self.txtBibEntries.setObjectName("txtBibEntries")
        self.gridLayout_2.addWidget(self.txtBibEntries, 0, 0, 1, 1)
        self.tabs.addTab(self.pageBibEntries, "")
        self.pageLog = QtWidgets.QWidget()
        self.pageLog.setObjectName("pageLog")
        self.gridLayout = QtWidgets.QGridLayout(self.pageLog)
        self.gridLayout.setContentsMargins(0, 0, 0, 8)
        self.gridLayout.setObjectName("gridLayout")
        self.txtLog = QtWidgets.QTextBrowser(self.pageLog)
        self.txtLog.setTabChangesFocus(True)
        self.txtLog.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-family:\'Courier 10 Pitch\';\"><br /></p></body></html>")
        self.txtLog.setAcceptRichText(False)
        self.txtLog.setOpenLinks(False)
        self.txtLog.setObjectName("txtLog")
        self.gridLayout.addWidget(self.txtLog, 0, 0, 1, 2)
        self.lblVerbosity = QtWidgets.QLabel(self.pageLog)
        self.lblVerbosity.setObjectName("lblVerbosity")
        self.gridLayout.addWidget(self.lblVerbosity, 1, 0, 1, 1)
        self.cbxVerbosity = QtWidgets.QComboBox(self.pageLog)
        self.cbxVerbosity.setObjectName("cbxVerbosity")
        self.cbxVerbosity.addItem("")
        self.cbxVerbosity.addItem("")
        self.cbxVerbosity.addItem("")
        self.cbxVerbosity.addItem("")
        self.gridLayout.addWidget(self.cbxVerbosity, 1, 1, 1, 1)
        self.tabs.addTab(self.pageLog, "")
        self.lyt.addWidget(self.tabs, 2, 0, 1, 1)
        self.wHead = QtWidgets.QWidget(OpenBibFile)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.wHead.sizePolicy().hasHeightForWidth())
        self.wHead.setSizePolicy(sizePolicy)
        self.wHead.setObjectName("wHead")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.wHead)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setSpacing(3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblFileName = QtWidgets.QLabel(self.wHead)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblFileName.sizePolicy().hasHeightForWidth())
        self.lblFileName.setSizePolicy(sizePolicy)
        self.lblFileName.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.lblFileName.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.lblFileName.setMidLineWidth(1)
        self.lblFileName.setTextFormat(QtCore.Qt.PlainText)
        self.lblFileName.setAlignment(QtCore.Qt.AlignCenter)
        self.lblFileName.setObjectName("lblFileName")
        self.horizontalLayout.addWidget(self.lblFileName)
        self.btnRefresh = QtWidgets.QToolButton(self.wHead)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/pic/refresh.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnRefresh.setIcon(icon1)
        self.btnRefresh.setIconSize(QtCore.QSize(22, 22))
        self.btnRefresh.setObjectName("btnRefresh")
        self.horizontalLayout.addWidget(self.btnRefresh)
        self.btnSave = QtWidgets.QToolButton(self.wHead)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/pic/save.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.btnSave.setIcon(icon2)
        self.btnSave.setIconSize(QtCore.QSize(22, 22))
        self.btnSave.setObjectName("btnSave")
        self.horizontalLayout.addWidget(self.btnSave)
        self.lyt.addWidget(self.wHead, 0, 0, 1, 1)

        self.retranslateUi(OpenBibFile)
        self.tabs.setCurrentIndex(0)
        self.stackEditTools.setCurrentIndex(3)
        self.cbxVerbosity.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(OpenBibFile)

    def retranslateUi(self, OpenBibFile):
        _translate = QtCore.QCoreApplication.translate
        self.btnGo.setText(_translate("OpenBibFile", "Run Bibolamazi !"))
        self.btnAddSourceList.setText(_translate("OpenBibFile", "add source list ..."))
        self.btnAddFilter.setText(_translate("OpenBibFile", "insert filter ..."))
        self.tabs.setTabText(self.tabs.indexOf(self.pageConfig), _translate("OpenBibFile", "Edit Bibolamazi Confguration"))
        self.txtInfo.setHtml(_translate("OpenBibFile", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'.SF NS Text\'; font-size:13pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:20px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-family:\'Lucida Grande\'; font-style:italic; color:#b1311d;\">&lt;no file open&gt;</span></p></body></html>"))
        self.tabs.setTabText(self.tabs.indexOf(self.pageInfo), _translate("OpenBibFile", "BIbolamazi File Info"))
        self.tabs.setTabText(self.tabs.indexOf(self.pageBibEntries), _translate("OpenBibFile", "Preview Bib Entries"))
        self.lblVerbosity.setText(_translate("OpenBibFile", "Log verbosity level (for next run):"))
        self.cbxVerbosity.setItemText(0, _translate("OpenBibFile", "Quiet"))
        self.cbxVerbosity.setItemText(1, _translate("OpenBibFile", "Information"))
        self.cbxVerbosity.setItemText(2, _translate("OpenBibFile", "Verbose"))
        self.cbxVerbosity.setItemText(3, _translate("OpenBibFile", "Very Verbose (for debugging)"))
        self.tabs.setTabText(self.tabs.indexOf(self.pageLog), _translate("OpenBibFile", "Messages"))
        self.lblFileName.setText(_translate("OpenBibFile", "some text here"))

from ..filterinstanceeditor import FilterInstanceEditor
from ..filterpackagepatheditor import FilterPackagePathEditor
from ..sourcelisteditor import SourceListEditor
from . import bibolamazi_res_rc
