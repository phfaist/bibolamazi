
# -*- coding: utf-8 -*-

import re



from PyQt4.QtCore import *
from PyQt4.QtGui import *


rxsrc = re.compile(r'^\s*(?P<src>src:)', re.MULTILINE)
rxfilter = re.compile(r'^\s*(?P<filter>filter:)\s+(?P<filtername>[-\w]+)', re.MULTILINE)
rxcomment = re.compile(r'^\s*%%.*$', re.MULTILINE)
rxstring = re.compile(r'\"([^"]|(?<!\\)\")\"')


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

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor(127,127,127))
        self.fmt_comment.setFontItalic(True)

        self.fmt_string = QTextCharFormat()
        self.fmt_string.setForeground(QColor(0,127,0))


    def highlightBlock(self, text):
        print "synt highlighter highlightBlock!"

        self.setFormat(0, 10, self.fmt_src);
        
        for m in rxsrc.finditer(text):
            self.setFormat(m.start('src'), m.end('src'), self.fmt_src)

        for m in rxfilter.finditer(text):
            self.setFormat(m.start('filter'), m.end('filter'), self.fmt_filter)
            self.setFormat(m.start('filtername'), m.end('filtername'), self.fmt_filtername)

        for m in rxcomment.finditer(text):
            self.setFormat(m.start(), m.end(), self.fmt_comment)

        for m in rxstring.finditer(text):
            self.setFormat(m.start(), m.end(), self.fmt_string)

        self.setCurrentBlockState(0)
