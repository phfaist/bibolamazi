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


from html import escape as htmlescape
import sys
import os
import os.path
import re
import textwrap
import shlex
import logging
import importlib

import bibolamazi.init
from bibolamazi.core import main as bibolamazimain
from bibolamazi.core import blogger
from bibolamazi.core.blogger import logger
from bibolamazi.core import bibolamazifile
from bibolamazi.core import butils
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibfilter import factory as filterfactory

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from . import uiutils
from .uiutils import ContextAttributeSetter
from . import buttontabsmanager
from .bibconfigsynthigh import BibolamaziConfigSyntaxHighlighter
from .favorites import FavoriteCmd, FavoritesModel, FavoritesItemDelegate, FavoritesOverBtns
from . import filterinstanceeditor
from . import settingswidget
from . import helpbrowser
from . import searchwidget

from .qtauto.ui_openbibfile import Ui_OpenBibFile

logger = logging.getLogger(__name__)



def bibolamazi_error_html(errortxt, wrap_pre=True):

    def a_link(m):
        return "<a href=\"action:/goto-bibolamazi-file-line/%d\">%s</a>" %(
            int(m.group('lineno')),
            m.group()
            )

    errortxt = str(htmlescape(errortxt, quote=True))
    errortxt = re.sub(r'@:.*line\s+(?P<lineno>\d+)', a_link, errortxt)
    try:
        # if wrap_pre = (start_tag, end_tag)
        return wrap_pre[0] + errortxt + wrap_pre[1]
    except (TypeError,IndexError):
        pass
    if wrap_pre:
        # if wrap_pre = True
        return ("<pre style=\"white-space: pre-wrap\">"+errortxt+"</pre>")
    return errortxt



class PreformattedHtml:
    def __init__(self, html):
        self.html = str(html)

    def getHtml(self):
        return self.html

    def __str__(self):
        return self.html


class LogToHtmlQtSignal(QObject, logging.Handler):
    #
    # Handler to generate Qt signals from log messages.
    #
    # IMPORTANT: Additionally, this class interacts with RunBibolamaziThread to
    # do some internal event processing by hacking into the logging mechanism.
    #

    def __init__(self, parent, threadparent=None):
        super().__init__(parent)
        logging.Handler.__init__(self)

        self.threadparent = threadparent

    clearLog = pyqtSignal()
    logHtml = pyqtSignal(str)

    def doclear(self):
        self.clearLog.emit()

    def dolog(self, txt, levelno=logging.INFO):

        try:
            html = txt.getHtml() # in case of a PreformattedHtml instance
        except AttributeError:
            html = str(htmlescape(txt)) # in case of a simple plain text string

        sty = ''
        if levelno == logging.ERROR or levelno == logging.CRITICAL:
            sty = "color: #ff0000; font-weight: bold;"
        elif levelno == logging.WARNING:
            sty = "color: rgb(150,80,0); font-weight: bold;"
        elif levelno == logging.INFO:
            sty = "font-weight: normal;" # default color #"color: #000000; font-weight: normal;"
        elif levelno == logging.DEBUG or levelno == blogger.LONGDEBUG:
            sty = "color: #7f7f7f; font-weight: normal;"
        else:
            # unknown level
            sty = "color: #7f7f7f; font-weight: normal;"

        sty += "white-space: pre;"

        self.logHtml.emit("<span style=\"%s\">%s\n</span>"%(sty, html))

    def emit(self, record):
        self.dolog(self.format(record), record.levelno)

        if hasattr(self.threadparent, 'my_process_events'):
            self.threadparent.my_process_events()




class LogToGuiContextManager:
    def __init__(self, logqtsig, bibolamazi_fname, thelogger=logging.getLogger()):
        self.ch = logqtsig
        self.ch.setLevel(logging.NOTSET) # propagate all messages

        self.bibolamazi_fname = bibolamazi_fname

        # create formatter and add it to the handlers
        self.formatter = blogger.ConditionalFormatter('%(message)s',
                                                      DEBUG='-- %(message)s',
                                                      LONGDEBUG='  -- %(message)s',
                                                      WARNING='WARNING: %(message)s',
                                                      ERROR=self._fmt_error,
                                                      CRITICAL='CRITICAL: %(message)s')
        self.ch.setFormatter(self.formatter)

        self.logger = thelogger

    def _fmt_error(self, d):
        html = bibolamazi_error_html(
            '%(message)s' % d, # d is the dictionary with the record information
            wrap_pre=('<span style="white-space: pre">', '</span>')
        )
        html = "<br />".join(['ERROR: %s'%(line) for line in html.split('\n')])
        return PreformattedHtml(html=html)

    def __enter__(self):
        # add the handlers to the logger
        self.logger.addHandler(self.ch)
        self.ch.doclear()
        return self
        

    def __exit__(self, type, value, traceback):
        # clean-up
        self.logger.removeHandler(self.ch)





