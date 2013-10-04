

# -*- coding: utf-8 -*-


import core.main
from core import blogger
from core.blogger import logger
from core import bibfilterfile
from core import butils

import filters

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qtauto.ui_helpbrowser import Ui_HelpBrowser


class HelpBrowser(QWidget):
    def __init__(self):
        super(HelpBrowser, self).__init__()

        self.ui = Ui_HelpBrowser()
        self.ui.setupUi(self)

        QObject.connect(self.ui.tabs, SIGNAL('tabCloseRequested(int)'), self.closeTab)

        self.filterButtons = []

        for filt in filters.__all__:
            fbutton = QPushButton('%s' %(filt), self)
            fbutton.setProperty('filter', filt)
            fbutton.setToolTip(filters.get_filter_class(filt).getHelpDescription())
            self.ui.lytHomeFilterButtons.addWidget(fbutton)

            QObject.connect(fbutton, SIGNAL('clicked()'), self.showFilterHelp)


    @pyqtSlot(int)
    def closeTab(self, index):
        if (index == 0):
            return
        self.ui.tabs.removeTab(index)

    @pyqtSlot()
    def showFilterHelp(self):
        sender = self.sender()
        filtname = str(sender.property('filter').toString())
        if (not filtname):
            print "BAD FILTER NAME: %r" %(filtname)
            return
        
        tb = QTextBrowser(self.ui.tabs)
        font = self.font()
        font.setFamily("Courier 10 Pitch")
        tb.setFont(font)
        tb.setText(filters.format_filter_help(filtname))

        tabindex = self.ui.tabs.addTab(tb, 'Filter: %s' %(filtname))
        self.ui.tabs.setTabToolTip(tabindex, filters.get_filter_class(filtname).getHelpDescription())
        self.ui.tabs.setCurrentIndex(tabindex)
                            
