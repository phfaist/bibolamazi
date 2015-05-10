
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


import re
from collections import namedtuple

import bibolamazi.init
# bibolamazi filters
from bibolamazi.core.bibfilter import factory as filters_factory

from PyQt4.QtCore import *
from PyQt4.QtGui import *



rxsrc = re.compile(r'^\s*(?P<src>src:)', re.MULTILINE)
rxfilter = re.compile(r'^\s*(?P<filter>filter:)\s+(?P<filtername>[-:\w]+)', re.MULTILINE)
rxcomment = re.compile(r'^\s*%%.*$', re.MULTILINE)
_rx_not_odd_num_backslashes = r'(((?<=[^\\])|^)(\\\\)*)';
rxstring1 = re.compile(_rx_not_odd_num_backslashes+r'(?P<str>\"([^"\\]|\\\\|\\\")*\")', re.MULTILINE)
rxstring2 = re.compile(_rx_not_odd_num_backslashes+r"(?P<str>\'[^']*\')", re.MULTILINE)


class BibolamaziConfigSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(BibolamaziConfigSyntaxHighlighter, self).__init__(parent)

        self.fmt_src = QTextCharFormat()
        self.fmt_src.setFontWeight(QFont.Bold)
        self.fmt_src.setForeground(QColor(0, 127, 127))

        self.fmt_filter = QTextCharFormat()
        self.fmt_filter.setFontWeight(QFont.Bold)
        self.fmt_filter.setForeground(QColor(127,0,0))

        self.fmt_filtername = QTextCharFormat()
        self.fmt_filtername.setForeground(QColor(0, 0, 127))

        self.fmt_filtername_nonex = QTextCharFormat(self.fmt_filtername)
        self.fmt_filtername_nonex.setUnderlineStyle(QTextCharFormat.SpellCheckUnderline)

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor(127,127,127))
        self.fmt_comment.setFontItalic(True)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(QColor(0,127,0))


    def highlightBlock(self, text):

        #pcache = BibConfigParsingCache()
        
        blockno = self.currentBlock().blockNumber()

        for m in rxsrc.finditer(text):
            self.setFormat(m.start('src'), len(m.group('src')), self.fmt_src)
            #pcache.add_sourcelist(line=blockno)

        for m in rxfilter.finditer(text):
            self.setFormat(m.start('filter'), len(m.group('filter')), self.fmt_filter)
            fmtname = self.fmt_filtername
            try:
                # try to load the filter module to see if it exists
                filtmodule = filters_factory.get_module(m.group('filtername'))
            except (filters_factory.NoSuchFilter, filters_factory.NoSuchFilterPackage):
                fmtname = self.fmt_filtername_nonex

            #pcache.add_filter(line=blockno, filtername=m.group('filtername'))
                
            self.setFormat(m.start('filtername'), len(m.group('filtername')), fmtname)

        for m in rxstring1.finditer(text):
            self.setFormat(m.start('str'), len(m.group('str')), self.fmt_string)
        for m in rxstring2.finditer(text):
            self.setFormat(m.start('str'), len(m.group('str')), self.fmt_string)

        for m in rxcomment.finditer(text):
            self.setFormat(m.start(), len(m.group()), self.fmt_comment)

        #self.setCurrentBlockState(0)
        #self.setCurrentBlockUserData(pcache)
