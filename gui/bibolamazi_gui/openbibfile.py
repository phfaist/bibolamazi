
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


import sys
import logging
import StringIO
import os.path
import re
import textwrap
import shlex
import logging

import bibolamazi.init
from bibolamazi.core import main as bibolamazimain
from bibolamazi.core import blogger
from bibolamazi.core.blogger import logger
from bibolamazi.core import bibolamazifile
from bibolamazi.core import butils
from bibolamazi.core.butils import BibolamaziError

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from .bibconfigsynthigh import BibolamaziConfigSyntaxHighlighter
from .favorites import FavoriteCmd, FavoritesModel, FavoritesOverBtns;
from . import filterinstanceeditor
from . import settingswidget

from .qtauto.ui_openbibfile import Ui_OpenBibFile

logger = logging.getLogger(__name__)



def bibolamazi_error_html(errortxt, bibolamaziFile, wrap_pre=True):

    def a_link(m):
        if bibolamaziFile is not None:
            return "<a href=\"action:/goto-config-line/%d\">%s</a>" %(
                bibolamaziFile.configLineNo(int(m.group('lineno'))),
                m.group()
                )
        return m.group();

    errortxt = str(Qt.escape(unicode(errortxt)))
    errortxt = re.sub(r'@:.*line\s+(?P<lineno>\d+)', a_link, errortxt)
    try:
        # if wrap_pre = (start_tag, end_tag)
        return wrap_pre[0] + errortxt + wrap_pre[1]
    except (TypeError,IndexError):
        pass
    if wrap_pre:
        # if wrap_pre = True
        return ("<pre>"+errortxt+"</pre>")
    return errortxt



class PreformattedHtml(object):
    def __init__(self, html):
        self.html = unicode(html)

    def getHtml(self):
        return self.html

    def __str__(self):
        return self.html.encode('utf-8')
    def __unicode__(self):
        return self.html

class LogToTextBrowserHandler(logging.Handler):
    def __init__(self, textEdit):
        logging.Handler.__init__(self)
        self.textEdit = textEdit

    def addtolog(self, txt, levelno=logging.INFO):
        #chfmt = QTextCharFormat()
        #if levelno == logging.ERROR or levelno == logging.CRITICAL:
        #    chfmt.setForeground(QColor(255,0,0));
        #    chfmt.setFontWeight(QFont.Bold);
        #elif levelno == logging.WARNING:
        #    chfmt.setForeground(QColor(204, 102, 0));
        #    chfmt.setFontWeight(QFont.Bold);
        #elif levelno == logging.INFO:
        #    chfmt.setForeground(QColor(0,0,0));
        #    chfmt.setFontWeight(QFont.Normal);
        #elif levelno == logging.DEBUG or levelno == logging.LONGDEBUG:
        #    chfmt.setForeground(QColor(127,127,127));
        #    chfmt.setFontWeight(QFont.Normal);
        #else:
        #    # unknown level
        #    chfmt.setForeground(QColor(127,127,127));
        #    chfmt.setFontWeight(QFont.Normal);

        try:
            html = txt.getHtml() # in case of a PreformattedHtml instance
        except AttributeError:
            html = unicode(Qt.escape(txt)) # in case of a simple plain text string

        sty = ''
        if levelno == logging.ERROR or levelno == logging.CRITICAL:
            sty = "color: #ff0000; font-weight: bold;"
        elif levelno == logging.WARNING:
            sty = "color: rgb(204,102,0); font-weight: bold;"
        elif levelno == logging.INFO:
            sty = "color: #000000; font-weight: normal;"
        elif levelno == logging.DEBUG or levelno == logging.LONGDEBUG:
            sty = "color: #7f7f7f; font-weight: normal;"
        else:
            # unknown level
            sty = "color: #7f7f7f; font-weight: normal;"

        sty += "white-space: pre;"

        cur = QTextCursor(self.textEdit.document())
        cur.movePosition(QTextCursor.End)
        #cur.setCharFormat(chfmt)
        #try:
        cur.insertHtml("<span style=\"%s\">%s\n</span>"%(sty, html))
        #except AttributeError: # txt is a normal string, not a PreformattedHtml instance
        #    cur.insertText(txt)
        self.textEdit.update()
        QApplication.instance().processEvents()

    def emit(self, record):
        self.addtolog(self.format(record), record.levelno)


