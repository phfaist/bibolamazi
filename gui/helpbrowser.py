
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


import core.main
from core import blogger
from core.blogger import logger
from core import butils
import core.argparseactions

import filters

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import filterinstanceeditor

from qtauto.ui_helpbrowser import Ui_HelpBrowser


class HelpBrowser(QWidget):
    def __init__(self):
        super(HelpBrowser, self).__init__()

        self.ui = Ui_HelpBrowser()
        self.ui.setupUi(self)

        QObject.connect(self.ui.tabs, SIGNAL('tabCloseRequested(int)'), self.closeTab)

        self.filterButtons = []

        self.openTabs = []

        for filt in filterinstanceeditor.get_filter_list():
            fbutton = QPushButton('%s' % (filt), self)
            fbutton.setProperty('helppath', 'filters/%s' %(filt))
            fbutton.setToolTip(filters.get_filter_class(filt).getHelpDescription())
            self.ui.lytHomeFilterButtons.addWidget(fbutton)

            QObject.connect(fbutton, SIGNAL('clicked()'), self.openHelpTopicBySender)


        static_help_btns = [ self.ui.btnWelcome,
                             self.ui.btnVersion,
                             self.ui.btnFilterList,
                             self.ui.btnCmdLineHelp
                             ]
        for btn in static_help_btns:
            QObject.connect(btn, SIGNAL('clicked()'), self.openHelpTopicBySender)

        self.shortcuts = [
            QShortcut(QKeySequence('Ctrl+W'), self, self.closeCurrentTab, self.closeCurrentTab),
            ]


    @pyqtSlot()
    def closeCurrentTab(self):
        index = self.ui.tabs.currentIndex()
        if (index == 0):
            # close help browser
            self.hide()
            return
        
        self.closeTab(index)

    @pyqtSlot(int)
    def closeTab(self, index):
        if (index == 0):
            return
        del self.openTabs[index-1]
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

        font = self.font()
        font.setFamily("Courier 10 Pitch")
        font.setStyleHint(QFont.TypeWriter)

        if (pathitems[0] == 'filters'):
            if (len(pathitems) < 2):
                print "No filter specified!!"
                return
            filtname = pathitems[1]

            tb = QTextBrowser(self.ui.tabs)
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
            tb.setFont(font)

            if pathitems[1] == 'welcome':
                tb.setPlainText(HELP_WELCOME)
                tb.setProperty('HelpTabTitle', 'Welcome')
            elif pathitems[1] == 'version':
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






HELP_WELCOME = """

---------------------------
Bibolamazi BibTeX Formatter
---------------------------

Collect bibliographic entries from BibTeX files and apply rules or filters to them.


What Bibolamazi Does
--------------------

Bibolamazi works by reading your reference bibtex files---the ``sources'', which
might for example have been generated by your favorite bibliography manager or
provided by your collaborators---and merging them all, applying specific rules,
or ``filters'', such as turning all the first names into initials or normalizing
the way arxiv IDs are presented.

The Bibolamazi file is in principle a new file, in which all the required bibtex
entries will be merged. When you prepare you LaTeX document, you should create a
new bibolamazi file, and provide that bibolamazi file as the bibtex file for the
bibliography.

When you open a bibolamazi file, you will be prompted to edit its configuration.
This is the set of rules which will tell bibolamazi where to look for your
bibtex entries and how to handle them. You first need to specify all your
sources, and then all the filters.


Sources
-------

Sources are the normal bibtex files from which bibtex entries are read. A source
is specified using the bibolamazi command

  src: source-file.bib  [ alternative-source-file.bib  ... ]

Alternative source locations can be specified, in case the first file does not
exist. This is convenient to locate a file which might be in different locations
on different computers. Each source file name can be an absolute path or a
relative path (relative to the bibolamazi file). It can also be an HTTP URL
which will be downloaded automatically.

You can specify several sources by repeating the src: command.

  src: first-source.bib  alternative-first-source.bib
  src: second-source.bib
  ...

Remember: the *first* readable source of *each* source command will be read, and
merged into the bibolamazi file.


Filters
-------

Filters are rules to apply on the whole bibliography database. Their syntax is

  filter: filter_name  <filter-options>

The filter is usually meant to deal with a particular task, such as for example
changing all first names of authors into initials.

For a list of filters and what they do, please refer the first page of this help
browser.

You can usually fine-tune the behavior of the filter by providing options. For
a list of options for a particular filter, please refer again to the help page
of that filter.


What now?
---------

We suggest at this point that you create a new bibolamazi file, and get started
with the serious stuff :)

If you want an example, you can have a look at the directory

  https://github.com/phfaist/bibolamazi/tree/master/test

and, in particular the bibolamazi file `output.bib`.


Command-line
------------

Please note that you can also use bibolamazi in command-line. If you installed
the binary, you'll need to install the command-line version again. Go to

  https://github.com/phfaist/bibolamazi

and follow the instructions there.

"""
