#!/usr/bin/env python
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


import sys
import os
import os.path
import re
import logging
import subprocess
import datetime

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

import bibolamazi.init

# set up basic logging
from bibolamazi.core import blogger

from bibolamazi.core import bibolamazifile
from bibolamazi.core import main
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core.bibfilter import argtypes
from bibolamazi.core import version as bibolamaziversion

from . import openbibfile
from . import helpbrowser
from . import settingswidget

from .favorites import FavoriteCmdsList
from .newbibolamazifiledialog import NewBibolamazifileDialog

from .qtauto.ui_mainwidget import Ui_MainWidget


logger = logging.getLogger(__name__)



class BibolamaziApplication(QApplication):
    def __init__(self, enable_software_updates=True):
        self.main_widget = None
        
        super(BibolamaziApplication, self).__init__(sys.argv)
        
        self.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))
        self.setApplicationName('Bibolamazi')
        self.setApplicationVersion(bibolamaziversion.version_str)
        self.setOrganizationDomain('org.bibolamazi')
        self.setOrganizationName('Bibolamazi Project')

        # before main widget, so that main widget can create & connect relevant menu items
        if enable_software_updates:
            setup_software_updater()

        # create & setup main widget
        self.main_widget = MainWidget()

        self.main_widget.show()
        self.main_widget.raise_()

    def event(self, event):
        if (event.type() == QEvent.FileOpen):
            logger.info("Opening file %s", event.file())
            # request to open file
            if (self.main_widget is None):
                logger.error("ERROR: CAN'T OPEN FILE: MAIN WIDGET IS NONE!")
            else:
                self.main_widget.openFile(event.file())
            return True
            
        return super(BibolamaziApplication, self).event(event)



