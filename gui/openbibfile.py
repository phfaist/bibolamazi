
# -*- coding: utf-8 -*-

import sys
import logging
import StringIO
import os.path
import re
import textwrap

import core.main
from core import blogger
from core.blogger import logger
from core import bibolamazifile
from core import butils
from core.butils import BibolamaziError


from PyQt4.QtCore import *
from PyQt4.QtGui import *

import bibconfigsynthigh


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
    def __init__(self, obj, **kwargs):
        self.attrib = kwargs
        self.obj = obj
        self.initvals = None

    def __enter__(self):
        self.initvals = {}
        for k,v in self.attrib.iteritems():
            self.initvals[k] = getattr(self.obj, k)
            setattr(self.obj, k, v)
            
        return self

    def __exit__(self, type, value, traceback):
        # clean-up
        for (k,v) in self.initvals.iteritems():
            setattr(self.obj, k, v)




class OpenBibFile(QWidget):

    requestHelpTopic = pyqtSignal('QString')

    def __init__(self):
        super(OpenBibFile, self).__init__()

        self.ui = Ui_OpenBibFile()
        self.ui.setupUi(self)

        self.ui.txtConfig.setWordWrapMode(QTextOption.WrapAnywhere)
        self.ui.txtLog.setWordWrapMode(QTextOption.WrapAnywhere)

        self.syntHighlighter = bibconfigsynthigh.BibolamaziConfigSyntaxHighlighter(self.ui.txtConfig)

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
        
        self.ui.txtConfig.setPlainText(self.bibolamaziFile.config_data())

        # now, try to further parse the config
        try:
            self.bibolamaziFile.load(to_state=bibolamazifile.BIBOLAMAZIFILE_PARSED)
        except BibolamaziError as e:
            self.ui.txtInfo.setHtml("<p style=\"color: rgb(127,0,0)\">Parse Error in file:</p>"+
                                    "<pre>"+Qt.escape(unicode(e))+"</pre>")
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

            sources.append('''<div class="source">%(srcname)s: %(srclist)s</div>''' % {
                'srcname': ('Source' if len(srclist) == 1 else 'Source List'), 
                'srclist': ", ".join(
                    ["<a href=\"%(sourceurl)s\">%(sourcepath)s</a>" % {
                        'sourcepath': s,
                        'sourceurl': srcurl(s),
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
              p, li { white-space: normal }
              a { text-decoration: none; }
              .source { margin: 0.2em 0px 0px 0px; }
              .filter { margin: 0.2em 0px 0px 0px; }
              .filterdescription { font-style: italic; margin-left: 2.5em; }
            </style>
          </head><body><div class="container"><h1>Sources</h1>%(sourceshtml)s<h1>Filters</h1>%(filtershtml)s</div></body></html>''') % {
            'sourceshtml': "".join(sources),
            'filtershtml': "".join(filters)
            };

        self.ui.txtInfo.setHtml(thehtml)
        


    @pyqtSlot()
    def on_btnGo_clicked(self):
        with ContextAttributeSetter(self.ui.btnGo, setEnabled=False):
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

        print "Opening URL %r" %(str(url.toString()))
        QDesktopServices.openUrl(url)
        
