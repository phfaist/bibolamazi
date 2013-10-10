
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

        self.ui.txtConfig.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtLog.setWordWrapMode(QTextOption.WrapAnywhere)

        self.syntHighlighter = BibolamaziConfigSyntaxHighlighter(self.ui.txtConfig)

        self.bibolamaziFileName = None
        self.bibolamaziFile = None

        self.updateTimer = QTimer(self)
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        QObject.connect(self.updateTimer, SIGNAL('timeout()'), self.updateFileContents)

        self.watcher = QFileSystemWatcher(self)
        QObject.connect(self.watcher, SIGNAL('fileChanged(QString)'), self.delayedUpdateFileContents)

        self.shortcuts = [
            QShortcut(QKeySequence('Ctrl+W'), self, self.closeFile, self.closeFile),
            QShortcut(QKeySequence('Ctrl+S'), self, self.saveToFile, self.saveToFile),
            ];

        self._ignore_cursor_change = False

        

    def setOpenFile(self, filename):
        if (self.bibolamaziFileName):
            self.watcher.removePath(self.bibolamaziFileName)
            
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

        self.ui.tabs.setCurrentWidget(self.ui.pageInfo)
        
        if (self.bibolamaziFileName):
            self.watcher.addPath(self.bibolamaziFileName)


    @pyqtSlot()
    def closeFile(self):
        if (self.bibolamaziFileName):
            self.watcher.removePath(self.bibolamaziFileName)
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

        # change the config block.
        self.bibolamaziFile.setConfigData(config_data)
        self.bibolamaziFile.save_to_file()

        # reload file.
        self.delayedUpdateFileContents()
        


    @pyqtSlot()
    def delayedUpdateFileContents(self):
        if (self.updateTimer.isActive()):
            self.updateTimer.stop()
        self.updateTimer.start()

    @pyqtSlot()
    def updateFileContents(self):
        print "updating config section"

        if (not self.bibolamaziFile):
            self.ui.txtConfig.setPlainText("")
            return

        try:
            self.bibolamaziFile.load(self.bibolamaziFileName, to_state=bibolamazifile.BIBOLAMAZIFILE_READ)
        except BibolamaziError:
            self.ui.txtInfo.setHtml("<p style=\"color: rgb(127,0,0)\">Error reading file.</p>")
            return

        cursorpos = self.ui.txtConfig.textCursor().position()
        self.ui.txtConfig.setPlainText(self.bibolamaziFile.config_data())
        cur = self.ui.txtConfig.textCursor()
        cur.setPosition(cursorpos)
        self.ui.txtConfig.setTextCursor(cur)

        # now, try to further parse the config
        try:
            self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)
        except BibolamaziError as e:
            # see if we can parse the error
            errortxt = str(Qt.escape(unicode(e)))
            errortxt = re.sub(r'@:.*line\s+(?P<lineno>\d+)',
                              lambda m: "<a href=\"action:/goto-config-line/%d\">%s</a>" %(
                                  int(m.group('lineno')) - self.bibolamaziFile.rawstartconfigdatalineno() - 1,
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
        


    @pyqtSlot()
    def on_btnGo_clicked(self):
        with ContextAttributeSetter( (self.ui.btnGo.isEnabled, self.ui.btnGo.setEnabled, False) ):
            if (not self.bibolamaziFileName):
                QMessageBox.critical(self, "No open file", "No file selected!")
                return

            logs = None
            with LogToTextBrowser(self.ui.txtLog) as log2txtLog:
                try:
                    self.ui.tabs.setCurrentWidget(self.ui.pageLog)
                    core.main.run_bibolamazi(outputbibfile=self.bibolamaziFileName,
                                             verbosity=self.ui.cbxVerbosity.currentIndex())
                except butils.BibolamaziError as e:
                    QMessageBox.warning(self, "Bibolamazi error", unicode(e))
                    


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
                cur = self.ui.txtConfig.textCursor()
                cur.setPosition(0)
                cur.movePosition(QTextCursor.Down, QTextCursor.MoveAnchor, int(m.group('lineno')))
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
        thisline = cur.block().blockNumber()

        thisline += self.bibolamaziFile.rawstartconfigdatalineno()+1

        for cmd in cmds:
            if cmd.lineno <= thisline and cmd.linenoend >= thisline:
                # got the current cmd
                print "Got cmd: %r" %(cmd)
                return cmd

        return None
    

    @pyqtSlot()
    def on_txtConfig_cursorPositionChanged(self):
        print "cursor position changed!"
        
        if self._ignore_cursor_change:
            return
        
        cmd = self._get_current_bibolamazi_cmd()
        if (cmd is None):
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageBase)
            return
        
        if (cmd.cmd == 'src'):
            self.ui.sourceListEditor.setSourceList(shlex.split(cmd.text), True)
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageSource)
            return

        if (cmd.cmd == "filter"):
            #self.ui.filterEditor.setFilterDefinition(cmd.info['filtername'], cmd.text)
            self.ui.stackEditTools.setCurrentWidget(self.ui.toolspageFilter)
            return

        print "Unknown command: %r" %(cmd)
        return


    @pyqtSlot(QStringList)
    def on_sourceListEditor_sourceListChanged(self, sourcelist):

        sourcelist = [str(x) for x in list(sourcelist)]
        
        cmd = self._get_current_bibolamazi_cmd()

        print 'Source list changed! on lines=%d--%d, sourcelist=%r' %(cmd.lineno, cmd.linenoend, sourcelist)

        if (cmd.cmd != "src"):
            print "Not currently in source cmd!!"
            return

        def doquote(x):
            if (re.match(r'[-\w./]', x)):
                # only very sympathetic chars
                return x
            return '"' + re.sub(r'("|\\)', lambda m: '\\'+m.group(), x) + '"';

        configlineno = cmd.lineno - self.bibolamaziFile.rawstartconfigdatalineno() - 1
        configlinenoend = cmd.linenoend - self.bibolamaziFile.rawstartconfigdatalineno() - 1

        self._ignore_cursor_change = True
        doc = self.ui.txtConfig.document()
        cursor = QTextCursor(doc.findBlockByNumber(configlineno))
        cursor.movePosition(QTextCursor.Down, QTextCursor.KeepAnchor, configlinenoend - configlineno + 1)
        cursor.insertText("src: " + ("\n     ".join([doquote(x) for x in sourcelist])) + "\n")
        tcursor = QTextCursor(doc.findBlockByNumber(configlineno))
        self.ui.txtConfig.setTextCursor(tcursor)
        self._ignore_cursor_change = False
