
# -*- coding: utf-8 -*-

import sys
import logging
import StringIO


import core.main
from core import blogger
from core.blogger import logger
from core import bibfilterfile
from core import butils


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qtauto.ui_openbibfile import Ui_OpenBibFile



class LogOneRun:
    def __init__(self, thelogger=logger, stream=None):
        if (stream is None):
            stream = StringIO.StringIO()
        self.stream = stream
        self.ch = logging.StreamHandler(self.stream);
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

    def getlog(self):
        # this assumes that self.stream is a StringIO. If not, it will explode.
        return self.stream.getvalue()


    def __enter__(self):
        # add the handlers to the logger
        self.logger.addHandler(self.ch)
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
    def __init__(self):
        super(OpenBibFile, self).__init__()

        self.ui = Ui_OpenBibFile()
        self.ui.setupUi(self)

        QObject.connect(self.ui.btnRefresh, SIGNAL('clicked()'), self.updateConfigSection)

        self.bibolamaziFile = None

        self.updateTimer = QTimer(self)
        self.updateTimer.setInterval(500)
        self.updateTimer.setSingleShot(True)
        QObject.connect(self.updateTimer, SIGNAL('timeout()'), self.updateConfigSection)

        self.watcher = QFileSystemWatcher(self)
        QObject.connect(self.watcher, SIGNAL('fileChanged(QString)'), self.delayedUpdateConfigSection)

        

    def setOpenFile(self, filename):
        if (self.bibolamaziFile):
            self.watcher.removePath(self.bibolamaziFile)
            
        self.bibolamaziFile = filename
        self.ui.lblFileName.setText(filename)
        self.updateConfigSection()

        self.setWindowFilePath(filename)
        self.setWindowTitle(filename)
        self.setWindowIcon(QIcon(':/pic/file.png'))

        if (self.bibolamaziFile):
            self.watcher.addPath(self.bibolamaziFile)

    @pyqtSlot()
    def delayedUpdateConfigSection(self):
        if (self.updateTimer.isActive()):
            self.updateTimer.stop()
        self.updateTimer.start()

    @pyqtSlot()
    def updateConfigSection(self):
        print "updating config section"

        if (not self.bibolamaziFile):
            self.ui.txtConfig.setText("")
            return
        
        try:
            bf = bibfilterfile.BibFilterFile(self.bibolamaziFile)
        except butils.BibolamaziError:
            self.ui.txtConfig.setText("<span style=\"color:rgb(127,0,0)\">parse error in config file.</span>")
            return
        
        self.ui.txtConfig.setText(bf.rawconfig())


    @pyqtSlot()
    def on_btnGo_clicked(self):
        with ContextAttributeSetter(self.ui.btnGo, setEnabled=False):
            if (not self.bibolamaziFile):
                QMessageBox.critical(self, "No open file", "No file selected!")
                return

            logs = None
            with LogOneRun() as onerunlogger:
                try:
                    core.main.run_bibolamazi(outputbibfile=self.bibolamaziFile,
                                             verbosity=self.ui.cbxVerbosity.currentIndex())
                except butils.BibolamaziError as e:
                    QMessageBox.warning(self, "Bibolamazi error", unicode(e))
                    
                logs = onerunlogger.getlog()
                self.ui.tabs.setCurrentWidget(self.ui.pageLog)

            self.ui.txtLog.setText(logs)