class RunBibolamaziThread(QThread):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("run-bibolamazi-thread")

        self._orig_except_hook = sys.excepthook
        sys.excepthook = self._py_except_hook

        self.keyboardinterrupt_requested = False

        self.busy = False # accessed directly by RunBibolamazi objects

    def getOwnRunBibolamazi(self):
        r = RunBibolamazi(self)
        r.moveToThread(self)
        return r

    @pyqtSlot()
    def doQuit(self):
        self.quit()
        self.wait()
        sys.excepthook = self._orig_except_hook

    def _py_except_hook(self, etype, evalue, tb):
        if etype is KeyboardInterrupt:
            self.keyboardinterrupt_requested = True
            return
        self._orig_except_hook(etype, evalue, tb)

    def my_process_events(self):
        if self.keyboardinterrupt_requested:
            self.keyboardinterrupt_requested = False
            raise KeyboardInterrupt

        QCoreApplication.processEvents()


global_run_bibolamazi_thread = None
def global_run_bibolamazi_thread_instance():
    global global_run_bibolamazi_thread
    if global_run_bibolamazi_thread is None:
        global_run_bibolamazi_thread = RunBibolamaziThread(QApplication.instance())
        global_run_bibolamazi_thread.start()
    return global_run_bibolamazi_thread


class RunBibolamazi(QObject):
    def __init__(self, threadparent):
        super().__init__(None) # important: no parent (for moveToThread())

        self.threadparent = threadparent

        self.logqtsig = LogToHtmlQtSignal(self, threadparent)
        self.logqtsig.clearLog.connect(self.clearLog)
        self.logqtsig.logHtml.connect(self.logHtml)

        self._busy = False


    busy = pyqtSignal(bool)
    bibolamaziDone = pyqtSignal()
    bibolamaziDoneError = pyqtSignal(str)

    clearLog = pyqtSignal()
    logHtml = pyqtSignal(str)

    def isBusy(self):
        return self._busy
    
    @pyqtSlot(str, int, list)
    def runBibolamazi(self, bibolamazifilename, verbosity_level, reload_filter_path):

        # reload_filter_path is a list of 2-tuples (fpname, fpdir)

        if self.threadparent.busy:
            logger.warning("Can't run bibolamazi twice simultaneously")
            return

        logger.debug("RunBibolamazi.runBibolamazi(): bibolamazifilename=%r, verbosity_level=%r, "
                     "reload_filter_path=%r. thread id=%r",
                     bibolamazifilename, verbosity_level, reload_filter_path,
                     QThread.currentThread().objectName())

        self._busy = True
        self.threadparent.busy = True
        self.busy.emit(True)

        try:

            rootlogger = logging.getLogger()
            loggerleveltoset = bibolamazimain.verbosity_logger_level(verbosity_level)
            with ContextAttributeSetter(
                    (lambda : rootlogger.level, rootlogger.setLevel, loggerleveltoset), ):
                with LogToGuiContextManager(logqtsig=self.logqtsig,
                                            bibolamazi_fname=bibolamazifilename) as log2sig:
                    try:
                        # TODO: we should reload all relevant packages here, not
                        # in the other method below

                        self._reload_filterpkg_modules(reload_filter_path)

                        bibolamazimain.run_bibolamazi(bibolamazifile=bibolamazifilename)

                        self.logqtsig.dolog(" --> Finished successfully. <--")
                        self.bibolamaziDone.emit()
                    except butils.BibolamaziError as e:
                        logger.error(str(e))
                        self.logqtsig.dolog(" --> Finished with errors. <--")
                        self.bibolamaziDoneError.emit(str(e))
                    except KeyboardInterrupt as e:
                        logger.error("*** interrupted ***")
                        self.logqtsig.dolog(" --> Stop: Interrupted. <--")
                        self.bibolamaziDoneError.emit("Bibolamazi interrupted")
                    except Exception as e:
                        stre = str(e)
                        logger.error(stre)
                        import traceback
                        logger.error(traceback.format_exc())
                        self.logqtsig.dolog(" --> EXCEPTION <--")
                        self.bibolamaziDoneError.emit(stre)

        finally:
            self.busy.emit(False)
            self._busy = False
            self.threadparent.busy = False


    def _reload_filterpkg_modules(self, reload_filter_path):
        #
        # reload all relevant local filter packages, in case the filter packages
        # have changed.
        #
        # reload_filter_path is a list of 2-tuples (fpname, fpdir)
        #
        allmodules = sorted(sys.modules.keys(), reverse=True) # so that "pkg.submodule" appears before "pkg"
        for pkgname, pkgpath in reload_filter_path:
            logger.debug("Inspecting user filter package `%s` to reload modules ...", pkgname)
            for modname in allmodules:
                if modname.startswith(pkgname):
                    mod = sys.modules[modname]
                    logger.debug("Reloading module `%s` (%r) in user filter package `%s`",
                                 modname, mod, pkgname)
                    origpath = sys.path
                    try:
                        sys.path = [pkgpath] + origpath
                        importlib.reload(mod)
                    finally:
                        sys.path = origpath

    #@pyqtSlot()
    #def _process_some_events(self):
    #    # this processes events for current thread (from Qt docs)
    #    QCoreApplication.processEvents()



                        

