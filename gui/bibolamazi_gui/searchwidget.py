
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2013 by Philippe Faist                                       #
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

import logging

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import bibolamazi.init
from .qtauto.ui_searchwidget import Ui_SearchWidget


logger = logging.getLogger(__name__)


class SearchWidget(QWidget):
    def __init__(self, parent):
        super(SearchWidget, self).__init__(parent)

        self.u = Ui_SearchWidget()
        self.u.setupUi(self)

        self.default_palette = QPalette(self.u.txt.palette())
        self.found_palette = QPalette(self.u.txt.palette())
        self.notfound_palette = QPalette(self.u.txt.palette())

        self.found_palette.setBrush(QPalette.Base, QColor(180,255,180))
        self.notfound_palette.setBrush(QPalette.Base, QColor(255,180,180))

        self.u.btnDone.clicked.connect(self.hide)
        self.u.btnDone.clicked.connect(self.searchDone)

        self.u.txt.returnPressed.connect(self.findNext)
        self.u.txt.installEventFilter(self)

        self.setVisible(False)


    def eventFilter(self, object, event):
        if object is self.u.txt:
            if event.type() == QEvent.KeyPress and hasattr(event, 'matches'):
                if event.key() == Qt.Key_Escape:
                    self.searchDone.emit()
                    self.setVisible(False)
                    return True
                if event.matches(QKeySequence.FindNext):
                    self.findNext.emit()
                    return True
                if event.matches(QKeySequence.FindPrevious):
                    self.findPrev.emit()
                    return True

        return super(SearchWidget, self).eventFilter(object, event)
        


    def searchString(self):
        return self.u.txt.text()

    doSearch = pyqtSignal(str)
    searchDone = pyqtSignal()

    findNext = pyqtSignal()#str)
    findPrev = pyqtSignal()#str)

    @pyqtSlot()
    @pyqtSlot(str)
    def showSearch(self, searchstr=None):
        self.u.txt.setText(searchstr)
        self.u.txt.setPalette(self.default_palette)
        self.setVisible(True)
        self.u.txt.setFocus()

    @pyqtSlot()
    def showFound(self):
        self.u.txt.setPalette(self.found_palette)

    @pyqtSlot()
    def showNotFound(self):
        self.u.txt.setPalette(self.notfound_palette)

    @pyqtSlot(str)
    def on_txt_textChanged(self, s):
        self.doSearch.emit(s)

    @pyqtSlot()
    def on_btnNext_clicked(self):
        self.findNext.emit()#self.searchString())

    @pyqtSlot()
    def on_btnPrev_clicked(self):
        self.findPrev.emit()#self.searchString())

#


class SearchTextEditManager(QObject):
    def __init__(self, searchwidget, textedit):
        super(SearchTextEditManager, self).__init__()

        self.textedit = textedit
        self.textedit.installEventFilter(self)

        self.searchwidget = searchwidget

        self.pos = -1
        self.search_matches = None

        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor(255,255,128))
        self.highlight_format.setFontUnderline(True)
        self.highlight_format.setUnderlineColor(QColor(180,180,80))

        self.cur_highlight_format = QTextCharFormat()
        self.cur_highlight_format.setBackground(QColor(0,0,80))
        self.cur_highlight_format.setForeground(QColor(255,255,255))
        self.cur_highlight_format.setFontUnderline(True)
        self.cur_highlight_format.setUnderlineColor(QColor(128,128,128))

        self.searchwidget.doSearch.connect(self.doSearch)
        self.searchwidget.findNext.connect(self.findNext)
        self.searchwidget.findPrev.connect(self.findPrev)
        self.searchwidget.searchDone.connect(self.searchDone)
        

    def eventFilter(self, object, event):
        if object is self.textedit:
            if event.type() == QEvent.KeyPress and hasattr(event, 'matches'):
                if event.matches(QKeySequence.Find):
                    self.showSearch()
                    return True
                if event.matches(QKeySequence.FindNext):
                    self.showSearch(self.searchwidget.searchString())
                    self.findNext()
                    return True
                if event.matches(QKeySequence.FindPrevious):
                    self.showSearch(self.searchwidget.searchString())
                    self.findPrev()
                    return True

        return super(SearchTextEditManager, self).eventFilter(object, event)

    @pyqtSlot()
    @pyqtSlot(str)
    def showSearch(self, s=''):
        self.searchwidget.showSearch(s)
        self.pos = self.textedit.textCursor().position() - 1

    @pyqtSlot(str)
    def doSearch(self, s):
        self.search_matches = []

        doc = self.textedit.document()

        c = QTextCursor()
        while True:
            c = doc.find(s, c)
            if c.isNull():
                break
            self.search_matches.append(c)

        self._set_extra_selections()

        if len(self.search_matches):
            self.searchwidget.showFound()
        else:
            self.searchwidget.showNotFound()

    def _set_extra_selections(self):
        extrasels = []
        for m in self.search_matches:
            sel = QTextEdit.ExtraSelection()
            sel.cursor = m
            sel.format = (self.cur_highlight_format if m.position() == self.pos
                          else self.highlight_format)
            extrasels.append(sel)

        self.textedit.setExtraSelections(extrasels)

    @pyqtSlot()
    def searchDone(self):
        self.textedit.setExtraSelections([])
        self.search_matches = None
        self.pos = -1
        self.textedit.setFocus() # return focus to text edit


    def _start_cursor(self):
        c = QTextCursor(self.textedit.document())
        c.movePosition(QTextCursor.Start)
        return c

    def _nextmatch(self):
        if self.search_matches is None:
            self.doSearch(self.searchwidget.searchString())
        return next( ( cc for cc in self.search_matches if cc.position() > self.pos ),
                     QTextCursor() )

    def _prevmatch(self):
        if self.search_matches is None:
            self.doSearch(self.searchwidget.searchString())
        return next( (cc for cc in reversed(self.search_matches)
                      if self.pos < 0 or cc.position() < self.pos),
                     QTextCursor() )

    def _show_match(self, c):
        self.searchwidget.showFound()
        self.pos = c.position()
        self._set_extra_selections()
        
        c2 = QTextCursor(c)
        c2.clearSelection()
        self.textedit.setTextCursor(c2)
        self.textedit.ensureCursorVisible()

    def _show_notfound(self):
        self.textedit.setTextCursor(self._start_cursor())
        self.searchwidget.showNotFound()
        self.pos = -1
        self._set_extra_selections()

    @pyqtSlot()
    def findNext(self):
        cnext = self._nextmatch()
        if cnext.isNull():
            self._show_notfound()
            return

        self._show_match(cnext)

    @pyqtSlot()
    def findPrev(self):
        cprev = self._prevmatch()
        if cprev.isNull():
            self._show_notfound()
            return

        self._show_match(cprev)