def find_retina_resolution():
    try:
        output = subprocess.check_output(['system_profiler', 'SPDisplaysDataType']).decode('utf-8')
    except Exception as e:
        logger.info("Couldn't check for retina display: %s", e)
        return
    logger.debug("Got display information:\n%s", output)

    mres = re.search(r'Resolution:\s*(?P<resX>\d+)\s*x\s*(?P<resY>\d+)\s*(?P<retina>.*Retina)',
                     output, flags=re.IGNORECASE)

    if not mres.group('retina'):
        # couldn't confirm it's Retina, try "Retina: Yes/No" field
        mretina = re.search(r'Retina:\s*(?P<answer>Yes|No)', output, flags=re.IGNORECASE)
        if not mretina:
            return None

    # yes, retina
    logger.debug('got res=(%d,%d)', int(mres.group('resX')), int(mres.group('resY')))

    return (int(mres.group('resX')), int(mres.group('resY')))


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.ui = Ui_MainWidget()
        self.ui.setupUi(self)

        # set up nice vector graphics on retina displays
        if sys.platform.startswith("darwin"):
            # use high-res SVG for retina displays
            retinaresolution = find_retina_resolution()
            if retinaresolution is not None:
                mydesktop = QApplication.desktop()
                # seems that myratio is not reliable (I get 1.77777..), so just use 2x
                #myratio = float(retinaresolution[0]) / mydesktop.width()
                myratio = 2
                logger.debug('myratio=%r', myratio)
                #if myratio > 1.01:
                self.mypict = QPicture()
                mypaint = QPainter(self.mypict)
                self.myicon = QIcon(":/pic/bibolamazi.svg")
                mysize = QSize(375, 150)
                mypaint.drawPixmap(QRect(QPoint(0,0),mysize), self.myicon.pixmap(myratio*mysize))
                self.ui.lblMain.setPicture(self.mypict)

        self.openbibfiles = []

        self.helpbrowser = None

        self.settingswidget = None

        self.favoriteCmdsList = FavoriteCmdsList(parent=self)
        self.favoriteCmdsList.loadFromSettings(QSettings())

        self.menubar = None
        self.shortcuts = []

        self.upd_checkenabled_action = None
        self.upd_checknow_action = None
        if (swu_interface is not None):
            self.upd_checkenabled_action = QAction("Regularly Check for Updates", self)
            self.upd_checkenabled_action.setCheckable(True)
            self.upd_checkenabled_action.setChecked(swu_interface.checkForUpdatesEnabled())
            self.upd_checkenabled_action.toggled.connect(swu_interface.setCheckForUpdatesEnabled)
            swu_interface.checkForUpdatesEnabledChanged.connect(self.upd_checkenabled_action.setChecked)
            #self.upd_checkenabled_action.toggled.connect(
            #    lambda value:
            #    QMessageBox.information(self, 'Software Updates',
            #                            'Software update checks have been turned %s.' %('on' if value else 'off'))
            #    )
            self.upd_checknow_action = QAction("Check for Updates Now", self)
            self.upd_checknow_action.triggered.connect(self.doCheckForUpdates)

        self.myactions = {}
        self.myactions['new'] = QAction("New", self)
        self.myactions['new'].triggered.connect(self.on_btnNewFile_clicked)
        self.myactions['new'].setShortcut(QKeySequence("Ctrl+N"))
        self.myactions['open'] = QAction("Open", self)
        self.myactions['open'].triggered.connect(self.on_btnOpenFile_clicked)
        self.myactions['open'].setShortcut(QKeySequence("Ctrl+O"))
        self.myactions['help'] = QAction("Open Help && Reference Browser", self)
        self.myactions['help'].triggered.connect(self.on_btnHelp_clicked)
        self.myactions['help'].setShortcut(QKeySequence("Ctrl+R"))
        self.myactions['quit'] = QAction("Quit", self)
        self.myactions['quit'].triggered.connect(self.on_btnQuit_clicked)
        self.myactions['quit'].setShortcut(QKeySequence("Ctrl+Q"))
        self.myactions['settings'] = QAction("Settings", self)
        self.myactions['settings'].triggered.connect(self.on_btnSettings_clicked)
        for a in self.myactions.values():
            self.addAction(a)

        if (sys.platform.startswith('darwin')):
            # Mac OS X
            self.menubar = QMenuBar(None)
            filemenu = self.menubar.addMenu("File")
            filemenu.addAction(self.myactions['new'])
            filemenu.addAction(self.myactions['open'])
            filemenu.addAction(self.myactions['settings'])
            if (self.upd_checkenabled_action):
                filemenu.addSeparator()
                filemenu.addAction(self.upd_checkenabled_action)
            if (self.upd_checknow_action):
                filemenu.addAction(self.upd_checknow_action)
            helpmenu = self.menubar.addMenu("Help")
            helpmenu.addAction(self.myactions['help'])
        else:
            #self.shortcuts += [
            #    (self.myactions['new'], "Ctrl+N"),
            #    (QAction("Open", self), "Ctrl+O"),
            #    (QAction("Help", self), "Ctrl+R"),
            #    (QAction("Quit", self), "Ctrl+Q"),
            #    (QAction("Settings", self), "Ctrl+P"),
            #    #
            #    # PyQt Bug: these shortcuts cause segfaults!! workaround: use QAction's instead.
            #    #
            #    #QShortcut(QKeySequence('Ctrl+N'), self, self.on_btnNewFile_clicked, self.on_btnNewFile_clicked,
            #    #          Qt.ApplicationShortcut),
            #    #QShortcut(QKeySequence('Ctrl+O'), self, self.on_btnOpenFile_clicked, self.on_btnOpenFile_clicked,
            #    #          Qt.ApplicationShortcut),
            #    #QShortcut(QKeySequence('Ctrl+R'), self, self.on_btnHelp_clicked, self.on_btnHelp_clicked,
            #    #          Qt.ApplicationShortcut),
            #    #QShortcut(QKeySequence('Ctrl+Q'), self, self.on_btnQuit_clicked, self.on_btnQuit_clicked,
            #    #          Qt.ApplicationShortcut),
            #    ]
            #if (self.upd_checkenabled_action):
            #    self.shortcuts += [
            #        #(self.upd_checkenabled_action, "Ctrl+U", None)
            #        ]
            #if (self.upd_checknow_action):
            #    self.shortcuts += [
            #        (self.upd_checknow_action, "Ctrl+U", None)
            #        ]
            # now, setup the shortcuts.
            for a in self.myactions.values():
                #print 'adding action with key %s' %(key)
                a.setShortcutContext(Qt.ApplicationShortcut)

        self.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))


    def doCheckForUpdates(self):
        if swu_interface is not None:
            ret = swu_interface.do_check_for_updates()
            if ret is None:
                pass # no checking for updates
            elif ret is False:
                # no new updates
                QMessageBox.information(self, "Software Update Check",
                                        "There are no new updates.")
            elif isinstance(ret, tuple):
                if len(ret) == 3:
                    QMessageBox.critical(self, "Error: Software Update Check",
                                         ret[2])
                    return
                # if ret[0]==True, then update installed but not restarted.
                # if ret[0]==False, then udpate exists, but not installed.
                return
                    
        
    def openFile(self, fname):
        logger.info("Opening file %r", fname)
        w = openbibfile.OpenBibFile()
        w.setFavoriteCmdsList(self.favoriteCmdsList)
        w.setOpenFile(fname)
        w.show()
        w.raise_()
        w.fileClosed.connect(self.bibFileClosed)
        self.openbibfiles.append(w)
        logger.debug("openbibfile object = %r, self.openbibfiles = %r", w, self.openbibfiles)

        w.requestHelpTopic.connect(self.openHelpTopic)


    @pyqtSlot('QString')
    def openHelpTopic(self, path):
        self.on_btnHelp_clicked()
        self.helpbrowser.openHelpTopic(path)


    @pyqtSlot()
    def on_btnOpenFile_clicked(self):
        openFileDialog = QFileDialog(self, "Open Bibolamazi File", str(),
                                     "Bibolamazi Files (*.bibolamazi.bib);;All Files (*)")

        if sys.platform.startswith('darwin'):
            # NOTE: BUG: OS X' file selection dialog won't understand the
            # .bibolamazi.bib extension. So use Qt's file dialog.
            openFileDialog.setOptions(QFileDialog.DontUseNativeDialog)
        
        openFileDialog.setDefaultSuffix("bibolamazi.bib")
        openFileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        openFileDialog.setFileMode(QFileDialog.AnyFile)
        if not openFileDialog.exec_():
            return
        
        selectedfiles = openFileDialog.selectedFiles()
        if not selectedfiles:
            return

        assert len(selectedfiles) == 1

        fname = selectedfiles[0]
        if (fname):
            self.openFile(fname)

        
    @pyqtSlot()
    def on_btnNewFile_clicked(self):

        dlg = NewBibolamazifileDialog(self)

        dlg.bibolamaziFileCreated.connect(self.openFile)

        dlg.show()
            

    @pyqtSlot()
    def on_btnHelp_clicked(self):
        if (self.helpbrowser is None):
            self.helpbrowser = helpbrowser.HelpBrowser()
        self.helpbrowser.show()
        self.helpbrowser.raise_()

    @pyqtSlot()
    def on_btnQuit_clicked(self):
        logger.info("App quit")
        self.close()


    @pyqtSlot()
    def on_btnSettings_clicked(self):
        if self.settingswidget is None:
            self.settingswidget = settingswidget.SettingsWidget(swu_interface=swu_interface,
                                                                swu_sourcefilter_devel=swu_sourcefilter_devel,
                                                                mainwin=self)
        self.settingswidget.show()
        self.settingswidget.raise_()

    @pyqtSlot()
    def bibFileClosed(self):
        sender = self.sender()
        if (not sender in self.openbibfiles):
            logger.warning("Widget sender %r of fileClosed() not in our openbibfiles list %r!!",
                           sender, self.openbibfiles)
            return
        logger.debug("file is closed (sender=%r).", sender)
        self.openbibfiles.remove(sender)

    def closeEvent(self, event):
        logger.debug("Close!!")

        # close open bib files one by one
        while len(self.openbibfiles):
            w = self.openbibfiles[0]
            ans = w.close() # this will call bibFileClosed and remove the window
                            # from the openbibfiles list
            if not ans:
                # if the widget cancels the close, then abort
                event.ignore()
                return

        if (self.helpbrowser):
            self.helpbrowser.close()

        self.favoriteCmdsList.saveToSettings(QSettings())

        super(MainWidget, self).closeEvent(event)


