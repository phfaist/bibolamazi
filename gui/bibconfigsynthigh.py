
# -*- coding: utf-8 -*-

import re
from collections import namedtuple

# bibolamazi filters
import filters

from PyQt4.QtCore import *
from PyQt4.QtGui import *


## class BibConfigParsingCache(QTextBlockUserData):

##     FilterCmdInfo = namedtuple('FilterCmdInfo', ('line', 'filtername', ))
##     SourceListCmdInfo = namedtuple('SourceListCmdInfo', ('line', ))
    
    
##     def __init__(self):
##         super(BibConfigParsingCache, self).__init__()

##         self.cmdfilters = []
##         self.cmdsourcelists = []

##     def add_filter(self, line, filtername):
##         f = FilterCmdInfo(line=line, filtername=filtername)
##         self.cmdfilters.append(f)

##     def add_sourcelist(self, line):
##         s = SourceListCmdInfo(line=line)
##         self.cmdsourcelists.append(s)


rxsrc = re.compile(r'^\s*(?P<src>src:)', re.MULTILINE)
rxfilter = re.compile(r'^\s*(?P<filter>filter:)\s+(?P<filtername>[-\w]+)', re.MULTILINE)
rxcomment = re.compile(r'^\s*%%.*$', re.MULTILINE)
rxstring = re.compile(r'\"([^"\\]|\\\\|\\\")*\"')


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
                filtmodule = filters.get_module(m.group('filtername'))
            except filters.NoSuchFilter:
                fmtname = self.fmt_filtername_nonex
                
            #pcache.add_filter(line=blockno, filtername=m.group('filtername'))
                
            self.setFormat(m.start('filtername'), len(m.group('filtername')), fmtname)

        for m in rxstring.finditer(text):
            self.setFormat(m.start(), len(m.group()), self.fmt_string)

        for m in rxcomment.finditer(text):
            self.setFormat(m.start(), len(m.group()), self.fmt_comment)

        #self.setCurrentBlockState(0)
        #self.setCurrentBlockUserData(pcache)