class LogToTextBrowser:
    def __init__(self, textedit, bibolamaziFile, thelogger=logging.getLogger()):
        self.ch = LogToTextBrowserHandler(textedit);
        self.ch.setLevel(logging.NOTSET); # propagate all messages

        self.bibolamaziFile = bibolamaziFile

        # create formatter and add it to the handlers
        self.formatter = blogger.ConditionalFormatter('%(message)s',
                                                      DEBUG='-- %(message)s',
                                                      LONGDEBUG='  -- %(message)s',
                                                      WARNING='WARNING: %(message)s',
                                                      ERROR=self._fmt_error,
                                                      CRITICAL='CRITICAL: %(message)s');
        self.ch.setFormatter(self.formatter);

        self.logger = thelogger


    def _fmt_error(self, x):
        html = bibolamazi_error_html(
            '%(message)s' % x, bibolamaziFile=self.bibolamaziFile,
            wrap_pre=('<span style="white-space: pre">', '</span>'))
        html = "<br />".join(['ERROR: %s'%(line) for line in html.split('\n')])
        return PreformattedHtml(html=html)

    def addtolog(self, txt):
        self.ch.addtolog(txt)

    def __enter__(self):
        # add the handlers to the logger
        self.logger.addHandler(self.ch)
        self.ch.textEdit.clear()
        return self
        

    def __exit__(self, type, value, traceback):
        # clean-up
        self.logger.removeHandler(self.ch)





class ContextAttributeSetter:
    """Give a list of pairs of method and value to set.

    For example:

    >>> with ContextAttributeSetter( (object.isEnabled, object.setEnabled, False), ):
            ...

    will retreive the current state of if the object is enabled with `object.isEnabled()`, then
    will disable the object with `object.setEnabled(False)`. Upon exiting the with block, the
    state is restored to its original state with `object.setEnabled(..)`.

    """

    def __init__(self, *args):
        """Constructor. Does initializations. The \"enter\" statement is done with __enter__().

        Note: the argument are a list of 3-tuples `(get_method, set_method, set_to_value)`.
        """
        self.attribpairs = args
        self.initvals = None

    def __enter__(self):
        self.initvals = []
        for (getm, setm, v) in self.attribpairs:
            self.initvals.append(getm())
            setm(v)
            
        return self

    def __exit__(self, type, value, traceback):
        # clean-up
        for i in xrange(len(self.attribpairs)):
            (getm, setm, v) = self.attribpairs[i]
            setm(self.initvals[i])




