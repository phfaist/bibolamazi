

# -*- coding: utf-8 -*-


import core.main
from core import blogger
from core.blogger import logger
from core import butils
import core.argparseactions

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

        self.openTabs = []

        for filt in filters.__all__:
            fbutton = QPushButton('%s' % (filt), self)
            fbutton.setProperty('helppath', 'filters/%s' %(filt))
            fbutton.setToolTip(filters.get_filter_class(filt).getHelpDescription())
            self.ui.lytHomeFilterButtons.addWidget(fbutton)

            QObject.connect(fbutton, SIGNAL('clicked()'), self.openHelpTopicBySender)

        QObject.connect(self.ui.btnVersion, SIGNAL('clicked()'), self.openHelpTopicBySender)
        QObject.connect(self.ui.btnFilterList, SIGNAL('clicked()'), self.openHelpTopicBySender)
        QObject.connect(self.ui.btnCmdLineHelp, SIGNAL('clicked()'), self.openHelpTopicBySender)


    @pyqtSlot(int)
    def closeTab(self, index):
        if (index == 0):
            return
        self.ui.tabs.removeTab(index)


    @pyqtSlot()
    def openHelpTopicBySender(self):
        sender = self.sender()
        path = str(sender.property('helppath').toString())
        if (not path):
            print "Bad help topic path: %r" %(path)
            return

        self.openHelpTopic(path)
        

    @pyqtSlot(QString)
    def openHelpTopic(self, spath):
        path = str(spath)
        pathitems = [x for x in path.split('/') if x];


        # check to see if the tab is already open
        for tab in self.openTabs:
            if (str(tab.property('helppath').toString()) == "/".join(pathitems)):
                # just raise this tab.
                self.ui.tabs.setCurrentWidget(tab)
                return

        widget = self.makeHelpTopicTab(pathitems)
        if (widget is None):
            return
        widget.setProperty('helppath', "/".join(pathitems))

        tabindex = self.ui.tabs.addTab(widget, widget.property('HelpTabTitle').toString())
        self.ui.tabs.setTabToolTip(tabindex, widget.property('HelpTabToolTip').toString())
        self.ui.tabs.setCurrentIndex(tabindex)

        self.openTabs.append(widget)



    def makeHelpTopicTab(self, pathitems):
        if (not len(pathitems)):
            print "No Path specified!"
            return

        if (pathitems[0] == 'filters'):
            if (len(pathitems) < 2):
                print "No filter specified!!"
                return
            filtname = pathitems[1]

            tb = QTextBrowser(self.ui.tabs)
            font = self.font()
            font.setFamily("Courier 10 Pitch")
            tb.setFont(font)
            tb.setText(filters.format_filter_help(filtname))

            tb.setProperty('HelpTabTitle', '%s filter' %(filtname))
            tb.setProperty('HelpTabToolTip', filters.get_filter_class(filtname).getHelpDescription())
            return tb

        if (pathitems[0] == 'general'):
            if (len(pathitems) < 2):
                print "No help topic general page specified!!"
                return

            tb = QTextBrowser(self.ui.tabs)
            font = self.font()
            font.setFamily("Courier 10 Pitch")
            tb.setFont(font)

            if pathitems[1] == 'version':
                tb.setPlainText(core.argparseactions.helptext_prolog())
                tb.setProperty('HelpTabTitle', 'Version')
            elif pathitems[1] == 'cmdline':
                tb.setPlainText(core.argparseactions.helptext_prolog() +
                                core.main.get_args_parser().format_help())
                tb.setProperty('HelpTabTitle', 'Command-Line Help')
            elif pathitems[1] == 'filter-list':
                tb.setPlainText(core.argparseactions.help_list_filters())
                tb.setProperty('HelpTabTitle', 'Filter List')
            else:
                tb.setPlainText('<Unknown help page>')
                tb.setProperty('HelpTabTitle', '<Unknown>')

            tb.setProperty('HelpTabToolTip', '')
            return tb
                
        print "Unknown help topic: %r" %("/".join(pathitems))
        return None