class OpenBibFile(QWidget):

    requestHelpTopic = pyqtSignal('QString')

    fileClosed = pyqtSignal()
    

    def __init__(self):
        super().__init__()

        self.ui = Ui_OpenBibFile()
        self.ui.setupUi(self)

        self.bibolamazi_thread = global_run_bibolamazi_thread_instance()

        self.run_bibolamazi = self.bibolamazi_thread.getOwnRunBibolamazi()
        self.run_bibolamazi.busy.connect(self._run_busy)
        self.run_bibolamazi.bibolamaziDone.connect(self._run_bibolamaziDone)
        self.run_bibolamazi.bibolamaziDoneError.connect(self._run_bibolamaziDoneError)
        self.run_bibolamazi.clearLog.connect(self._run_clearLog)
        self.run_bibolamazi.logHtml.connect(self._run_logHtml)

        self.requestRunBibolamazi.connect(self.run_bibolamazi.runBibolamazi)

        self.resize(QSize(1200,800))
        self.ui.splitEditConfig.setSizes([700,500])

        # connect buttons as "tabs"
        self.btabs = buttontabsmanager.ButtonTabsManager(self.ui.tabs, self)
        self.btabs.registerButton(self.ui.btnPageEditConfig, self.ui.tabPageEditFilters)
        self.btabs.registerButton(self.ui.btnPageFileInfo, self.ui.tabPageFileInfo)
        self.btabs.registerButton(self.ui.btnPageRunMessages, self.ui.tabPageRunMessages)

        # also in info page
        self.btabsinfo = buttontabsmanager.ButtonTabsManager(self.ui.stkInfo, self)
        self.btabsinfo.registerButton(self.ui.btnInfoPageHeader, self.ui.pageInfoHeader)
        self.btabsinfo.registerButton(self.ui.btnInfoPageEntries, self.ui.pageInfoEntries)

        self.ui.txtConfig.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtLog.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtBibEntries.setWordWrapMode(QTextOption.WrapAnywhere)

        p = QPalette(self.ui.stackEditTools.palette())
        c = p.color(QPalette.Active, QPalette.Window)
        p.setColor(QPalette.Window, QColor(int(c.red()*0.9), int(c.green()*0.9), int(c.blue()*0.9)))
        self.ui.stackEditTools.setPalette(p)
        self.ui.stackEditTools.setAutoFillBackground(True)

        font = settingswidget.get_typewriter_font(self.ui.txtConfig)
        self.ui.txtConfig.setFont(font)
        self.ui.txtLog.setFont(font)
        self.ui.txtBibEntries.setFont(font)

        self.searchConfigManager = searchwidget.SearchTextEditManager(
            self.ui.searchConfigWidget,
            self.ui.txtConfig
        )

        self.searchPrevBibEntriesManager = searchwidget.SearchTextEditManager(
            self.ui.searchPrevBibEntries,
            self.ui.txtBibEntries
        )

        self.syntHighlighter = BibolamaziConfigSyntaxHighlighter(self.ui.txtConfig)

        self._favorites_overbtn = FavoritesOverBtns(self.ui.treeFavorites)
        self._favorites_overbtn.insertCommand.connect(self._insert_new_cmd)

        self.ui.filterInstanceEditor.requestAddToFavorites.connect(self.add_favorite_cmd)
        self.ui.sourceListEditor.requestAddToFavorites.connect(self.add_favorite_cmd)
        self.ui.sourceListEditor.requestAddSourceList.connect(self.on_btnAddSourceList_clicked)

        self.ui.btnSelectedMultipleAddFavorite.clicked.connect(self.add_favorite_selection)

        self.bibolamaziFileName = None
        self.bibolamaziFile = None

        # to implement delayed reparsing of the current textedit contents
        self.reparseTimer = QTimer(self)
        self.reparseTimer.timeout.connect(self._reparse_textedit)
        
        # to implement delayed full reload of the file
        self.updateTimer = QTimer(self)
        self.updateTimer.timeout.connect(self.reloadFile)
        

        self._flag_modified_externally = False

        self.fwatcher = QFileSystemWatcher(self)
        self.fwatcher.fileChanged.connect(self.fileModifiedExternally)
        #self.delayedUpdateFileContents)

        self.shortcuts = [
            QShortcut(QKeySequence('Ctrl+W'), self, self.close, self.close),
            QShortcut(QKeySequence('Ctrl+S'), self, self.saveToFile, self.saveToFile),
            QShortcut(QKeySequence(Qt.CTRL|Qt.Key_Return), self, self.runBibolamazi, self.runBibolamazi),
            ]

        self._ignore_change_for_edittools = False
        self._needs_update_txtbibentries = False
        self._set_modified(False)

        logger.longdebug("finished OpenBibFile constructor!")

    def setFavoriteCmdsList(self, favoriteCmdsList):
        self.favoriteCmdsList = favoriteCmdsList

        self._favorites_model = FavoritesModel(favcmds=self.favoriteCmdsList, parent=self)
        self.ui.treeFavorites.setModel(self._favorites_model)

        self._favorites_delegate = FavoritesItemDelegate(parent=self)
        self.ui.treeFavorites.setItemDelegate(self._favorites_delegate)
        

    def setOpenFile(self, filename):
        if self.bibolamaziFileName:
            self.fwatcher.removePath(self.bibolamaziFileName)
            
        self.bibolamaziFileName = filename
        self.bibolamaziFile = None

        ok = self.reloadFile()

        if self.bibolamaziFileName:
            self.fwatcher.addPath(self.bibolamaziFileName)

        return ok


    def hasUnsavedModifications(self):
        return self._modified

    def fileName(self):
        return self.bibolamaziFileName

    # use close() to close the widget and file
    def closeEvent(self, closeEvent):

        # refuse to close if the bibolamazi thread is busy for us
        if self.run_bibolamazi.isBusy():
            logger.debug("Bibolamazi is running, can't close window")
            closeEvent.ignore()
            return

        logger.debug("closeEvent(): cleaning up.")
        
        if self._modified:
            ans = QMessageBox.question(self, 'Save Changes',
                                       "Save changes to file `%s'?" %(self.bibolamaziFileName,),
                                       QMessageBox.Save|QMessageBox.Discard|QMessageBox.Cancel,
                                       QMessageBox.Save)
            if ans == QMessageBox.Save:
                # save first (no need for updating), then proceed with close
                self.saveToFile(noupdate=True)
                
            if ans == QMessageBox.Cancel:
                # ignore the event
                closeEvent.ignore()
                return
        
        if self.bibolamaziFileName:
            self.fwatcher.removePath(self.bibolamaziFileName)
            self.bibolamaziFileName = None
        if self.bibolamaziFile:
            self.bibolamaziFile = None

        QMetaObject.invokeMethod(self, 'fileClosed', Qt.QueuedConnection)
        
        return super().closeEvent(closeEvent)


    @pyqtSlot()
    def saveToFile(self, noupdate=False):
        if not self.bibolamaziFile:
            QMessageBox.critical(self, "No File!", "No file to save to!")
            return

        config_data = str(self.ui.txtConfig.toPlainText())

        # ignore changes caused by ourselves
        self.fwatcher.blockSignals(True)
        
        # change the config block.
        self.bibolamaziFile.setConfigData(config_data)
        self.bibolamaziFile.saveRawToFile()

        self._set_modified(False)

        # reload file.
        if not noupdate:
            self.delayedUpdateFileContents()

    @pyqtSlot()
    def fileModifiedExternally(self):
        logger.debug("File modified externally!!")
        self._flag_modified_externally = True
        #self.delayedUpdateFileContents

    @pyqtSlot()
    def delayedUpdateFileContents(self):
        if self.updateTimer.isActive():
            self.updateTimer.stop()

        self.ui.txtConfig.setReadOnly(True)

        self.updateTimer.setInterval(1000)
        self.updateTimer.setSingleShot(True)
        self.updateTimer.start()



    def _set_win_state(self, file_is_loaded, errormessagehtml=None, ifOkSetConfigTab=False):

        # enable/disable these GUI widgets/buttons
        
        self.ui.tabPageEditFilters.setEnabled(file_is_loaded)
        self.ui.pageBibEntries.setEnabled(file_is_loaded)
        self.ui.tabPageRunMessages.setEnabled(file_is_loaded)

        self.ui.btnSave.setEnabled(file_is_loaded)
        self.ui.btnGo.setEnabled(file_is_loaded)
        self.ui.btnInterrupt.setVisible(False)
        

        if not file_is_loaded:
            # disabled state

            self.ui.tabs.setCurrentWidget(self.ui.tabPageRunMessages)
            self.ui.txtParseErrorMessages.setVisible(True)
            self.ui.txtParseErrorMessages.setText(errormessagehtml)

            self.ui.txtInfo.setText("<h3 style=\"color: rgb(127,0,0)\">parse error in file.</h3>")

            with ContextAttributeSetter( (self.ui.txtConfig.signalsBlocked,
                                          self.ui.txtConfig.blockSignals, True) ):
                self.ui.txtConfig.setPlainText("")

            self.ui.lblFileName.setText("<no file loaded>")

            self.setWindowFilePath(str())
            self.setWindowTitle("<no file loaded>")
            self.setWindowIcon(QIcon(':/pic/file.png'))

            self._modified = False

            return

        # normal, enabled state
        self.ui.lblFileName.setText(self.bibolamaziFileName)

        self.ui.txtParseErrorMessages.setVisible(False)

        self.setWindowFilePath(self.bibolamaziFileName)
        self.setWindowTitle(os.path.basename(self.bibolamaziFileName))
        self.setWindowIcon(QIcon(':/pic/file.png'))

        if ifOkSetConfigTab:
            self.ui.tabs.setCurrentWidget(self.ui.tabPageEditFilters)
        self.ui.txtConfig.setFocus()


    @pyqtSlot()
    def reloadFile(self):
        logger.debug("reloading file")

        self._flag_modified_externally = False

        # we may be sensitive again to external changes again
        if self.fwatcher.signalsBlocked():
            self.fwatcher.blockSignals(False)

        if not self.bibolamaziFileName:
            with ContextAttributeSetter( (self.ui.btnGo.isEnabled, self.ui.btnGo.setEnabled, False) ):
                self.ui.txtInfo.setText("<h3 style=\"color: rgb(127,0,0)\">no file loaded.</h3>")
                self.ui.txtConfig.setPlainText("")
            return False

        if not self.bibolamaziFile:
            self.bibolamaziFile = bibolamazifile.BibolamaziFile()

        try:

            self.bibolamaziFile.load(self.bibolamaziFileName, to_state=bibolamazifile.BIBOLAMAZIFILE_READ)

        except butils.BibolamaziError as e:
            self.bibolamaziFile = None
            QMessageBox.critical(self, "Load Error", u"Error loading file: %s" %(str(e)))
            self._set_win_state(False,
                                "<h3 style=\"color: rgb(127,0,0)\">Error reading file.</h3>\n"
                                + bibolamazi_error_html(str(e)))
            return False

        self._set_win_state(True)

        # all set, clear any read-only flags on the txtConfig
        self.ui.txtConfig.setReadOnly(False)

        has_cache = os.path.exists(os.path.join(self.bibolamaziFile.fdir(),
                                                self.bibolamaziFileName + '.bibolamazicache'))
        # if there is a cache file, then offer to delete it
        self._set_ui_delete_cache_btn(has_cache)

        with ContextAttributeSetter( (self.ui.txtConfig.signalsBlocked,
                                      self.ui.txtConfig.blockSignals, True) ):
            cursorpos = self.ui.txtConfig.textCursor().position()
            self.ui.txtConfig.setPlainText(self.bibolamaziFile.configData())
            cur = self.ui.txtConfig.textCursor()
            cur.setPosition(cursorpos)
            self.ui.txtConfig.setTextCursor(cur)

        # now, try to further parse the config
        self._bibolamazifile_reparse()

        self._set_modified(False)

        self._needs_update_txtbibentries = True

        if self.bibolamaziFile.getLoadState() == bibolamazifile.BIBOLAMAZIFILE_PARSED:
            self._display_header()

        logger.debug("file contents updated!")
        return True


    @pyqtSlot()
    def on_btnDeleteCache_clicked(self):
        cachefile = os.path.join(self.bibolamaziFile.fdir(),
                                 self.bibolamaziFileName + '.bibolamazicache')
        if not os.path.exists(cachefile):
            QMessageBox.warning(self, "No cache file",
                                "There is no cache file to remove (%s)"%(cachefile))
            return

        logger.debug("removing cache file %r", cachefile)
        os.remove(cachefile)

        self._set_ui_delete_cache_btn(False)
        
    def _set_ui_delete_cache_btn(self, is_on):
        if is_on:
            self.ui.btnDeleteCache.setText("Delete cache")
            self.ui.btnDeleteCache.setEnabled(True)
        else:
            self.ui.btnDeleteCache.setText("(no cache file)")
            self.ui.btnDeleteCache.setEnabled(False)
            

    def _display_header(self):

        rawheader = self.bibolamaziFile.rawHeader().strip()
        if rawheader:
            fileinfohtml = ("<h2>Raw Header</h2>\n"
                            "<p class=\"shadow\">The top section of the bibolamazi file "
                            "is ignored by bibolamazi.  Whatever bibtex entries listed here "
                            "will not be affected by bibolamazi filters and will be retained "
                            "as is at the top of the file.  These bibtex entries are seen by "
                            "latex as regular entries that have not been filtered by bibolamazi.  "
                            "This portion of the file cannot be edited here; use your favorite "
                            "text editor to edit.</p>"
                            "<pre class=\"small\">" + htmlescape(rawheader) + "</pre>")

        dark_mode = uiutils.is_dark_mode(self)

        thehtml = textwrap.dedent('''\
        <!DOCTYPE HTML>
        <html>
          <head>
            <style type="text/css">
              %(basecss)s
              .source { margin: 0.5em 0px 0px 0px; }
              .filter { margin: 0.3em 0px 0px 0px; }
              .filterdescription { font-style: italic; margin-left: 2.5em; }
            </style>
          </head>
          <body>
            %(content)s
          </body>
        </html>''') % {
            'basecss': helpbrowser.getCssHelpStyle(dark_mode=dark_mode),
            'content': helpbrowser.wrapInHtmlContentContainer(fileinfohtml, width=800)
        }
        self.ui.txtInfo.setHtml(thehtml)
        

    @pyqtSlot(bool)
    def on_btnInfoPageEntries_toggled(self, on):
        logger.debug("on_btnInfoPageEntries_toggled(%r)", on)
        if on: # self.ui.stkInfo.widget(index) is self.ui.pageInfoEntries:
            logger.debug("redisplaying bib entries")
            if self._needs_update_txtbibentries:
                self.ui.txtBibEntries.setPlainText(self.bibolamaziFile.rawRest())

    @pyqtSlot(bool)
    def on_btnPageFileInfo_toggled(self, on):
        logger.debug("on_btnPageFileInfo_toggled(%r)", on)
        if on and self.ui.btnInfoPageEntries.isChecked():
            logger.debug("redisplaying bib entries")
            if self._needs_update_txtbibentries:
                self.ui.txtBibEntries.setPlainText(self.bibolamaziFile.rawRest())


    @pyqtSlot()
    def on_btnGo_clicked(self):
        self.ui.txtConfig.setReadOnly(True) # enter read-only state because
                                            # otherwise changes would get
                                            # overwritten right away
        self.runBibolamazi()

    @pyqtSlot()
    def on_btnInterrupt_clicked(self):
        self.ui.btnInterrupt.setEnabled(False) # not twice in a row
        import signal

        sig = signal.SIGINT
        if sys.platform.startswith('win'):
            logger.warning("Interrupt does not work on Windows (not implemented).")
            return
            # doesn't work????!?
            #logger.debug("Sending Ctrl+C ...")
            #sig = signal.CTRL_C_EVENT
            
        os.kill(os.getpid(), sig)


    requestRunBibolamazi = pyqtSignal(str, int, list)
    
    @pyqtSlot(bool)
    def _run_busy(self, busy):

        # block notifications for file contents updates that we generate ourselves...
        self.fwatcher.blockSignals(busy)

        if sys.platform.startswith('win'):
            self.ui.btnGo.setEnabled(not busy)
            self.ui.btnInterrupt.setVisible(False)
        else:
            self.ui.btnInterrupt.setVisible(busy)
            self.ui.btnInterrupt.setEnabled(busy)
            self.ui.btnGo.setVisible(not busy)

        if busy:
            self._busy_before_curtab = self.ui.tabs.currentWidget()
            self.ui.tabs.setCurrentWidget(self.ui.tabPageRunMessages)


    @pyqtSlot()
    def _run_bibolamaziDone(self):
        # if we're done with success, go back to previous tab
        if self._busy_before_curtab is not None:
            self.ui.tabs.setCurrentWidget(self._busy_before_curtab)
            self._busy_before_curtab = None
        self.delayedUpdateFileContents()

    @pyqtSlot(str)
    def _run_bibolamaziDoneError(self, errstr):
        QMessageBox.warning(self, "Bibolamazi error", errstr)
        self._busy_before_curtab = None
        self.delayedUpdateFileContents()

    @pyqtSlot()
    def _run_clearLog(self):
        self.ui.txtLog.clear()

    @pyqtSlot(str)
    def _run_logHtml(self, html):
        cur = QTextCursor(self.ui.txtLog.document())
        cur.movePosition(QTextCursor.End)
        cur.insertHtml(html)


    @pyqtSlot()
    def runBibolamazi(self):
        if self._modified:
            yn = QMessageBox.question(self, "Save Changes?", "Save changes to your config?",
                                      QMessageBox.Save|QMessageBox.Cancel, QMessageBox.Save)
            if yn == QMessageBox.Cancel:
                return

            # save our config
            self.saveToFile()
            
        if not self.bibolamaziFileName:
            QMessageBox.critical(self, "No open file", "No file selected!")
            return

        if not self.bibolamaziFile:
            QMessageBox.critical(self, "No open file", "No file is open!")
            return

        verbosity_level = self.ui.cbxVerbosity.currentIndex()

        self.ui.txtParseErrorMessages.setVisible(False)

        reload_filter_path = list(self.bibolamaziFile.filterPath().items())

        self.requestRunBibolamazi.emit(self.bibolamaziFileName, verbosity_level,
                                       reload_filter_path)


    @pyqtSlot(int)
    def gotoConfigLineNo(self, configlineno):
        self.ui.tabs.setCurrentWidget(self.ui.tabPageEditFilters)
        cur = QTextCursor(self.ui.txtConfig.document().findBlockByNumber(configlineno-1))
        self.ui.txtConfig.setTextCursor(cur)


    @pyqtSlot()
    def on_btnSave_clicked(self):
        self.saveToFile()

    @pyqtSlot()
    def on_btnRefresh_clicked(self):
        if self._modified:
            yn = QMessageBox.question(self, "Really revert?",
                                      self.tr("You are about to revert the file, but you "
                                              "have unsaved changes. Do you really want "
                                              "to abandon your changes and revert the "
                                              "file to disk?"),
                                      QMessageBox.Ok|QMessageBox.Cancel, QMessageBox.Cancel)
            if yn != QMessageBox.Ok:
                return

        self.reloadFile()


    @pyqtSlot(QUrl)
    def on_txtInfo_anchorClicked(self, url):
        self._open_anchor(url)

    @pyqtSlot(QUrl)
    def on_txtParseErrorMessages_anchorClicked(self, url):
        self._open_anchor(url)

    @pyqtSlot(QUrl)
    def on_txtLog_anchorClicked(self, url):
        self._open_anchor(url)

    def _open_anchor(self, url):
        logger.debug("Link clicked: %r", url.toString())

        if url.scheme() == "helptopic":
            self.requestHelpTopic.emit(url.path())
            return

        if url.scheme() == "action":
            m = re.match(r'/goto-config-line/(?P<lineno>\d+)', url.path())
            if m:
                self.gotoConfigLineNo(int(m.group('lineno')))
                return

            m = re.match(r'/goto-bibolamazi-file-line/(?P<lineno>\d+)', url.path())
            if m:
                if (self.bibolamaziFile is None or
                    self.bibolamaziFile.getLoadState() < bibolamazifile.BIBOLAMAZIFILE_READ):
                    logger.warning("No bibolamazifile open!")
                    return
                configlineno = self.bibolamaziFile.configLineNo(int(m.group('lineno')))
                self.gotoConfigLineNo(configlineno)
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
            if not self._modified:
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
            if clickedbtn == revertbtn:
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

        # set a short time-out to reparse the file. This is to avoid reparsing
        # too often, especially when doing
        # computationally/transactionally-intensive changes such as changing the
        # argument of a 'package:' directive with a remote location.
        self._delayed_reparse_textedit()


    @pyqtSlot()
    def _delayed_reparse_textedit(self):
        if self.reparseTimer.isActive():
            self.reparseTimer.stop()

        self.reparseTimer.setInterval(500)
        self.reparseTimer.setSingleShot(True)
        self.reparseTimer.start()

    @pyqtSlot()
    def _reparse_textedit(self):
        self._bibolamazifile_reparse()
        self._do_update_edittools()


    def _bibolamazifile_reparse(self):
        try:
            self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)
        except BibolamaziError as e:
            # see if we can parse the error
            self.ui.txtParseErrorMessages.setVisible(True)
            self.ui.txtParseErrorMessages.setHtml(
                "<p style=\"color: rgb(127,0,0)\">Parse Error in file:</p>\n"+
                bibolamazi_error_html(str(e)))
            # self.ui.txtInfo.setHtml("<p style=\"color: rgb(180,0,0)\">Parse error in file&mdash;"
            #                         "check \"Run messages\" tab.</p>")
            return
        self.ui.txtParseErrorMessages.setVisible(False)

    @pyqtSlot()
    def on_txtConfig_cursorPositionChanged(self):
        logger.debug("cursor position changed!")
        
        self._do_update_edittools()


    @pyqtSlot()
    def on_btnAddFilter_clicked(self):
        logger.debug('add filter: clicked')

        filterpath = filterfactory.filterpath
        if self.bibolamaziFile.getLoadState() == bibolamazifile.BIBOLAMAZIFILE_PARSED:
            filterpath = self.bibolamaziFile.fullFilterPath()

        filter_list = filterinstanceeditor.get_filter_list(filterpath)

        (filtname, ok) = QInputDialog.getItem(self, "Select Filter",
                                              "Please select which filter you wish to add",
                                              filter_list)
        if not ok:
            # cancelled
            return

        # insert new filter command
        self._insert_new_cmd('filter: %s' %(filtname))

    @pyqtSlot()
    def on_btnAddSourceList_clicked(self):
        logger.debug('add source list: clicked')

        self._insert_new_cmd('src: ""')
        # directly set the focus on the file name field
        self.ui.sourceListEditor.changeSource()
        

    def _insert_new_cmd(self, cmdtext):

        doc = self.ui.txtConfig.document()
        
        insertcur = None
        
        cmd = self._get_current_bibolamazi_cmd()
        if cmd is None:
            insertcur = QTextCursor(doc.findBlockByNumber(self.ui.txtConfig.textCursor().block().blockNumber()))
        else:
            # insert _after_ current cmd (-> +1 for next line, -1 to correct for offset starting at 1)
            insertcur = QTextCursor(doc.findBlockByNumber(self.bibolamaziFile.configLineNo(cmd.linenoend)))

        cmdtext = str(cmdtext)

        insertcur.insertText('\n' + cmdtext+'\n\n')
        # select inserted text without the newline
        #insertcur.movePosition(QTextCursor.Left)
        insertcur.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(cmdtext)+1)
        #insertcur.movePosition(QTextCursor.StartOfBlock, QTextCursor.KeepAnchor)
        self.ui.txtConfig.setTextCursor(insertcur)


    def _get_current_bibolamazi_cmd(self):

        if not self.bibolamaziFile:
            logger.warning("No bibolamazi file open")
            return

        cmds = self.bibolamaziFile.configCmds()
        if cmds is None:
            # file is not yet parsed
            return None

        cur = self.ui.txtConfig.textCursor()
        block = cur.block()
        thisline = block.blockNumber()+1

        thisline = self.bibolamaziFile.fileLineNo(thisline)

        logger.longdebug("searching for cmd... at file line=%d", thisline)
        for cmd in cmds:
            logger.longdebug("\t -- testing cmd %r", cmd)
            if cmd.lineno <= thisline and cmd.linenoend >= thisline:
                # got the current cmd
                logger.longdebug("\tGot cmd: %r", cmd)
                return cmd

        return None

    def _get_current_bibolamazi_cmdlist(self):

        if not self.bibolamaziFile:
            logger.warning("No bibolamazi file open")
            return

        cmds = self.bibolamaziFile.configCmds()
        if cmds is None:
            # file is not yet parsed
            return None

        cur = self.ui.txtConfig.textCursor()
        block = cur.block()
        thisline = block.blockNumber()+1
        thisline = self.bibolamaziFile.fileLineNo(thisline)

        if cur.hasSelection():
            cur2 = QTextCursor(cur)
            cur2.setPosition(cur.anchor())
            otherline = cur2.block().blockNumber()+1
            otherline = self.bibolamaziFile.fileLineNo(otherline)
        else:
            otherline = thisline

        minline = min(thisline, otherline)
        maxline = max(thisline, otherline)

        logger.longdebug("searching for cmds between lines %d and %d", minline, maxline)
        cmdlist = []
        for cmd in cmds:
            logger.longdebug("\t -- testing cmd %r", cmd)
            if cmd.lineno <= maxline and cmd.linenoend >= minline:
                # got the current cmd
                logger.longdebug("\tGot cmd: %r", cmd)
                cmdlist.append(cmd)

        return cmdlist


    def _do_update_edittools(self):
        if self._ignore_change_for_edittools:
            return

        cmdlist = self._get_current_bibolamazi_cmdlist()
        if not cmdlist: # None, or empty list
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageBase)
            return

        if len(cmdlist) > 1:
            # several commands selected
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageSelectedMultiple)
            return

        # single command selected
        cmd = cmdlist[0]
        
        if cmd.cmd == "src":
            try:
                thesrcs = shlex.split(cmd.text)
            except ValueError as e:
                logger.debug("Invalid source list specification, syntax error: %s", str(e))
                self.ui.sourceListEditor.dispSourceListError(str(e))
                return
            self.ui.sourceListEditor.setSourceList(thesrcs, noemit=True)
            self.ui.sourceListEditor.setRefDir(self.bibolamaziFile.fdir())
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageSource)
            return

        if cmd.cmd == "package":
            try:
                self.ui.filterPackagePathEditor.setFilterPackageInfo(cmd.text.strip())
                self.ui.filterPackagePathEditor.setRefDir(self.bibolamaziFile.fdir())
            except BibolamaziError as e:
                self.ui.filterPackagePathEditor.setFilterPackageError(str(e))
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspagePackage)
            return

        if cmd.cmd == "filter":
            filtername = cmd.info['filtername']
            text = cmd.text
            if text and text[-1] == '\n':
                text = text[:-1]
            self.ui.filterInstanceEditor.setFilterPath(self.bibolamaziFile.fullFilterPath())
            self.ui.filterInstanceEditor.setFilterInstanceDefinition(filtername, text, noemit=True)
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageFilter)
            return

        logger.warning("Unknown command: %r", cmd)
        return


    def _replace_current_cmd(self, repltext, forcecheckcmd):
        logger.debug('_replace_current_cmd(%r,%r)', repltext, forcecheckcmd)
        
        cmd = self._get_current_bibolamazi_cmd()

        if cmd is None or cmd.cmd != forcecheckcmd:
            logger.debug("Expected to currently be in cmd %s!!", forcecheckcmd)
            return

        logger.debug('About to change cmd %s on lines=%d--%d', cmd.cmd, cmd.lineno, cmd.linenoend)

        configlineno = self.bibolamaziFile.configLineNo(cmd.lineno)
        configlinenoend = self.bibolamaziFile.configLineNo(cmd.linenoend)

        self._ignore_change_for_edittools = True
        doc = self.ui.txtConfig.document()
        cursor = QTextCursor(doc.findBlockByNumber(configlineno-1))
        endblock = (configlinenoend+1)-1
        if endblock >= doc.blockCount():
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
        

    @pyqtSlot('QStringList')
    def on_sourceListEditor_sourceListChanged(self, sourcelist):

        sourcelist = [str(x) for x in list(sourcelist)]

        cmdtext = "src: " + ("\n     ".join([butils.quotearg(x) for x in sourcelist])) + "\n"

        self._replace_current_cmd(cmdtext, "src")


    @pyqtSlot(str)
    def on_filterPackagePathEditor_filterPackagePathChanged(self, fpath):

        self._replace_current_cmd("package: " + fpath + "\n", "package")


    @pyqtSlot()
    def on_filterInstanceEditor_filterInstanceDefinitionChanged(self):
        filtername = self.ui.filterInstanceEditor.filterName()
        optionstring = self.ui.filterInstanceEditor.optionString()
        errorstring = self.ui.filterInstanceEditor.errorString()

        logger.debug('on_filterInstanceEditor_filterInstanceDefinitionChanged() '
                     'filtername=%r, optionstring=%r, errorstring=%r',
                     filtername, optionstring, errorstring)

        if errorstring is not None:
            return

        cmdtext = "filter: " + filtername + ' ' + optionstring + "\n"

        self._replace_current_cmd(cmdtext, "filter")
        

    @pyqtSlot('QString')
    def on_filterInstanceEditor_filterHelpRequested(self, topic):
        self.requestHelpTopic.emit(str(topic))


    @pyqtSlot()
    def add_favorite_cmd(self):
        cmd = self._get_current_bibolamazi_cmd()

        if cmd is None:
            logger.warning("No command to add to favorites!")
            return

        logger.debug("Adding command %s on lines %d--%d to favorites: %r",
                     cmd.cmd, cmd.lineno, cmd.linenoend, cmd)

        cmdtext = []
        doc = self.ui.txtConfig.document()
        for n in range(self.bibolamaziFile.configLineNo(cmd.lineno),
                       self.bibolamaziFile.configLineNo(cmd.linenoend)+1):
            cmdtext.append(str(doc.findBlockByNumber(n-1).text()))
        cmdtext = "\n".join(cmdtext)

        self.add_favorite_cmdtext(cmdtext)

    @pyqtSlot()
    def add_favorite_selection(self):
        selected_text = self.ui.txtConfig.textCursor().selectedText()

        logger.debug("Selected text: %r", selected_text)
        self.add_favorite_cmdtext(selected_text)

    @pyqtSlot(str)
    def add_favorite_cmdtext(self, cmdtext):
        cmdtext = str(cmdtext)

        shorttext = cmdtext
        if len(shorttext) > 27:
            shorttext = shorttext[:30] + '...'

        self.favoriteCmdsList.addFavorite(FavoriteCmd(name=shorttext, cmd=cmdtext))

        QMessageBox.information(self, "Favorite Added", "Added this command to your favorites.")