swu_updater = None
swu_interface = None
swu_source = None
swu_sourcefilter_devel = None


def setup_software_updater():
    if (not hasattr(sys, '_MEIPASS')):
        # not pyinstaller-packaged
        return

    global swu_updater, swu_interface, swu_source, swu_sourcefilter_devel

    import logging
    from updater4pyi import upd_core, upd_source, upd_iface, upd_log
    from updater4pyi.upd_source import relpattern, RELTYPE_BUNDLE_ARCHIVE, RELTYPE_EXE
    from updater4pyi.upd_iface_pyqt4 import UpdatePyQt4Interface

    # updater4pyi's logger will use our main logger anyway.
    #upd_log.setup_logger(logging.DEBUG)

    # DEBUG:
    #upd_iface.DEFAULT_INIT_CHECK_DELAY = datetime.timedelta(days=0, seconds=3, microseconds=0) # seconds
    #upd_iface.DEFAULT_CHECK_INTERVAL = datetime.timedelta(days=0, seconds=10, microseconds=0) # seconds

    swu_source = upd_source.UpdateGithubReleasesSource('phfaist/bibolamazi')

    swu_sourcefilter_devel = upd_source.UpdateSourceDevelopmentReleasesFilter(False)
    swu_source.add_release_filter(swu_sourcefilter_devel)

    swu_updater = upd_core.Updater(current_version=bibolamaziversion.version_str, #'0.9', ## DEBUG!!! 
                                   update_source=swu_source)

    swu_interface = UpdatePyQt4Interface(swu_updater, progname='Bibolamazi', ask_before_checking=True,
                                         parent=QApplication.instance())
    swu_interface.start()



