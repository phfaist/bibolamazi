
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

import re
import os
import os.path
import logging
logger = logging.getLogger(__name__)


from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import bibolamazi.init

from .qtauto.ui_sourcelisteditor import Ui_SourceListEditor

from . import helpbrowser
from .helpbrowser import htmlescape


def sanitize_bib_rel_path(fname, ref_dir=None):
    # decide on whether to refer to file in absolute or relative fashion
    if (ref_dir):
        relpath = os.path.relpath(os.path.realpath(fname), os.path.realpath(ref_dir))
        if '..' in relpath.split(os.sep) or '..' in relpath.split(os.altsep):
            # out of scope, so use absolute.
            pass
        else:
            # can easily be referred to by relative path (in same or sub directory), use relative.
            fname = relpath

    homeprefix = os.path.expanduser("~") + os.sep
    if fname.startswith(homeprefix):
        fname = "~/"+fname[len(homeprefix):]

    return fname



class SourceListEditor(QWidget):
    def __init__(self, parent):
        super(SourceListEditor, self).__init__(parent)

        self.ui = Ui_SourceListEditor()
        self.ui.setupUi(self)
        
        self.ui.lblLinkInfo.setVisible(False)

        self.ui.btnAddFavorite.clicked.connect(self.requestAddToFavorites)

        self.sourcelist = []

        #self.ui.lstSources.model().layoutChanged.connect(self.update_stuff_moved)
        #self._is_updating = False

        self._ref_dir = None


    sourceListChanged = pyqtSignal('QStringList')

    requestAddToFavorites = pyqtSignal()
    requestAddSourceList = pyqtSignal()
    

    def sourceList(self):
        if self._erorr_state:
            logger.warning("SourceListEditor's error state is on! don't call sourceList()!")
        return self.sourcelist
        #return [str(self.ui.lstSources.item(i).text())  for i in range(self.ui.lstSources.count())]


    def setRefDir(self, refdir):
        """Sets the \"reference\" directory, which is the directory in which the bibolamazi
        file being edited resides. This is used to decide on whether to refer to a file with
        an absolute or a relative path.
        """
        self._ref_dir = refdir
        

    @pyqtSlot('QStringList')
    def dispSourceListError(self, errormsg):
        self._error_state = True

        self.ui.lbl.setText("<p style=\"color: #800000;\">" +
                            "<b>Parse error:</b> " + htmlescape(errormsg) + "</p>")

    @pyqtSlot('QStringList', bool)
    @pyqtSlot('QStringList')
    def setSourceList(self, newsourcelist, noemit=False):
        self._error_state = False

        newsourcelist = [str(x) for x in list(newsourcelist)]
        
        # don't reset source list if it's the same. In particular, don't emit the changed signal.
        if (newsourcelist == self.sourcelist):
            return

        self.sourcelist = newsourcelist
        self._updated_source_list(noemit=noemit)

    def _updated_source_list(self, noemit=False):
        if self._error_state:
            logger.warning("SourceListEditor's error state is on, don't call _updated_source_list()!")

        def htmlforsrc(i, x):
            code = htmlescape(str(x))
            code += " <a href=\"srcaction:/change/"+str(i)+"\">[\N{HORIZONTAL ELLIPSIS}]</a>"
            if len(self.sourcelist) > 1:
                code += " <a href=\"srcaction:/remove/"+str(i)+"\">[\N{MINUS SIGN}]</a>"
            if i > 0:
                code += " <a href=\"srcaction:/up/"+str(i)+"\">[\N{BLACK UP-POINTING TRIANGLE}]</a>"
            if i < len(self.sourcelist)-1:
                code += " <a href=\"srcaction:/down/"+str(i)+"\">[\N{BLACK DOWN-POINTING TRIANGLE}]</a>"
            return "<p>\N{BLACK RIGHT-POINTING SMALL TRIANGLE} " + code + "</p>"

        if not self.sourcelist:
            self.sourcelist = ['<not set>']

        fileitems = [ htmlforsrc(i,x) for i,x in enumerate(self.sourcelist) ]
        items = fileitems[0]
        if len(fileitems) > 1:
            items += "<p class=\"heading\">Alternatives:</p>" + "".join(fileitems[1:])
        items += ("<p><a href=\"srcaction:/add_alternative/-1\">add alternative source "
                  "location \N{HORIZONTAL ELLIPSIS}</a></p>")
        items += "<p>&nbsp;</p>"

        lbltext = """\
<!DOCTYPE HTML>
<html><head><style type="text/css">
%(basecss)s
.heading { font-style: italic; }
</style></head>
<body>
<p class=\"heading\">Source:</p>
%(sourceitems)s</body></html>
""" % {
    'basecss': helpbrowser.getCssHelpStyle(),
    'sourceitems': items
    }
        #lbltext = ("<ul>" + items + "</ul>")

        self.ui.lbl.setText(lbltext)

        if not noemit:
            self.emitSourceListChanged()

    @pyqtSlot(str)
    def on_lbl_linkHovered(self, link):
        if self._error_state:
            logger.debug("SourceListEditor: Ignoring link interaction while error state is on")
            return

        if not link:
            # link un-hovered
            self.ui.lblLinkInfo.setText("")
            self.ui.lblLinkInfo.setVisible(False)
            return
            
        self.ui.lblLinkInfo.setVisible(True)

        m = re.match(r'^srcaction:/(?P<action>[a-zA-Z0-9_-]+)/(?P<num>[-0-9]+)$', link)
        if m is None:
            logger.warning("Invalid action link: %r", link)
            return
        action = m.group('action')
        i = int(m.group('num'))
        if action == 'change':
            self.ui.lblLinkInfo.setText("Select a new file to replace the current one.")
        elif action == 'remove':
            self.ui.lblLinkInfo.setText("Remove this source location")
        elif action == 'up':
            self.ui.lblLinkInfo.setText("Promote this alternative source location to higher priority")
        elif action == 'down':
            self.ui.lblLinkInfo.setText("Demote this alternative source location to lower priority")
        elif action == 'add_alternative':
            self.ui.lblLinkInfo.setText(
                "Specify an additional bibtex file location where this source can be found.  "
                "This might be useful, for instance, if between different computers or "
                "different collaborators the source bibtex files are stored at different locations."
            )
        else:
            logger.warning("Invalid action link: %r (bad action %r)", link, action)


    @pyqtSlot(str)
    def on_lbl_linkActivated(self, link):

        if self._error_state:
            logger.debug("SourceListEditor: Ignoring link interaction while error state is on")
            return

        m = re.match(r'^srcaction:/(?P<action>[a-zA-Z0-9_-]+)/(?P<num>[-0-9]+)$', link)
        if m is None:
            logger.warning("Invalid action link: %r", link)
            return

        action = m.group('action')
        i = int(m.group('num'))
        if action == 'change':
            self.changeSource(i)
        elif action == 'remove':
            if len(self.sourcelist) > 1:
                del self.sourcelist[i]
                self._updated_source_list()
        elif action == 'up':
            if i > 0:
                self.sourcelist[i], self.sourcelist[i-1] = self.sourcelist[i-1], self.sourcelist[i]
                self._updated_source_list()
        elif action == 'down':
            if i < len(self.sourcelist)-1:
                self.sourcelist[i], self.sourcelist[i+1] = self.sourcelist[i+1], self.sourcelist[i]
                self._updated_source_list()
        elif action == 'add_alternative':
            self.addSourceAlt()
        else:
            logger.warning("Invalid action link: %r (bad action %r)", link, action)

    @pyqtSlot(int, bool)
    @pyqtSlot(int)
    @pyqtSlot()
    def changeSource(self, i=0, noemit=False):
        """
        Prompt user with a file dialog and change the source at index `i`
        """

        if self._error_state:
            logger.warning("SourceListEditor's error state is on, don't call changeSource()!")

        fname = self._get_source_fname()
        if not fname:
            return
        
        self.sourcelist[i] = fname
        self._updated_source_list(noemit=noemit)
        
    @pyqtSlot(bool)
    @pyqtSlot()
    def addSourceAlt(self, noemit=False):

        if self._error_state:
            logger.warning("SourceListEditor's error state is on, don't call addSourceAlt()!")

        fname = self._get_source_fname()
        if not fname:
            return
        
        self.sourcelist.append(fname)
        self._updated_source_list(noemit=noemit)

    def _get_source_fname(self):
        fname, _filter = QFileDialog.getOpenFileName(self, 'Select BibTeX File', str(),
                                                     'BibTeX Files (*.bib);;All Files (*)')
        logger.debug("fname=%r.", fname)
        if (not fname):
            return None

        fname = sanitize_bib_rel_path(fname, ref_dir=self._ref_dir)

        return fname

    
    @pyqtSlot()
    def emitSourceListChanged(self):
        logger.debug("emitting sourceListChanged()!")
        self.sourceListChanged.emit(self.sourcelist)


    @pyqtSlot()
    def on_btnAddSource_clicked(self):
        self.requestAddSourceList.emit()

