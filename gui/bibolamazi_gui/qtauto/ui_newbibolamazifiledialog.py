# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newbibolamazifiledialog.ui'
#
# Created by: PyQt5 UI code generator 5.7.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NewBibolamazifileDialog(object):
    def setupUi(self, NewBibolamazifileDialog):
        NewBibolamazifileDialog.setObjectName("NewBibolamazifileDialog")
        NewBibolamazifileDialog.resize(547, 533)
        NewBibolamazifileDialog.setSizeGripEnabled(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(NewBibolamazifileDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(NewBibolamazifileDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(0, 30))
        font = QtGui.QFont()
        font.setItalic(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.stk = QtWidgets.QStackedWidget(NewBibolamazifileDialog)
        self.stk.setObjectName("stk")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName("page")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.page)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.srcmulti = QtWidgets.QGroupBox(self.page)
        self.srcmulti.setObjectName("srcmulti")
        self.gridLayout = QtWidgets.QGridLayout(self.srcmulti)
        self.gridLayout.setObjectName("gridLayout")
        self.rdbtnMergeMultiple = QtWidgets.QRadioButton(self.srcmulti)
        self.rdbtnMergeMultiple.setObjectName("rdbtnMergeMultiple")
        self.gridLayout.addWidget(self.rdbtnMergeMultiple, 1, 0, 1, 2)
        self.rdbtnSingleSource = QtWidgets.QRadioButton(self.srcmulti)
        self.rdbtnSingleSource.setChecked(True)
        self.rdbtnSingleSource.setObjectName("rdbtnSingleSource")
        self.gridLayout.addWidget(self.rdbtnSingleSource, 0, 0, 1, 2)
        self.verticalLayout_2.addWidget(self.srcmulti)
        self.groupBox_2 = QtWidgets.QGroupBox(self.page)
        self.groupBox_2.setObjectName("groupBox_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lblSources = QtWidgets.QLabel(self.groupBox_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lblSources.sizePolicy().hasHeightForWidth())
        self.lblSources.setSizePolicy(sizePolicy)
        self.lblSources.setWordWrap(True)
        self.lblSources.setObjectName("lblSources")
        self.horizontalLayout.addWidget(self.lblSources)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.btnSrcSet = QtWidgets.QPushButton(self.groupBox_2)
        self.btnSrcSet.setObjectName("btnSrcSet")
        self.horizontalLayout_2.addWidget(self.btnSrcSet)
        self.btnSrcAdd = QtWidgets.QPushButton(self.groupBox_2)
        self.btnSrcAdd.setObjectName("btnSrcAdd")
        self.horizontalLayout_2.addWidget(self.btnSrcAdd)
        self.btnSrcClear = QtWidgets.QPushButton(self.groupBox_2)
        self.btnSrcClear.setObjectName("btnSrcClear")
        self.horizontalLayout_2.addWidget(self.btnSrcClear)
        self.horizontalLayout.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        self.chkDuplicatesFilter = QtWidgets.QGroupBox(self.page)
        self.chkDuplicatesFilter.setCheckable(True)
        self.chkDuplicatesFilter.setObjectName("chkDuplicatesFilter")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.chkDuplicatesFilter)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_5 = QtWidgets.QLabel(self.chkDuplicatesFilter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_5.sizePolicy().hasHeightForWidth())
        self.label_5.setSizePolicy(sizePolicy)
        self.label_5.setWordWrap(True)
        self.label_5.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_5.addWidget(self.label_5)
        self.verticalLayout_2.addWidget(self.chkDuplicatesFilter)
        spacerItem = QtWidgets.QSpacerItem(20, 1, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.stk.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName("page_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.chkArxivUnpublished = QtWidgets.QGroupBox(self.page_2)
        self.chkArxivUnpublished.setCheckable(True)
        self.chkArxivUnpublished.setObjectName("chkArxivUnpublished")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.chkArxivUnpublished)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.rdbtnArxivUnpub_unpubnote = QtWidgets.QRadioButton(self.chkArxivUnpublished)
        self.rdbtnArxivUnpub_unpubnote.setObjectName("rdbtnArxivUnpub_unpubnote")
        self.gridLayout_2.addWidget(self.rdbtnArxivUnpub_unpubnote, 2, 0, 1, 1)
        self.rdbtnArxivUnpub_eprint = QtWidgets.QRadioButton(self.chkArxivUnpublished)
        self.rdbtnArxivUnpub_eprint.setChecked(True)
        self.rdbtnArxivUnpub_eprint.setObjectName("rdbtnArxivUnpub_eprint")
        self.gridLayout_2.addWidget(self.rdbtnArxivUnpub_eprint, 1, 0, 1, 1)
        self.chkArxivUnpubIncludeTheses = QtWidgets.QCheckBox(self.chkArxivUnpublished)
        self.chkArxivUnpubIncludeTheses.setChecked(True)
        self.chkArxivUnpubIncludeTheses.setObjectName("chkArxivUnpubIncludeTheses")
        self.gridLayout_2.addWidget(self.chkArxivUnpubIncludeTheses, 3, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.chkArxivUnpublished)
        self.chkArxivPublished = QtWidgets.QGroupBox(self.page_2)
        self.chkArxivPublished.setCheckable(True)
        self.chkArxivPublished.setObjectName("chkArxivPublished")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.chkArxivPublished)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.rdbtnArxivPub_eprint = QtWidgets.QRadioButton(self.chkArxivPublished)
        self.rdbtnArxivPub_eprint.setChecked(True)
        self.rdbtnArxivPub_eprint.setObjectName("rdbtnArxivPub_eprint")
        self.verticalLayout_7.addWidget(self.rdbtnArxivPub_eprint)
        self.rdbtnArxivPub_unpubnote = QtWidgets.QRadioButton(self.chkArxivPublished)
        self.rdbtnArxivPub_unpubnote.setObjectName("rdbtnArxivPub_unpubnote")
        self.verticalLayout_7.addWidget(self.rdbtnArxivPub_unpubnote)
        self.rdbtnArxivPub_strip = QtWidgets.QRadioButton(self.chkArxivPublished)
        self.rdbtnArxivPub_strip.setObjectName("rdbtnArxivPub_strip")
        self.verticalLayout_7.addWidget(self.rdbtnArxivPub_strip)
        self.chkArxivPubIncludeTheses = QtWidgets.QCheckBox(self.chkArxivPublished)
        self.chkArxivPubIncludeTheses.setObjectName("chkArxivPubIncludeTheses")
        self.verticalLayout_7.addWidget(self.chkArxivPubIncludeTheses)
        self.verticalLayout_3.addWidget(self.chkArxivPublished)
        self.chkUrlFilter = QtWidgets.QGroupBox(self.page_2)
        self.chkUrlFilter.setCheckable(True)
        self.chkUrlFilter.setObjectName("chkUrlFilter")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.chkUrlFilter)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.chkUrlStrip = QtWidgets.QCheckBox(self.chkUrlFilter)
        self.chkUrlStrip.setObjectName("chkUrlStrip")
        self.verticalLayout_8.addWidget(self.chkUrlStrip)
        self.chkUrlStripAllIfDoiOrArxiv = QtWidgets.QCheckBox(self.chkUrlFilter)
        self.chkUrlStripAllIfDoiOrArxiv.setChecked(True)
        self.chkUrlStripAllIfDoiOrArxiv.setObjectName("chkUrlStripAllIfDoiOrArxiv")
        self.verticalLayout_8.addWidget(self.chkUrlStripAllIfDoiOrArxiv)
        self.chkUrlStripDoiArxiv = QtWidgets.QCheckBox(self.chkUrlFilter)
        self.chkUrlStripDoiArxiv.setChecked(True)
        self.chkUrlStripDoiArxiv.setObjectName("chkUrlStripDoiArxiv")
        self.verticalLayout_8.addWidget(self.chkUrlStripDoiArxiv)
        self.chkUrlKeepFirstUrlOnly = QtWidgets.QCheckBox(self.chkUrlFilter)
        self.chkUrlKeepFirstUrlOnly.setChecked(True)
        self.chkUrlKeepFirstUrlOnly.setObjectName("chkUrlKeepFirstUrlOnly")
        self.verticalLayout_8.addWidget(self.chkUrlKeepFirstUrlOnly)
        self.verticalLayout_3.addWidget(self.chkUrlFilter)
        spacerItem1 = QtWidgets.QSpacerItem(20, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.stk.addWidget(self.page_2)
        self.page_3 = QtWidgets.QWidget()
        self.page_3.setObjectName("page_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.page_3)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.chkFixesFilter = QtWidgets.QGroupBox(self.page_3)
        self.chkFixesFilter.setCheckable(True)
        self.chkFixesFilter.setObjectName("chkFixesFilter")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.chkFixesFilter)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.chkFixesGeneralSelection = QtWidgets.QCheckBox(self.chkFixesFilter)
        self.chkFixesGeneralSelection.setChecked(True)
        self.chkFixesGeneralSelection.setObjectName("chkFixesGeneralSelection")
        self.verticalLayout_6.addWidget(self.chkFixesGeneralSelection)
        self.chkFixesEncodeToLatex = QtWidgets.QCheckBox(self.chkFixesFilter)
        self.chkFixesEncodeToLatex.setChecked(True)
        self.chkFixesEncodeToLatex.setObjectName("chkFixesEncodeToLatex")
        self.verticalLayout_6.addWidget(self.chkFixesEncodeToLatex)
        self.verticalLayout_4.addWidget(self.chkFixesFilter)
        self.chkKeepOnlyUsed = QtWidgets.QGroupBox(self.page_3)
        self.chkKeepOnlyUsed.setCheckable(True)
        self.chkKeepOnlyUsed.setObjectName("chkKeepOnlyUsed")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.chkKeepOnlyUsed)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_4 = QtWidgets.QLabel(self.chkKeepOnlyUsed)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)
        self.verticalLayout_4.addWidget(self.chkKeepOnlyUsed)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_4.addItem(spacerItem2)
        self.stk.addWidget(self.page_3)
        self.verticalLayout.addWidget(self.stk)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.btnCancel = QtWidgets.QPushButton(NewBibolamazifileDialog)
        self.btnCancel.setObjectName("btnCancel")
        self.horizontalLayout_3.addWidget(self.btnCancel)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.btnNext = QtWidgets.QPushButton(NewBibolamazifileDialog)
        self.btnNext.setObjectName("btnNext")
        self.horizontalLayout_3.addWidget(self.btnNext)
        self.btnSaveFinish = QtWidgets.QPushButton(NewBibolamazifileDialog)
        self.btnSaveFinish.setObjectName("btnSaveFinish")
        self.horizontalLayout_3.addWidget(self.btnSaveFinish)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(NewBibolamazifileDialog)
        self.stk.setCurrentIndex(1)
        self.rdbtnSingleSource.toggled['bool'].connect(self.btnSrcSet.setVisible)
        self.rdbtnMergeMultiple.toggled['bool'].connect(self.btnSrcAdd.setVisible)
        self.rdbtnMergeMultiple.toggled['bool'].connect(self.btnSrcClear.setVisible)
        self.rdbtnMergeMultiple.toggled['bool'].connect(self.chkDuplicatesFilter.setVisible)
        self.btnCancel.clicked.connect(NewBibolamazifileDialog.reject)
        self.chkUrlStrip.toggled['bool'].connect(self.chkUrlStripAllIfDoiOrArxiv.setDisabled)
        self.chkUrlStrip.toggled['bool'].connect(self.chkUrlKeepFirstUrlOnly.setDisabled)
        self.chkUrlStrip.toggled['bool'].connect(self.chkUrlStripDoiArxiv.setDisabled)
        QtCore.QMetaObject.connectSlotsByName(NewBibolamazifileDialog)

    def retranslateUi(self, NewBibolamazifileDialog):
        _translate = QtCore.QCoreApplication.translate
        NewBibolamazifileDialog.setWindowTitle(_translate("NewBibolamazifileDialog", "Create new bibolamazi file"))
        self.label.setText(_translate("NewBibolamazifileDialog", "So you\'d like to organize your bibtex entries..."))
        self.srcmulti.setTitle(_translate("NewBibolamazifileDialog", "Would you like to collect bibliography entries from several bibtex files?"))
        self.rdbtnMergeMultiple.setText(_translate("NewBibolamazifileDialog", "I would like to merge bibliography entries from different files"))
        self.rdbtnSingleSource.setText(_translate("NewBibolamazifileDialog", "My bibliography entries are currently all in one bibtex file"))
        self.groupBox_2.setTitle(_translate("NewBibolamazifileDialog", "Specify sources where to collect bibtex entries from"))
        self.lblSources.setText(_translate("NewBibolamazifileDialog", "<html><head/><body><p style=\"font-style:italic; color: #808080;\">Please add source&nbsp;&nbsp;&nbsp;→</p></body></html>"))
        self.btnSrcSet.setText(_translate("NewBibolamazifileDialog", "set"))
        self.btnSrcAdd.setText(_translate("NewBibolamazifileDialog", "add"))
        self.btnSrcClear.setText(_translate("NewBibolamazifileDialog", "clear"))
        self.chkDuplicatesFilter.setTitle(_translate("NewBibolamazifileDialog", "Merge duplicate entries with different key names && create aliases"))
        self.label_5.setText(_translate("NewBibolamazifileDialog", "<html><head/><body>\n"
"<p>Citing the same article using different keys, such as <code>\\cite{Einstein1937}</code> and <code>\\cite{EPRpaper}</code> will refer to the same bibliography entry.</p>\n"
"<p style=\"font-style:italic\">In order for this to work, you need to add the following line in the preamble of your document:</p><pre>\\input{bibolamazi_dup_aliases.tex}</pre></body></html>"))
        self.chkArxivUnpublished.setTitle(_translate("NewBibolamazifileDialog", "Normalize arxiv fields in entries, for *unpublished* entries"))
        self.rdbtnArxivUnpub_unpubnote.setText(_translate("NewBibolamazifileDialog", "Set entry type to @unpublished and add \"note = {arXiv:XXXX.ZZZZZ}\""))
        self.rdbtnArxivUnpub_eprint.setText(_translate("NewBibolamazifileDialog", "Use \"eprint\" field, like \"eprint = {XXXX.ZZZZZ}\""))
        self.chkArxivUnpubIncludeTheses.setText(_translate("NewBibolamazifileDialog", "Include theses as unpublished entries"))
        self.chkArxivPublished.setTitle(_translate("NewBibolamazifileDialog", "Normalize arxiv fields in entries, for *published* entries"))
        self.rdbtnArxivPub_eprint.setText(_translate("NewBibolamazifileDialog", "Use \"eprint\" field, like \"eprint = {XXXX.ZZZZZ}\""))
        self.rdbtnArxivPub_unpubnote.setText(_translate("NewBibolamazifileDialog", "Add \"note = {arXiv:XXXX.ZZZZZ}\""))
        self.rdbtnArxivPub_strip.setText(_translate("NewBibolamazifileDialog", "Strip arxiv information entirely from published entries"))
        self.chkArxivPubIncludeTheses.setText(_translate("NewBibolamazifileDialog", "Include theses as published entries"))
        self.chkUrlFilter.setTitle(_translate("NewBibolamazifileDialog", "Fix URLs"))
        self.chkUrlStrip.setText(_translate("NewBibolamazifileDialog", "Remove all URLs"))
        self.chkUrlStripAllIfDoiOrArxiv.setText(_translate("NewBibolamazifileDialog", "Remove all URLs if there is an arXiv id or a DOI"))
        self.chkUrlStripDoiArxiv.setText(_translate("NewBibolamazifileDialog", "Remove URLs that simply refer to a DOI or to an arxiv page"))
        self.chkUrlKeepFirstUrlOnly.setText(_translate("NewBibolamazifileDialog", "Keep only the first URL available"))
        self.chkFixesFilter.setTitle(_translate("NewBibolamazifileDialog", "Apply general fixes"))
        self.chkFixesGeneralSelection.setText(_translate("NewBibolamazifileDialog", "Include a selection of general fixes"))
        self.chkFixesEncodeToLatex.setText(_translate("NewBibolamazifileDialog", "Encode accents and special characters into LaTeX"))
        self.chkKeepOnlyUsed.setTitle(_translate("NewBibolamazifileDialog", "Keep only entries that I actually use in my LaTeX document"))
        self.label_4.setText(_translate("NewBibolamazifileDialog", "<html><body><p style=\"font-style:italic\">Make sure when you save the bibolamazi file to give it the same base name as your LaTeX document. For instance, if your document is named <code>example.tex</code>, save the bibolamazifile as <code>example.bibolamazi.bib</code>.</p></body></html>"))
        self.btnCancel.setText(_translate("NewBibolamazifileDialog", "cancel"))
        self.btnNext.setText(_translate("NewBibolamazifileDialog", "next ▶"))
        self.btnSaveFinish.setText(_translate("NewBibolamazifileDialog", "save file ▶"))

