
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2018 by Philippe Faist                                       #
#   philippe.faist@bluewin.ch                                                  #
#                                                                              #
#   Bibolamazi is free software: you can redistribute it and/or modify         #
#   it under the terms of the GNU General Public License as published by       #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   Bibolamazi is distributed in the hope that it will be useful,              #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              #
#   GNU General Public License for more details.                               #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with Bibolamazi.  If not, see <http://www.gnu.org/licenses/>.        #
#                                                                              #
################################################################################

# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr

import sys
import os
import os.path
import re
import logging
import textwrap
import codecs
from html import escape as htmlescape

import bibolamazi.init
from bibolamazi.core import bibolamazifile

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .qtauto.ui_newbibolamazifiledialog import Ui_NewBibolamazifileDialog
from .sourcelisteditor import sanitize_bib_rel_path

logger = logging.getLogger(__name__)



# ------------------------------------------------------------------------------



class NewBibolamazifileDialog(QDialog):
    def __init__(self, parent=None):
        super(NewBibolamazifileDialog, self).__init__(parent)

        self.ui = Ui_NewBibolamazifileDialog()
        self.ui.setupUi(self)

        self.ui.txtSources.setHtml("""\
<!DOCTYPE HTML>
<html>
  <head>
    <style type="text/css">
p, li { white-space: pre-wrap; }
    </style>
  </head>
  <body>
    <p style="font-style:italic; color:#808080;">Please add source&nbsp;&nbsp;\N{RIGHTWARDS ARROW}</p>
  </body>
</html>
""")

        palette = self.ui.txtSources.palette()
        palette.setColor(QPalette.Base, palette.color(QPalette.Window))
        self.ui.txtSources.setPalette(palette)

        self.ui.btnSrcAdd.setVisible(False)
        self.ui.btnSrcClear.setVisible(False)
        self.ui.chkDuplicatesFilter.setVisible(False)

        self.ui.btnBack.setVisible(False)
        self.ui.btnSaveFinish.setVisible(False)

        self.ui.stk.setCurrentIndex(0)

        class _Ns: pass

        self.data = _Ns()
        self.data.src = []

        self.selected_save_fname = None


    bibolamaziFileCreated = pyqtSignal(str)

    def selectedSaveFileName(self):
        return self.selected_save_fname

    @pyqtSlot(int)
    def on_stk_currentChanged(self, pageno):
        self.ui.btnBack.setVisible(pageno > 0)
        if pageno == self.ui.stk.count()-1:
            self.ui.btnNext.setVisible(False)
            self.ui.btnSaveFinish.setVisible(True)
        else:
            self.ui.btnNext.setVisible(True)
            self.ui.btnSaveFinish.setVisible(False)

    @pyqtSlot()
    def on_btnNext_clicked(self):
        self.ui.stk.setCurrentIndex(self.ui.stk.currentIndex() + 1)

    @pyqtSlot()
    def on_btnBack_clicked(self):
        self.ui.stk.setCurrentIndex(self.ui.stk.currentIndex() - 1)

    @pyqtSlot()
    def on_btnSrcSet_clicked(self):
        
        fname, _filter = QFileDialog.getOpenFileName(self, 'Select BibTeX File', str(),
                                                     'BibTeX Files (*.bib);;All Files (*)')
        logger.debug("selected fname = %r", fname)
        if not fname:
            return

        self.data.src = [ fname ]
        self.updateSrcDisplay()

    @pyqtSlot()
    def on_btnSrcClear_clicked(self):
        
        self.data.src = [ ]
        self.updateSrcDisplay()

    @pyqtSlot()
    def on_btnSrcAdd_clicked(self):
        
        fnamelist, _filter = QFileDialog.getOpenFileNames(self, 'Select BibTeX File(s)', str(),
                                                          'BibTeX Files (*.bib);;All Files (*)')
        logger.debug("selected fname list = %r", fnamelist)
        if not fnamelist or not fnamelist[0]:
            return

        self.data.src += fnamelist
        self.updateSrcDisplay()

    def updateSrcDisplay(self):
        if self.data.src:
            html = "<html><head/><body>"
            if len(self.data.src) == 1:
                html += "<p>" + htmlescape(self.data.src[0]) + "</p>"
            else:
                html += "<ol>" + "".join([ "<li>"+htmlescape(x)+"</li>" for x in self.data.src ]) + "</ol>"
            html += "</body></html>"
            self.ui.txtSources.setHtml(html)
        else:
            self.ui.txtSources.setHtml(
                "<html><head/><body><p style=\"color: #808080; font-style:italic\">(no sources set)</p></body></html>"
            )


    @pyqtSlot(bool)
    def on_chkArxivUnpubIncludeTheses_toggled(self, on):
        self.ui.chkArxivPubIncludeTheses.setChecked(not on)
    
    @pyqtSlot(bool)
    def on_chkArxivPubIncludeTheses_toggled(self, on):
        self.ui.chkArxivUnpubIncludeTheses.setChecked(not on)


    @pyqtSlot()
    def on_btnSaveFinish_clicked(self):

        saveFileDialog = QFileDialog(self, "Create Bibolamazi File", str(),
                                     "Bibolamazi Files (*.bibolamazi.bib);;All Files (*)")
        if sys.platform.startswith('darwin'):
            # NOTE: BUG: OS X' file selection dialog won't understand the
            # .bibolamazi.bib extension. So use Qt's file dialog.
            saveFileDialog.setOptions(QFileDialog.DontUseNativeDialog)
        
        saveFileDialog.setDefaultSuffix("bibolamazi.bib")
        saveFileDialog.setAcceptMode(QFileDialog.AcceptSave)
        saveFileDialog.setFileMode(QFileDialog.AnyFile)
        if not saveFileDialog.exec_():
            return
        
        selectedfiles = saveFileDialog.selectedFiles()
        if not selectedfiles:
            return
        assert len(selectedfiles) == 1
        newfilename = selectedfiles[0]
            
        if (not newfilename):
            # cancelled maybe?
            return

        #if (os.path.exists(newfilename)):
        #    QMessageBox.critical(
        #        self, "File Exists",
        #        ("File %s already exists. Please select a file name to save to,"
        #         " without overwriting any existing file.")%(newfilename)
        #    )
        #    return self.on_btnSaveFinish_clicked()

        content = self.generateBibolamazifileConfig(ref_dir=os.path.dirname(newfilename))

        fullcontent = (bibolamazifile.TEMPLATE_HEADER + "\n" +
                       bibolamazifile.CONFIG_BEGIN_TAG + "\n"
                       "% " + content.replace("\n", "\n% ") + "\n" +
                       bibolamazifile.CONFIG_END_TAG + "\n\n")

        try:
            with codecs.open(newfilename, 'w', encoding='utf-8') as f:
                f.write(fullcontent)
        except Exception as e:
            QMessageBox.critical(self, "Error", "Error: Can't create file: %s"%(str(e)))
            return

        self.selected_save_fname = newfilename

        self.bibolamaziFileCreated.emit(newfilename)

        self.accept()

    
    def generateBibolamazifileConfig(self, ref_dir=None):

        srcmulti = self.ui.rdbtnMergeMultiple.isChecked()

        bibolamazi_config = """
%% This bibliography database uses BIBOLAMAZI:
%%
%%     https://github.com/phfaist/bibolamazi
%%
%% Use this file as your latex bibliography bibtex file, i.e.
%% \\bibliography{<this-file-name>.bibolamazi.bib}

%% This is the BIBOLAMAZI configuration section. Additional two leading
%% percent signs indicate comments within the configuration.

%% **** SOURCES ****

%% Specify where to get the bibtex entries from.  Alternatives may be specified
%% as several files for the same 'src:' command

"""

        if len(self.data.src):
            bibolamazi_config += "\n".join( [ 'src: '+sanitize_bib_rel_path(x, ref_dir=ref_dir)
                                              for x in self.data.src ] )
        else:
            bibolamazi_config += "src: <INSERT-SOURCE-PATH-HERE>"

        bibolamazi_config += """

%% Add additional sources here.

%% **** FILTERS ****

%% Specify filters here. Specify as many filters as you want, each with a
%% `filter:' directive. See also the "Help & Reference" information.

"""

        # merge duplicates?
        if srcmulti:
            if self.ui.chkDuplicatesFilter.isChecked():
                if self.ui.chkKeepOnlyUsed.isChecked():
                    bibolamazi_config += """\
%% Merge duplicates into a single bibtex entry and create aliases so that
%% \cite{...} commands may use either key interchangably
%%
%% Important: You must include "\\input{bibolamazi_dup_aliases.tex}" in the
%% preamble of your LaTeX document.
%%
%% Also, only keep entries that we actually use in the LaTeX document, and
%% discard any entries in the source bibtex files that we don't cite. NOTE: If
%% the LaTeX document has a different base name than the current bibolamazi
%% file, you need to set the -sJobname=documentname option here.
filter: duplicates -dMergeDuplicates
                   -dEnsureConflictKeysAreDuplicates
                   -sDupfile=bibolamazi_dup_aliases.tex
                   -dKeepOnlyUsed

"""
                else:
                    bibolamazi_config += """\
%% Merge duplicates into a single bibtex entry and create aliases so that
%% \cite{...} commands may use either key interchangably
%%
%% Important: You must include "\\input{bibolamazi_dup_aliases.tex}" in the
%% preamble of your LaTeX document.
filter: duplicates -dMergeDuplicates
                   -dEnsureConflictKeysAreDuplicates
                   -sDupfile=bibolamazi_dup_aliases.tex

"""
            else:
                if self.ui.chkKeepOnlyUsed.isChecked():
                    bibolamazi_config += """\
%% Don't merge duplicates, but make sure that any repeated entries between
%% different files *do* in fact refer to the same entry.
%%
%% Also, only keep entries that we actually use in the LaTeX document, and
%% discard any entries in the source bibtex files that we don't cite. NOTE: If
%% the LaTeX document has a different base name than the current bibolamazi
%% file, you need to set the -sJobname=documentname option here.
filter: duplicates -dMergeDuplicates=False
                   -dEnsureConflictKeysAreDuplicates
                   -dKeepOnlyUsed

"""
                else:
                    bibolamazi_config += """\
%% Don't merge duplicates, but make sure that any repeated entries between
%% different files *do* in fact refer to the same entry.
filter: duplicates -dMergeDuplicates=False -dEnsureConflictKeysAreDuplicates

"""

        else: # if not srcmulti
            if self.ui.chkKeepOnlyUsed.isChecked():
                bibolamazi_config += """\
%% Only keep entries that we actually use in the LaTeX document, and discard any
%% entries in the source bibtex files that we don't cite. NOTE: If the LaTeX
%% document has a different base name than the current bibolamazi file, you need
%% to set the -sJobname=documentname option here.
filter: only_used

"""

        if self.ui.chkFixesFilter.isChecked():
            fixesopts = []
            if self.ui.chkFixesGeneralSelection.isChecked():
                fixesopts += [ '-dFixSpaceAfterEscape', '-dRemoveTypeFromPhd', '-dRemoveFileField' ]
            if self.ui.chkFixesEncodeToLatex.isChecked():
                fixesopts += [ '-dEncodeUtf8ToLatex' ]

            bibolamazi_config += ("""\
%%%% Apply some general fixes & hacks
filter: fixes %(fixesoptstr)s

"""%dict(fixesoptstr="\n              ".join(fixesopts)))


        if self.ui.chkArxivUnpublished.isChecked():
            bibolamazi_config += """\
%% Format arxiv references for *unpublished* entries."""
            if self.ui.chkArxivUnpubIncludeTheses.isChecked():
                thesespublishedopt = '-dThesesCountAsPublished=False'
            else:
                thesespublishedopt = '-dThesesCountAsPublished'
            if self.ui.rdbtnArxivUnpub_eprint.isChecked():
                bibolamazi_config += ("""
%%%% Include a 'eprint = {...}' field with arXiv identifier:
filter: arxiv -sUnpublishedMode=eprint
              -sMode=none
              %(thesespublishedopt)s
              -dWarnJournalRef

"""%dict(thesespublishedopt=thesespublishedopt))
            elif self.ui.rdbtnArxivUnpub_unpubnote.isChecked():
                bibolamazi_config += ("""
%%%% Mark bibtex entry as type @unpublished{...}, and include a bibtex field
%%%% 'note = {arXiv:...}' with the arXiv identifier:
filter: arxiv -sUnpublishedMode=unpublished-note
              -sMode=none
              %(thesespublishedopt)s
              -dWarnJournalRef

"""%dict(thesespublishedopt=thesespublishedopt))
            else:
                logger.warning("arxiv unpublished was checked, but no explicit mode was set")
        
        if self.ui.chkArxivPublished.isChecked():
            bibolamazi_config += """\
%% Format arxiv references for entries considered as *published*."""
            if self.ui.chkArxivPubIncludeTheses.isChecked():
                thesespublishedopt = '-dThesesCountAsPublished'
            else:
                thesespublishedopt = '-dThesesCountAsPublished=False'
            if self.ui.rdbtnArxivPub_eprint.isChecked():
                bibolamazi_config += ("""
%%%% Include a 'eprint = {...}' field with arXiv identifier:
filter: arxiv -sMode=eprint
              -sUnpublishedMode=none
              %(thesespublishedopt)s

"""%dict(thesespublishedopt=thesespublishedopt))
            elif self.ui.rdbtnArxivPub_unpubnote.isChecked():
                bibolamazi_config += ("""
%%%% Include a 'note = {arXiv:...}' field with arXiv identifier:
filter: arxiv -sMode=note
              -sUnpublishedMode=none
              %(thesespublishedopt)s

"""%dict(thesespublishedopt=thesespublishedopt))
            elif self.ui.rdbtnArxivPub_strip.isChecked():
                bibolamazi_config += ("""
%%%% Strip out arxiv information entirely
filter: arxiv -sMode=strip
              -sUnpublishedMode=none
              %(thesespublishedopt)s

"""%dict(thesespublishedopt=thesespublishedopt))
            else:
                logger.warning("arxiv published was checked, but no explicit mode was set")
        

        if self.ui.chkUrlFilter.isChecked():
            urlopts = []
            if self.ui.chkUrlStrip.isChecked():
                urlopts.append('-dStrip')
            else:
                if self.ui.chkUrlStripAllIfDoiOrArxiv.isChecked():
                    urlopts.append('-dStripAllIfDoiOrArxiv')
                if self.ui.chkUrlStripDoiArxiv.isChecked():
                    urlopts += [ '-dStripDoiUrl', '-dStripArxivUrl' ]
                if self.ui.chkUrlKeepFirstUrlOnly.isChecked():
                    urlopts.append('-dKeepFirstUrlOnly')
            bibolamazi_config += ("""\
%%%% Clean up URLs in bibtex entries (the 'url = {...}' field)
filter: url %(urloptstr)s

"""%dict(urloptstr="\n            ".join(urlopts)))

        # always add the order_entries filter
        bibolamazi_config += """\
%% Order the entries in the final bibtex output. This has usually no effect on
%% the final bibliography formatting, but it avoids large file differences at
%% each run of bibolamazi (useful for instance when using git)
filter: orderentries -sOrder=alphabetical

"""

        return bibolamazi_config