def run_main():

    blogger.setup_simple_console_logging()

    # default level: set to root logger.  May be set externally via environment variable
    # (e.g. for debugging)
    if 'BIBOLAMAZI_LOG_LEVEL' in os.environ and os.environ['BIBOLAMAZI_LOG_LEVEL']:
        logging.getLogger().setLevel(argtypes.LogLevel(os.environ['BIBOLAMAZI_LOG_LEVEL']).levelno)
    else:
        logging.getLogger().setLevel(logging.INFO)

    # ## Seems we still need this for pyinstaller, I'm not sure why....
    #
    # load precompiled filters, if we've got any
    try:
        import bibolamazi_compiled_filter_list as pc
        filters_factory.load_precompiled_filters('bibolamazi.filters', dict([
            (fname, pc.__dict__[fname])  for fname in pc.filter_list
            ]))
    except ImportError:
        pass


    logger.debug("starting application")

    app = BibolamaziApplication()

    try:
        # load filter packages from environment ...
        main.setup_filterpackages_from_env()
        # ... and from settings.
        settingswidget.setup_filterpackages_from_settings(QSettings())
    except (filters_factory.NoSuchFilter, filters_factory.NoSuchFilterPackage, BibolamaziError):
        QMessageBox.warning(None, "Filter packages error",
                            "An error was detected in the filter packages configuration. "
                            "Please edit your settings.")
        pass

    args = app.arguments()
    _rxscript = re.compile('\.(py[co]?|exe)$', flags=re.IGNORECASE)
    for k in range(1,len(args)): # skip program name == argv[0]
        fn = str(args[k])
        if (_rxscript.search(fn)):
            # our own script, bug on windows?
            logger.debug("skipping own arg: %s", fn)
            continue
        
        logger.debug("opening arg: %s", fn)
        app.main_widget.openFile(fn)

    sys.exit(app.exec_())
    

if __name__ == '__main__':

    run_main()
