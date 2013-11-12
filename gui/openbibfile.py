
# -*- coding: utf-8 -*-

import sys
import logging
import StringIO
import os.path
import re
import textwrap
import shlex

import core.main
from core import blogger
from core.blogger import logger
from core import bibolamazifile
from core import butils
from core.butils import BibolamaziError
import filters


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from bibconfigsynthigh import BibolamaziConfigSyntaxHighlighter


from qtauto.ui_openbibfile import Ui_OpenBibFile


class LogToTextBrowserHandler(logging.Handler):
    def __init__(self, textEdit):
        logging.Handler.__init__(self)
        self.textEdit = textEdit

    def emit(self, record):
        self.textEdit.append(self.format(record))
        self.textEdit.update()
        QApplication.instance().processEvents()


class LogToTextBrowser:
    def __init__(self, textedit, thelogger=logger):
        self.ch = LogToTextBrowserHandler(textedit);
        self.ch.setLevel(logging.NOTSET); # propagate all messages

        # create formatter and add it to the handlers
        self.formatter = blogger.ConditionalFormatter('%(message)s',
                                                      DEBUG='-- %(message)s',
                                                      LONGDEBUG='  -- %(message)s',
                                                      WARNING='WARNING: %(message)s',
                                                      ERROR='ERROR: %(message)s',
                                                      CRITICAL='CRITICAL: %(message)s');
        self.ch.setFormatter(self.formatter);

        self.logger = thelogger
        

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

    def __init__(self):
        super(OpenBibFile, self).__init__()

        self.ui = Ui_OpenBibFile()
        self.ui.setupUi(self)

        self.resize(QSize(1200,800))
        self.ui.splitEditConfig.setSizes([100,1])

        self.ui.txtConfig.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtLog.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtBibEntries.setWordWrapMode(QTextOption.WrapAnywhere)

        self.syntHighlighter = BibolamaziConfigSyntaxHighlighter(self.ui.txtConfig)

        self.bibolamaziFileName = None
        self.bibolamaziFile = None

        self.updateTimer = QTimer(self)
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        QObject.connect(self.updateTimer, SIGNAL('timeout()'), self.updateFileContents)
        
        self._flag_modified_externally = False

        self.fwatcher = QFileSystemWatcher(self)
        QObject.connect(self.fwatcher, SIGNAL('fileChanged(QString)'), self.fileModifiedExternally)
        #self.delayedUpdateFileContents)

        self.shortcuts = [
            QShortcut(QKeySequence('Ctrl+W'), self, self.closeFile, self.closeFile),
            QShortcut(QKeySequence('Ctrl+S'), self, self.saveToFile, self.saveToFile),
            ];

        self._ignore_change_for_edittools = False
        self._needs_update_txtbibentries = False
        self._set_modified(False)

        

    def setOpenFile(self, filename):
        if (self.bibolamaziFileName):
            self.fwatcher.removePath(self.bibolamaziFileName)
            
        self.bibolamaziFileName = filename
        self.bibolamaziFile = bibolamazifile.BibolamaziFile()
        try:
            self.bibolamaziFile.load(filename, to_state=bibolamazifile.BIBOLAMAZIFILE_READ)
        except butils.BibolamaziError as e:
            self.ui.pageInfo.txtInfo.setText(unicode(e))
        self.ui.lblFileName.setText(filename)
        self.updateFileContents()

        self.setWindowFilePath(filename)
        self.setWindowTitle(os.path.basename(filename))
        self.setWindowIcon(QIcon(':/pic/file.png'))

        self.ui.tabs.setCurrentWidget(self.ui.pageConfig)
        
        if (self.bibolamaziFileName):
            self.fwatcher.addPath(self.bibolamaziFileName)


    @pyqtSlot()
    def closeFile(self):
        if (self.bibolamaziFileName):
            self.fwatcher.removePath(self.bibolamaziFileName)
            self.bibolamaziFileName = None
        if (self.bibolamaziFile):
            self.bibolamaziFile = None
        self.close()


    @pyqtSlot()
    def saveToFile(self):
        if (not self.bibolamaziFile):
            QMessageBox.critical(self, "No File!", "No file to save to!")
            return

        config_data = str(self.ui.txtConfig.toPlainText())

        # ignore changes caused by ourselves
        self.fwatcher.blockSignals(True)
        
        # change the config block.
        self.bibolamaziFile.setConfigData(config_data)
        self.bibolamaziFile.save_to_file()

        self._set_modified(False)

        # reload file.
        self.delayedUpdateFileContents()
        


    @pyqtSlot()
    def fileModifiedExternally(self):
        print "File modified externally!!"
        self._flag_modified_externally = True
        #self.delayedUpdateFileContents

    @pyqtSlot()
    def delayedUpdateFileContents(self):
        if (self.updateTimer.isActive()):
            self.updateTimer.stop()
        self.updateTimer.start()

    @pyqtSlot()
    def updateFileContents(self):
        print "updating config section"

        self._flag_modified_externally = False

        self._set_modified(False)

        # we may be sensitive again to external changes again
        if (self.fwatcher.signalsBlocked()):
            self.fwatcher.blockSignals(False)

        
        if (not self.bibolamaziFile):
            with ContextAttributeSetter( (self.ui.btnGo.isEnabled, self.ui.btnGo.setEnabled, False) ):
                self.ui.txtConfig.setPlainText("")
            return

        try:
            self.bibolamaziFile.load(self.bibolamaziFileName, to_state=bibolamazifile.BIBOLAMAZIFILE_READ)
        except BibolamaziError:
            self.ui.txtInfo.setHtml("<p style=\"color: rgb(127,0,0)\">Error reading file.</p>")
            return

        with ContextAttributeSetter( (self.ui.txtConfig.signalsBlocked, self.ui.txtConfig.blockSignals, True) ):
            cursorpos = self.ui.txtConfig.textCursor().position()
            self.ui.txtConfig.setPlainText(self.bibolamaziFile.config_data())
            cur = self.ui.txtConfig.textCursor()
            cur.setPosition(cursorpos)
            self.ui.txtConfig.setTextCursor(cur)

        self._needs_update_txtbibentries = True

        # now, try to further parse the config
        try:
            self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)
        except BibolamaziError as e:
            # see if we can parse the error
            errortxt = str(Qt.escape(unicode(e)))
            errortxt = re.sub(r'@:.*line\s+(?P<lineno>\d+)',
                              lambda m: "<a href=\"action:/goto-config-line/%d\">%s</a>" %(
                                  self.bibolamaziFile.configLineNo(int(m.group('lineno'))),
                                  m.group()
                                  ),
                              errortxt)
            self.ui.txtInfo.setHtml("<p style=\"color: rgb(127,0,0)\">Parse Error in file:</p>"+
                                    "<pre>"+errortxt+"</pre>")
            return

        def srcurl(s):
            if (re.match(r'^\w+:/', s)):
                # already URL
                return s;
            if (not os.path.isabs(s)):
                s = self.bibolamaziFile.fdir() + '/' + s
            return 'file:///'+s;

        sources = []
        for srcline in self.bibolamaziFile.source_lists():
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

        print "file contents updated!"
        

    @pyqtSlot(int)
    def on_tabs_currentChanged(self, index):
        if (self.ui.tabs.widget(index) == self.ui.pageBibEntries):
            if (self._needs_update_txtbibentries):
                self.ui.txtBibEntries.setPlainText(self.bibolamaziFile.rawrest())


    @pyqtSlot()
    def on_btnGo_clicked(self):
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
            with LogToTextBrowser(self.ui.txtLog) as log2txtLog:
                try:
                    self.ui.tabs.setCurrentWidget(self.ui.pageLog)
                    # block notifications for file contents updates that we generate ourselves...
                    self.fwatcher.blockSignals(True)
                    core.main.run_bibolamazi(outputbibfile=self.bibolamaziFileName,
                                             verbosity=self.ui.cbxVerbosity.currentIndex())
                except butils.BibolamaziError as e:
                    QMessageBox.warning(self, "Bibolamazi error", unicode(e))

        self.delayedUpdateFileContents()
                    


    @pyqtSlot()
    def on_btnSave_clicked(self):
        self.saveToFile()

    @pyqtSlot()
    def on_btnRefresh_clicked(self):
        self.updateFileContents()


    @pyqtSlot(QUrl)
    def on_txtInfo_anchorClicked(self, url):
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

            print "ERROR: Unknown action: %s" %(str(url.toString()))
            return

        print "Opening URL %r" %(str(url.toString()))
        QDesktopServices.openUrl(url)
        


    def _get_current_bibolamazi_cmd(self):

        if (not self.bibolamaziFile):
            print "No bibolamazi file open"
            return

        cmds = self.bibolamaziFile.rawcmds();
        if (cmds is None):
            # file is not yet parsed
            return None

        cur = self.ui.txtConfig.textCursor()
        block = cur.block()
        thisline = cur.block().blockNumber()+1

        thisline = self.bibolamaziFile.fileLineNo(thisline)

        #print "searching for cmd... at file line=%d" %(thisline)
        for cmd in cmds:
            #print "\t -- testing cmd %r" %(cmd)
            if cmd.lineno <= thisline and cmd.linenoend >= thisline:
                # got the current cmd
                #print "\tGot cmd: %r" %(cmd)
                return cmd

        return None

    @pyqtSlot(bool)
    def _set_modified(self, modif):
        self._modified = modif
        self.ui.btnSave.setEnabled(self._modified)

    @pyqtSlot()
    def on_txtConfig_textChanged(self):
        print "text changed! fwatcher signals blocked=%d" %(self.fwatcher.signalsBlocked())

        if self._flag_modified_externally:
            print "Modified externally!"
            
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
                print "Reverting!!"
                # reload the file
                self.updateFileContents()
                return

            self._flag_modified_externally = False


        self._set_modified(True)
        print 'modified!!'

        self.bibolamaziFile.setConfigData(str(self.ui.txtConfig.toPlainText()))
        self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)

        self._do_update_edittools()

    @pyqtSlot()
    def on_txtConfig_cursorPositionChanged(self):
        print "cursor position changed!"
        
        self._do_update_edittools()


    def _do_update_edittools(self):
        if self._ignore_change_for_edittools:
            return

        cmd = self._get_current_bibolamazi_cmd()
        if (cmd is None):
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageBase)
            return
        
        if (cmd.cmd == 'src'):
            self.ui.sourceListEditor.setSourceList(shlex.split(cmd.text), noemit=True)
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

        print "Unknown command: %r" %(cmd)
        return


    def _replace_current_cmd(self, repltext, forcecheckcmd):
        print '_replace_current_cmd(%r,%r)' %(repltext, forcecheckcmd)
        
        cmd = self._get_current_bibolamazi_cmd()

        if (cmd is None or cmd.cmd != forcecheckcmd):
            print "Expected to currently be in cmd %s!!" %(forcecheckcmd)
            return

        print 'About to change cmd %s on lines=%d--%d' %(cmd.cmd, cmd.lineno, cmd.linenoend)

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
        self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)
        

    @pyqtSlot(QStringList)
    def on_sourceListEditor_sourceListChanged(self, sourcelist):

        sourcelist = [str(x) for x in list(sourcelist)]

        cmdtext = "src: " + ("\n     ".join([butils.quotearg(x) for x in sourcelist])) + "\n"

        self._replace_current_cmd(cmdtext, 'src')


    @pyqtSlot()
    def on_filterInstanceEditor_filterInstanceDefinitionChanged(self):
        filtername = self.ui.filterInstanceEditor.filterName()
        optionstring = self.ui.filterInstanceEditor.optionString()

        print 'on_filterInstanceEditor_filterInstanceDefinitionChanged() filtername=%r, optionstring=%r' %(filtername, optionstring)

        cmdtext = "filter: " + filtername + ' ' + optionstring + "\n"

        self._replace_current_cmd(cmdtext, 'filter')
        

    @pyqtSlot(QString)
    def on_filterInstanceEditor_filterHelpRequested(self, topic):
        self.requestHelpTopic.emit(str(topic))