class OpenBibFile(QWidget):

    requestHelpTopic = pyqtSignal('QString')

    fileClosed = pyqtSignal()
    

    def __init__(self):
        super(OpenBibFile, self).__init__()

        self.ui = Ui_OpenBibFile()
        self.ui.setupUi(self)

        self.resize(QSize(1200,800))
        self.ui.splitEditConfig.setSizes([100,1])

        self.ui.txtConfig.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtLog.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtBibEntries.setWordWrapMode(QTextOption.WrapAnywhere)

        font = settingswidget.get_typewriter_font(self.ui.txtConfig)
        self.ui.txtConfig.setFont(font)
        self.ui.txtLog.setFont(font)
        self.ui.txtBibEntries.setFont(font)

        self.syntHighlighter = BibolamaziConfigSyntaxHighlighter(self.ui.txtConfig)

        self._favorites_overbtn = FavoritesOverBtns(self.ui.treeFavorites)
        self._favorites_overbtn.insertCommand.connect(self._insert_new_cmd)

        self.ui.filterInstanceEditor.requestAddToFavorites.connect(self.add_favorite_cmd)
        self.ui.sourceListEditor.requestAddToFavorites.connect(self.add_favorite_cmd)
        self.ui.sourceListEditor.requestAddSourceList.connect(self.on_btnAddSourceList_clicked)

        self.bibolamaziFileName = None
        self.bibolamaziFile = None

        self.updateTimer = QTimer(self)
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        QObject.connect(self.updateTimer, SIGNAL('timeout()'), self.reloadFile)
        
        self._flag_modified_externally = False

        self.fwatcher = QFileSystemWatcher(self)
        QObject.connect(self.fwatcher, SIGNAL('fileChanged(QString)'), self.fileModifiedExternally)
        #self.delayedUpdateFileContents)

        self.shortcuts = [
            QShortcut(QKeySequence('Ctrl+W'), self, self.close, self.close),
            QShortcut(QKeySequence('Ctrl+S'), self, self.saveToFile, self.saveToFile),
            QShortcut(QKeySequence(Qt.CTRL|Qt.Key_Return), self, self.runBibolamazi, self.runBibolamazi),
            ];

        self._ignore_change_for_edittools = False
        self._needs_update_txtbibentries = False
        self._set_modified(False)

        logger.longdebug("finished OpenBibFile constructor!")

    def setFavoriteCmdsList(self, favoriteCmdsList):
        self.favoriteCmdsList = favoriteCmdsList

        self._favorites_model = FavoritesModel(favcmds=self.favoriteCmdsList, parent=self);
        self.ui.treeFavorites.setModel(self._favorites_model);
        

    def setOpenFile(self, filename):
        if (self.bibolamaziFileName):
            self.fwatcher.removePath(self.bibolamaziFileName)
            
        self.bibolamaziFileName = filename
        self.bibolamaziFile = None

        self.reloadFile()

        if (self.bibolamaziFileName):
            self.fwatcher.addPath(self.bibolamaziFileName)


    def hasUnsavedModifications(self):
        return self._modified;

    def fileName(self):
        return self.bibolamaziFileName

    # use close() to close the widget and file
    def closeEvent(self, closeEvent):
        if (self._modified):
            ans = QMessageBox.question(self, 'Save Changes',
                                       "Save changes to file `%s'?" %(self.bibolamaziFileName),
                                       QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel,
                                       QMessageBox.Save)
            if (ans == QMessageBox.Save):
                # save first (no need for updating), then proceed with close
                self.saveToFile(noupdate=True)
                
            if (ans == QMessageBox.Cancel):
                # ignore the event
                closeEvent.ignore()
                return
        
        if (self.bibolamaziFileName):
            self.fwatcher.removePath(self.bibolamaziFileName)
            self.bibolamaziFileName = None
        if (self.bibolamaziFile):
            self.bibolamaziFile = None

        self.fileClosed.emit()
        
        return super(OpenBibFile, self).closeEvent(closeEvent)


    @pyqtSlot()
    def saveToFile(self, noupdate=False):
        if (not self.bibolamaziFile):
            QMessageBox.critical(self, "No File!", "No file to save to!")
            return

        config_data = str(self.ui.txtConfig.toPlainText())

        # ignore changes caused by ourselves
        self.fwatcher.blockSignals(True)
        
        # change the config block.
        self.bibolamaziFile.setConfigData(config_data)
        self.bibolamaziFile.saveToFile()

        self._set_modified(False)

        # reload file.
        if (not noupdate):
            self.delayedUpdateFileContents()

    @pyqtSlot()
    def fileModifiedExternally(self):
        logger.debug("File modified externally!!")
        self._flag_modified_externally = True
        #self.delayedUpdateFileContents

    @pyqtSlot()
    def delayedUpdateFileContents(self):
        if (self.updateTimer.isActive()):
            self.updateTimer.stop()
        self.updateTimer.start()



    def _set_win_state(self, file_is_loaded, errormessagehtml=None, ifOkSetConfigTab=False):

        # enable/disable these GUI widgets/buttons
        
        self.ui.pageConfig.setEnabled(file_is_loaded)
        self.ui.pageBibEntries.setEnabled(file_is_loaded)
        self.ui.pageLog.setEnabled(file_is_loaded)

        self.ui.btnSave.setEnabled(file_is_loaded)
        self.ui.btnGo.setEnabled(file_is_loaded)
        

        if not file_is_loaded:
            # disabled state

            self.ui.tabs.setCurrentWidget(self.ui.pageInfo)
            self.ui.txtInfo.setText(errormessagehtml)

            with ContextAttributeSetter( (self.ui.txtConfig.signalsBlocked, self.ui.txtConfig.blockSignals, True) ):
                self.ui.txtConfig.setPlainText("")

            self.ui.lblFileName.setText("<no file loaded>")

            self.setWindowFilePath(QString())
            self.setWindowTitle("<no file loaded>")
            self.setWindowIcon(QIcon(':/pic/file.png'))

            self._modified = False

            return

        # normal, enabled state
        self.ui.lblFileName.setText(self.bibolamaziFileName)

        self.setWindowFilePath(self.bibolamaziFileName)
        self.setWindowTitle(os.path.basename(self.bibolamaziFileName))
        self.setWindowIcon(QIcon(':/pic/file.png'))

        if ifOkSetConfigTab:
            self.ui.tabs.setCurrentWidget(self.ui.pageConfig)
        self.ui.txtConfig.setFocus()


    @pyqtSlot()
    def reloadFile(self):
        logger.debug("reloading file")

        self._flag_modified_externally = False

        self._set_modified(False)

        # we may be sensitive again to external changes again
        if (self.fwatcher.signalsBlocked()):
            self.fwatcher.blockSignals(False)

        if (not self.bibolamaziFileName):
            with ContextAttributeSetter( (self.ui.btnGo.isEnabled, self.ui.btnGo.setEnabled, False) ):
                self.ui.txtInfo.setText("<h3 style=\"color: rgb(127,0,0)\">no file loaded.</h3>");
                self.ui.txtConfig.setPlainText("")
            return

        if (not self.bibolamaziFile):
            self.bibolamaziFile = bibolamazifile.BibolamaziFile()

        try:

            self.bibolamaziFile.load(self.bibolamaziFileName, to_state=bibolamazifile.BIBOLAMAZIFILE_READ)

        except butils.BibolamaziError as e:
            self.bibolamaziFile = None
            QMessageBox.critical(self, "Load Error", u"Error loading file: %s" %(unicode(e)))
            self._set_win_state(False,
                                "<h3 style=\"color: rgb(127,0,0)\">Error reading file.</h3>\n"
                                + bibolamazi_error_html(unicode(e), bibolamaziFile=self.bibolamaziFile))
            return

        self._set_win_state(True)

        with ContextAttributeSetter( (self.ui.txtConfig.signalsBlocked, self.ui.txtConfig.blockSignals, True) ):
            cursorpos = self.ui.txtConfig.textCursor().position()
            self.ui.txtConfig.setPlainText(self.bibolamaziFile.configData())
            cur = self.ui.txtConfig.textCursor()
            cur.setPosition(cursorpos)
            self.ui.txtConfig.setTextCursor(cur)

        self._needs_update_txtbibentries = True

        # now, try to further parse the config
        self._bibolamazifile_reparse()

        if self.bibolamaziFile.getLoadState() == bibolamazifile.BIBOLAMAZIFILE_PARSED:
            self._display_info()

        logger.debug("file contents updated!")

        

    def _display_info(self):

        def srcurl(s):
            if (re.match(r'^\w+:/', s)):
                # already URL
                return s;
            s = self.bibolamaziFile.resolveSourcePath(s)
            return 'file:///'+s;

        sources = []
        for srcline in self.bibolamaziFile.sourceLists():
            if (isinstance(srcline, list)):
                srclist = srcline
            else:
                srclist = [ srcline ]

            sources.append('''<div class="source">%(srcname)s: <ul>%(srclist)s</ul></div>''' % {
                'srcname': ('Source' if len(srclist) == 1 else 'Source List'), 
                'srclist': "".join(
                    ["<li><a href=\"%(sourceurl)s\">%(sourcepath)s</a></li>" % {
                        'sourcepath': Qt.escape(s),
                        'sourceurl': Qt.escape(srcurl(s)),
                        }
                     for s in srclist
                     ]
                    )
                });
                
        filters = []
        for fil in self.bibolamaziFile.filters():
            filters.append('''<div class="filter"><div class="filtertitle">Filter: <a href="helptopic:/filters/%(filtername)s">%(filtername)s</a></div><div class="filterdescription">%(filterdescription)s</div></div>''' % { 'filtername': fil.name(),
                     'filterdescription': fil.getHelpDescription(),
                    });

        thehtml = textwrap.dedent('''\
        <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">
        <html><head>
            <meta name="qrichtext" content="1" />
            <style type="text/css">
              body {
                white-space: normal;
                margin: 0px;
                padding: 0px;
              }
              .container {
                margin: 0px;
                padding-top: 20px;
              }
              h1 {
                font-weight: bold;
                font-size: 1.2em;
                color: rgb(0,127,127);
                margin: 0.5em 0px 0px;
                padding: 0px;
              }
              ul, li { margin: 0px; }
              p, li { white-space: normal }
              a { text-decoration: none; }
              .source { margin: 0.5em 0px 0px 0px; }
              .filter { margin: 0.3em 0px 0px 0px; }
              .filterdescription { font-style: italic; margin-left: 2.5em; }
            </style>
          </head><body><div class="container"><h1>Sources</h1>%(sourceshtml)s<h1>Filters</h1>%(filtershtml)s</div></body></html>''') % {
            'sourceshtml': "".join(sources),
            'filtershtml': "".join(filters)
            };

        self.ui.txtInfo.setHtml(thehtml)
        

    @pyqtSlot(int)
    def on_tabs_currentChanged(self, index):
        if (self.ui.tabs.widget(index) == self.ui.pageBibEntries):
            if (self._needs_update_txtbibentries):
                self.ui.txtBibEntries.setPlainText(self.bibolamaziFile.rawRest())


    @pyqtSlot()
    def on_btnGo_clicked(self):
        self.runBibolamazi()

    @pyqtSlot()
    def runBibolamazi(self):
        if (self._modified):
            yn = QMessageBox.question(self, "Save Changes?", "Save changes to your config?",
                                      QMessageBox.Save|QMessageBox.Cancel, QMessageBox.Save)
            if (yn == QMessageBox.Cancel):
                return

            # save our config
            self.saveToFile()
            
        with ContextAttributeSetter( (self.ui.btnGo.isEnabled, self.ui.btnGo.setEnabled, False) ):
            if (not self.bibolamaziFileName):
                QMessageBox.critical(self, "No open file", "No file selected!")
                return

            logs = None
            rootlogger = logging.getLogger()
            setloggerlevel = bibolamazimain.verbosity_logger_level(self.ui.cbxVerbosity.currentIndex())
            with ContextAttributeSetter( (lambda : rootlogger.level, rootlogger.setLevel,
                                          setloggerlevel),
                                         (self.ui.tabs.currentWidget, self.ui.tabs.setCurrentWidget,
                                          self.ui.pageLog) ):
                with LogToTextBrowser(textedit=self.ui.txtLog,
                                      bibolamaziFile=self.bibolamaziFile) as log2txtLog:
                    try:
                        # block notifications for file contents updates that we generate ourselves...
                        self.fwatcher.blockSignals(True)
                        bibolamazimain.run_bibolamazi(bibolamazifile=self.bibolamaziFileName)
                        log2txtLog.addtolog(" --> Finished successfully. <--")
                    except butils.BibolamaziError as e:
                        logger.error(unicode(e))
                        log2txtLog.addtolog(" --> Finished with errors. <--")
                        QMessageBox.warning(self, "Bibolamazi error", unicode(e))

        self.delayedUpdateFileContents()
                    


    @pyqtSlot()
    def on_btnSave_clicked(self):
        self.saveToFile()

    @pyqtSlot()
    def on_btnRefresh_clicked(self):
        if (self._modified):
            yn = QMessageBox.question(self, "Really revert?",
                                      self.tr("You are about to revert the file, but you "
                                              "have unsaved changes. Do you really want "
                                              "to abandon your changes and revert the "
                                              "file to disk?"),
                                      QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Cancel)
            if (yn != QMessageBox.Ok):
                return

        self.reloadFile()


    @pyqtSlot(QUrl)
    def on_txtInfo_anchorClicked(self, url):
        self._open_anchor(url)

    @pyqtSlot(QUrl)
    def on_txtLog_anchorClicked(self, url):
        self._open_anchor(url)

    def _open_anchor(self, url):
        if (url.scheme() == "helptopic"):
            self.requestHelpTopic.emit(url.path());
            return

        if (url.scheme() == "action"):
            m = re.match(r'/goto-config-line/(?P<lineno>\d+)', url.path())
            if m:
                self.ui.tabs.setCurrentWidget(self.ui.pageConfig)
                cur = QTextCursor(self.ui.txtConfig.document().findBlockByNumber(int(m.group('lineno'))-1))
                self.ui.txtConfig.setTextCursor(cur)
                return

            logger.warning("Unknown action: %s", str(url.toString()))
            return

        logger.debug("Opening URL %r", str(url.toString()))
        QDesktopServices.openUrl(url)
        

    @pyqtSlot(bool)
    def _set_modified(self, modif):
        self._modified = modif
        self.ui.btnSave.setEnabled(self._modified)

    @pyqtSlot()
    def on_txtConfig_textChanged(self):
        logger.debug("text changed! fwatcher signals blocked=%d", self.fwatcher.signalsBlocked())

        if self._flag_modified_externally:
            logger.debug("Modified externally!")
            
            revertbtn = None
            box = None
            if (not self._modified):
                # file was modified externally, but we have no local changes.
                box = QMessageBox(QMessageBox.Warning, "File Modified Externally",
                                  "The File was modified externally. Revert and reload it?")
                revertbtn = box.addButton("Revert", QMessageBox.AcceptRole)
                box.addButton(QMessageBox.Cancel)
                box.setDefaultButton(revertbtn)
            else:
                # file was modified externally, but we have LOCAL UNSAVED CHANGES
                box = QMessageBox(QMessageBox.Warning, "File Modified Externally",
                                  "The File was modified externally, but you have unsaved changes. "
                                  "Keep your changes and ignore the external modification, or "
                                  "revert it to version on disk?")
                revertbtn = box.addButton("Revert", QMessageBox.AcceptRole)
                box.addButton("Keep changes", QMessageBox.RejectRole)
                box.setDefaultButton(revertbtn)

            box.exec_()
            clickedbtn = box.clickedButton()
            if (clickedbtn == revertbtn):
                logger.debug("Reverting!!")
                # reload the file
                self.reloadFile()
                return

            self._flag_modified_externally = False

        if not self.bibolamaziFile:
            logger.debug("No file loaded.")
            return

        self._set_modified(True)
        logger.debug('modified!!')

        self.bibolamaziFile.setConfigData(str(self.ui.txtConfig.toPlainText()))
        self._bibolamazifile_reparse();

        self._do_update_edittools()


    def _bibolamazifile_reparse(self):
        try:
            self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)
        except BibolamaziError as e:
            # see if we can parse the error
            self.ui.txtInfo.setHtml("<p style=\"color: rgb(127,0,0)\">Parse Error in file:</p>\n"+
                                    bibolamazi_error_html(unicode(e), bibolamaziFile=self.bibolamaziFile))
            return

    @pyqtSlot()
    def on_txtConfig_cursorPositionChanged(self):
        logger.debug("cursor position changed!")
        
        self._do_update_edittools()


    @pyqtSlot()
    def on_btnAddFilter_clicked(self):
        logger.debug('add filter: clicked')

        filter_list = filterinstanceeditor.get_filter_list()

        (filtname, ok) = QInputDialog.getItem(self, "Select Filter", "Please select which filter you wish to add",
                                              filter_list);
        if (not ok):
            # cancelled
            return

        # insert new filter command
        self._insert_new_cmd('filter: %s' %(filtname))

    @pyqtSlot()
    def on_btnAddSourceList_clicked(self):
        logger.debug('add source list: clicked')

        self._insert_new_cmd('src: ""')
        # directly set the focus on the file name field
        self.ui.sourceListEditor.selectSourceAltLoc(0)
        

    def _insert_new_cmd(self, cmdtext):

        doc = self.ui.txtConfig.document()
        
        insertcur = None
        
        cmd = self._get_current_bibolamazi_cmd()
        if (cmd is None):
            insertcur = QTextCursor(doc.findBlockByNumber(self.ui.txtConfig.textCursor().block().blockNumber()))
        else:
            # insert _after_ current cmd (-> +1 for next line, -1 to correct for offset starting at 1)
            insertcur = QTextCursor(doc.findBlockByNumber(self.bibolamaziFile.configLineNo(cmd.linenoend)))

        insertcur.insertText(str(cmdtext)+'\n')
        # select inserted text without the newline
        insertcur.movePosition(QTextCursor.Left)
        insertcur.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        self.ui.txtConfig.setTextCursor(insertcur)


    def _get_current_bibolamazi_cmd(self):

        if (not self.bibolamaziFile):
            logger.warning("No bibolamazi file open")
            return

        cmds = self.bibolamaziFile.configCmds();
        if (cmds is None):
            # file is not yet parsed
            return None

        cur = self.ui.txtConfig.textCursor()
        block = cur.block()
        thisline = cur.block().blockNumber()+1

        thisline = self.bibolamaziFile.fileLineNo(thisline)

        logger.longdebug("searching for cmd... at file line=%d", thisline)
        for cmd in cmds:
            logger.longdebug("\t -- testing cmd %r", cmd)
            if cmd.lineno <= thisline and cmd.linenoend >= thisline:
                # got the current cmd
                logger.longdebug("\tGot cmd: %r", cmd)
                return cmd

        return None

    def _do_update_edittools(self):
        if self._ignore_change_for_edittools:
            return

        cmd = self._get_current_bibolamazi_cmd()
        if (cmd is None):
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageBase)
            return
        
        if (cmd.cmd == 'src'):
            thesrcs = shlex.split(cmd.text)
            self.ui.sourceListEditor.setSourceList(thesrcs, noemit=True)
            self.ui.sourceListEditor.setRefDir(self.bibolamaziFile.fdir())
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageSource)
            return

        if (cmd.cmd == "filter"):
            filtername = cmd.info['filtername']
            text = cmd.text
            if (text and text[-1] == '\n'):
                text = text[:-1]
            self.ui.filterInstanceEditor.setFilterInstanceDefinition(filtername, text,
                                                                     noemit=True)
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageFilter)
            return

        logger.warning("Unknown command: %r", cmd)
        return


    def _replace_current_cmd(self, repltext, forcecheckcmd):
        logger.debug('_replace_current_cmd(%r,%r)', repltext, forcecheckcmd)
        
        cmd = self._get_current_bibolamazi_cmd()

        if (cmd is None or cmd.cmd != forcecheckcmd):
            logger.debug("Expected to currently be in cmd %s!!", forcecheckcmd)
            return

        logger.debug('About to change cmd %s on lines=%d--%d', cmd.cmd, cmd.lineno, cmd.linenoend)

        configlineno = self.bibolamaziFile.configLineNo(cmd.lineno)
        configlinenoend = self.bibolamaziFile.configLineNo(cmd.linenoend)

        self._ignore_change_for_edittools = True
        doc = self.ui.txtConfig.document()
        cursor = QTextCursor(doc.findBlockByNumber(configlineno-1))
        endblock = (configlinenoend+1)-1
        if (endblock >= doc.blockCount()):
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        else:
            cursorend = QTextCursor(doc.findBlockByNumber(endblock))
            cursor.setPosition(cursorend.position(), QTextCursor.KeepAnchor)
        cursor.insertText(repltext)
        tcursor = QTextCursor(doc.findBlockByNumber(configlineno-1))
        self.ui.txtConfig.setTextCursor(tcursor)
        self._ignore_change_for_edittools = False

        # now, reparse the config
        self.bibolamaziFile.setConfigData(str(self.ui.txtConfig.toPlainText()))
        self._bibolamazifile_reparse()
        

    @pyqtSlot(QStringList)
    def on_sourceListEditor_sourceListChanged(self, sourcelist):

        sourcelist = [str(x) for x in list(sourcelist)]

        cmdtext = "src: " + ("\n     ".join([butils.quotearg(x) for x in sourcelist])) + "\n"

        self._replace_current_cmd(cmdtext, 'src')


    @pyqtSlot()
    def on_filterInstanceEditor_filterInstanceDefinitionChanged(self):
        filtername = self.ui.filterInstanceEditor.filterName()
        optionstring = self.ui.filterInstanceEditor.optionString()

        logger.debug('on_filterInstanceEditor_filterInstanceDefinitionChanged() '
                     'filtername=%r, optionstring=%r', filtername, optionstring)

        cmdtext = "filter: " + filtername + ' ' + optionstring + "\n"

        self._replace_current_cmd(cmdtext, 'filter')
        

    @pyqtSlot(QString)
    def on_filterInstanceEditor_filterHelpRequested(self, topic):
        self.requestHelpTopic.emit(str(topic))


    @pyqtSlot()
    def add_favorite_cmd(self):
        cmd = self._get_current_bibolamazi_cmd()

        if (cmd is None):
            logger.warning("No command to add to favorites!")
            return

        logger.debug("Adding command %s on lines %d--%d to favorites: %r", cmd.cmd, cmd.lineno, cmd.linenoend, cmd)

        cmdtext = []
        doc = self.ui.txtConfig.document();
        for n in xrange(self.bibolamaziFile.configLineNo(cmd.lineno),
                        self.bibolamaziFile.configLineNo(cmd.linenoend)+1):
            cmdtext.append(str(doc.findBlockByNumber(n-1).text()))
        cmdtext = "\n".join(cmdtext)

        self.add_favorite_cmdtext(cmdtext)

    @pyqtSlot()
    def add_favorite_selection(self):
        # ### TODO : get selection (QTextCursor::selectedText()) ... and add favorite.
        #            Also add this option in the context menu.
        pass

    @pyqtSlot(QString)
    def add_favorite_cmdtext(self, cmdtext):
        cmdtext = str(cmdtext)
        
        self.favoriteCmdsList.addFavorite(FavoriteCmd(name=cmdtext[:30], cmd=cmdtext))

        QMessageBox.information(self, "Favorite Added", "Added this command to your favorites.")
