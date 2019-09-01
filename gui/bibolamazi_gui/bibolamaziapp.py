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


import sys
import os
import os.path
import re
import logging
import datetime

logger = logging.getLogger(__name__)

import bibolamazi.init

from bibolamazi.core import main
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core.bibfilter import pkgprovider, pkgfetcher_github
from bibolamazi.core import version as bibolamaziversion



from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

#print("loaded Qt. executable=", sys.executable, ' meipass=', sys._MEIPASS)

from . import openbibfile
from . import helpbrowser
from . import settingswidget
from . import startupwidget

from .favorites import FavoriteCmdsList
from .newbibolamazifiledialog import NewBibolamazifileDialog



class RecentFile:
    def __init__(self, fname, date):
        self.fname = fname
        self.date = date


DEFAULT_MAX_RECENT_FILES = 10


class RecentFilesList(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        self.max_recent_files = DEFAULT_MAX_RECENT_FILES
        self.files = []

    filesChanged = pyqtSignal()

    def loadFromSettings(self, settings):
        settings.beginGroup("RecentFiles")

        self.files[:] = []

        self.max_recent_files = int(settings.value("max_recent_files", DEFAULT_MAX_RECENT_FILES))
        
        siz = settings.beginReadArray("filelist")
        for i in range(siz):
            settings.setArrayIndex(i)
            fname = settings.value("fname")
            if fname is None: fname = ''
            fname = str(fname)
            date = settings.value("date")
            if date is None: date = QDate.currentDate()
            date = QDate(date).toPyDate()
            self.files.append(RecentFile(fname=fname, date=date))
        settings.endArray()

        settings.endGroup()

        self.filesChanged.emit()

    def saveToSettings(self, settings):
        settings.beginGroup("RecentFiles")

        settings.setValue("max_recent_files", int(self.max_recent_files))

        settings.beginWriteArray("filelist", len(self.files))
        for i,f in enumerate(self.files):
            settings.setArrayIndex(i)
            settings.setValue("fname", str(f.fname))
            settings.setValue("date", QDate(f.date))
        settings.endArray()

        settings.endGroup()

    def addRecentFile(self, fname):
        fp = os.path.realpath(os.path.abspath(fname))
        existing = False
        for i, rf in enumerate(self.files):
            if rf.fname == fp:
                self.files[i].date = datetime.date.today()
                existing = True
        if not existing:
            self.files.insert(0, RecentFile(fp, datetime.date.today()))
        self.files.sort(key=lambda x: x.date, reverse=True) # most recent first
        # drop old files
        if len(self.files) > self.max_recent_files:
            self.files[:] = self.files[:self.max_recent_files]
        self.filesChanged.emit()






class BibolamaziApplication(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        self.setWindowIcon(QIcon(':/pic/bibolamazi_icon.png'))
        self.setApplicationName('Bibolamazi')
        self.setApplicationVersion(bibolamaziversion.version_str)
        self.setOrganizationDomain('org.bibolamazi')
        self.setOrganizationName('Bibolamazi Project')

        if sys.platform.startswith("darwin"):
            self.setQuitOnLastWindowClosed(False)

        # a list of widgets for each open bibolamazi file
        self.openbibfiles = []

        # the help browser
        self.helpbrowser = None

        # the settings widget
        self.settingswidget = None

        # new bibolamazi file dialog
        self.newfiledialog = None

        # favorite commands
        self.favoriteCmdsList = FavoriteCmdsList(parent=self)
        self.favoriteCmdsList.loadFromSettings(QSettings())

        # recent files
        self.recentFilesList = RecentFilesList(parent=self)
        self.recentFilesList.loadFromSettings(QSettings())
        self.recentFilesMenus = []
        self.recentFilesActions = {}
        self.recentFilesList.filesChanged.connect(self.updateRecentFilesMenus)

        # load additional settings
        s = QSettings()
        # -- Ui group
        s.beginGroup("Ui")
        self.hide_startup_window_on_open_doc = \
            s.value("HideStartupWindowOnOpenDoc", sys.platform.startswith('darwin'), type=int)
        s.endGroup()

        # thread in which bibolamazi is run
        self.bibolamazi_thread = openbibfile.global_run_bibolamazi_thread_instance()

        # flag to avoid recursive calls to quit_app()
        self.is_quitting_app = False

        # application actions
        self.myactions = {}
        self.myactions['new'] = QAction("New Bibolamazi File", self)
        self.myactions['new'].triggered.connect(self.createNewFile)
        self.myactions['new'].setShortcut(QKeySequence("Ctrl+N"))
        self.myactions['open'] = QAction("Open Bibolamazi File", self)
        self.myactions['open'].triggered.connect(self.selectOpenFile)
        self.myactions['open'].setShortcut(QKeySequence("Ctrl+O"))
        self.myactions['help'] = QAction("Open Help && Reference Browser", self)
        self.myactions['help'].triggered.connect(self.openHelpBrowser)
        self.myactions['help'].setShortcut(QKeySequence("Ctrl+R"))
        self.myactions['about'] = QAction("About Bibolamazi", self)
        self.myactions['about'].triggered.connect(lambda : self.openHelpTopic('/guiabout'))
        self.myactions['quit'] = QAction("Quit", self)
        self.myactions['quit'].triggered.connect(self.quit_app)
        self.myactions['quit'].setShortcut(QKeySequence("Ctrl+Q"))
        self.myactions['settings'] = QAction("Settings", self)
        self.myactions['settings'].triggered.connect(self.openSettings)
        self.myactions['startupwindow'] = QAction("Show Start-up Window", self)
        
        self.menubar = None
        if sys.platform.startswith('darwin'):
            # Mac OS X
            self.menubar = QMenuBar(None)
            filemenu = self.menubar.addMenu("File")
            filemenu.addAction(self.myactions['new'])
            filemenu.addAction(self.myactions['open'])
            appmenurecentmenu = filemenu.addMenu("Open Recent")
            self.setRecentFilesMenu(appmenurecentmenu)
            filemenu.addAction(self.myactions['settings'])
            filemenu.addSeparator()
            filemenu.addAction(self.myactions['startupwindow'])
            helpmenu = self.menubar.addMenu("Help")
            helpmenu.addAction(self.myactions['help'])
            helpmenu.addAction(self.myactions['about'])

        # create & setup startup widget
        self.startup_widget = startupwidget.StartupWidget(bibapp=self)
        self.startup_widget.showAndRaise()
        self.myactions['startupwindow'].triggered.connect(self.startup_widget.showAndRaise)

        # update recent files menus app-wide
        self.updateRecentFilesMenus()


    recentFilesAvailable = pyqtSignal(bool)


    def openFile(self, fname):
        logger.info("Opening file %r", fname)

        fnamecanon = os.path.realpath(fname)

        logger.debug("canonical file name = %r", fnamecanon)

        for wopen in self.openbibfiles:
            if fnamecanon == wopen.fileName():
                wopen.raise_()
                logger.debug("File %r already open, raising window.", fnamecanon)
                return

        w = openbibfile.OpenBibFile()
        w.setFavoriteCmdsList(self.favoriteCmdsList)
        ok = w.setOpenFile(fname)

        if not ok:
            logger.warning("Failed to open file %s", fname)
            return

        if self.startup_widget.isVisible() and self.hide_startup_window_on_open_doc:
            # Setting designed for Mac OS X.  We show the start-up window, and
            # then we hide it once we open a file or create a new file (to avoid
            # clutter).  You can always show again the start-up window in
            # "File->Show Startup Window".
            self.startup_widget.hide()

        w.show()
        w.raise_()
        w.fileClosed.connect(self.bibFileClosed)

        self.openbibfiles.append(w)
        logger.debug("openbibfile object = %r, self.openbibfiles = %r", w, self.openbibfiles)

        w.requestHelpTopic.connect(self.openHelpTopic)

        if ok:
            self.recentFilesList.addRecentFile(fname)


    def hasOpenFiles(self):
        if self.openbibfiles:
            return True
        return False

        
    @pyqtSlot()
    def selectOpenFile(self):
        openFileDialog = QFileDialog(self.startup_widget, "Open Bibolamazi File", str(),
                                     "Bibolamazi Files (*.bibolamazi.bib);;All Files (*)")

        if sys.platform.startswith('darwin'):
            # NOTE: BUG: OS X' file selection dialog won't understand the
            # .bibolamazi.bib extension (confused by multiple dots). So use Qt's
            # file dialog.
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
        if fname:
            self.openFile(fname)

        
    def setHideStartupWindowOnOpenDoc(self, on):
        self.hide_startup_window_on_open_doc = bool(on)


    @pyqtSlot()
    def createNewFile(self):
        logger.debug("creating new bibolamazi file")

        # parentwidget = None
        # eventsender = self.sender()
        # if eventsender is not None and isinstance(eventsender, QWidget):
        #     parentwidget = eventsender

        if self.newfiledialog and self.newfiledialog.isVisible():
            self.newfiledialog.raise_()
            return

        self.newfiledialog = NewBibolamazifileDialog(parent=self.startup_widget)
        self.newfiledialog.bibolamaziFileCreated.connect(self.openFile)
        self.newfiledialog.show()
        self.newfiledialog.raise_()




    @pyqtSlot()
    def openHelpBrowser(self):
        if self.helpbrowser is None:
            self.helpbrowser = helpbrowser.HelpBrowser()
        self.helpbrowser.show()
        self.helpbrowser.raise_()

    @pyqtSlot('QString')
    def openHelpTopic(self, path):
        self.openHelpBrowser()
        self.helpbrowser.openHelpTopic(path)

    @pyqtSlot()
    def openSettings(self):
        if self.settingswidget is None:
            self.settingswidget = settingswidget.SettingsWidget(bibapp=self)
            # let the package provider/manager notify the settings widget of changes
            filters_factory.package_provider_manager.settings_widget = self.settingswidget

        self.settingswidget.show()
        self.settingswidget.raise_()



    @pyqtSlot()
    def bibFileClosed(self):
        sender = self.sender()
        if not sender in self.openbibfiles:
            logger.warning("Widget sender %r of fileClosed() not in our openbibfiles list %r!!",
                           sender, self.openbibfiles)
            return
        logger.debug("file is closed (sender=%r).", sender)
        self.openbibfiles.remove(sender)

        # on Mac OS X, if the last window was closed, then show the start-up
        # window:
        if not self.startup_widget.isVisible():
            if not len(self.openbibfiles):
                #    QTimer.singleShot(100, self.startup_widget.showAndRaise)
                self.startup_widget.showAndRaise()


    @pyqtSlot()
    def quit_app(self):
        if self.is_quitting_app:
            return
        self.is_quitting_app = True
        try:

            logger.info("App quit")

            settings = QSettings()
            self.favoriteCmdsList.saveToSettings(settings)
            self.recentFilesList.saveToSettings(settings)

            # close open bib files one by one
            for i in range(len(self.openbibfiles)):
                w = self.openbibfiles[i]
                ans = w.close() # this will call bibFileClosed and remove the window
                                # from the openbibfiles list
                if not ans:
                    # if the widget cancels the close, then abort
                    event.ignore()
                    return False

            # at this point, quit is confirmed and we shut down everything

            while self.bibolamazi_thread.busy:
                QThread.currentThread().usleep(100000) # 0.1 seconds
            self.bibolamazi_thread.doQuit()

            if self.helpbrowser:
                self.helpbrowser.close()

            self.quit()

        finally:
            self.is_quitting_app = False



    def event(self, event):
        if event.type() == QEvent.FileOpen:
            logger.info("Opening file %s", event.file())
            self.openFile(event.file())
            return True

        if event.type() == QEvent.Close:
            # Cmd-Q
            logger.debug("Intercepting Cmd-Q, quitting gracefully...")
            QTimer.singleShot(0, self.quit_app)
            event.ignore()
            return True
            
        return super().event(event)



    def setRecentFilesMenu(self, menu):
        """
        Register `menu` as being a "recent-files" menu.  The menu will be populated
        with recent files and updated whenever the recent files list changes.
        """
        self.recentFilesMenus.append(menu)


    @pyqtSlot()
    def updateRecentFilesMenus(self):

        files = self.recentFilesList.files

        for menu in self.recentFilesMenus:
            menu.clear()

        if not files:
            self.recentFilesAvailable.emit(False)
            return

        self.recentFilesAvailable.emit(True)

        # file name title to show in menu -- add some path information in case
        # file names are the same
        def fpathitems(fpath, num=3):
            p, f = os.path.split(fpath)
            if not f: return []
            if num <= 1:
                return [f]
            return fpathitems(p, num-1) + [f]
        def ftitle(fname):
            fpath, fn = os.path.split(fname)
            return fn + " (" + os.sep.join(fpathitems(fpath)) + ")"

        for rf in files:
            if rf.fname not in self.recentFilesActions:
                a = QAction(ftitle(rf.fname), self)
                a.triggered.connect(self._openRecentFileSlot)
                a.setProperty("recentFileName", rf.fname)
                self.recentFilesActions[rf.fname] = a

            for menu in self.recentFilesMenus:
                menu.addAction(self.recentFilesActions[rf.fname])

    @pyqtSlot()
    def _openRecentFileSlot(self):
        action = self.sender()
        fname = action.property("recentFileName")
        self.openFile(fname)


#
class AppPackageProviderManager(pkgprovider.PackageProviderManager):
    def __init__(self):
        super().__init__()
        settings = QSettings()
        settings.beginGroup('RemoteFilterPackages')
        self.prompted_for_remote = settings.value('PromptedForRemote', False)
        self.allow_remote = settings.value('AllowRemote', False)
        settings.endGroup()

        self.settings_widget = None

    def saveRemoteAllowedPreference(self, allow_remote):

        self.allow_remote = allow_remote

        self.prompted_for_remote = True
        settings = QSettings()
        settings.beginGroup('RemoteFilterPackages')
        settings.setValue('PromptedForRemote', True)
        settings.setValue('AllowRemote', self.allow_remote)
        settings.endGroup()
        settings.sync()

        if self.settings_widget:
            self.settings_widget.update_allow_remote_filterpackages()

        if self.allow_remote:
            logger.warning("Allowing remote filter packages for future sessions. "
                           "You can change this in the settings.")
        

    def remoteAllowed(self):
        if not self.prompted_for_remote:
            # ask for remote
            r = QMessageBox.warning(
                None,
                "Allow remote filter packages",
                "Filter packages are python scripts that can execute arbitrary code. "
                "You should only run filters from sources you trust.  Do you want to "
                "enable automatically downloading remote packages when a remote package "
                "is specified?  (You can change this later in the settings window.)",
                QMessageBox.Yes | QMessageBox.No
            )

            allow_remote = ( r == QMessageBox.Yes )

            self.saveRemoteAllowedPreference(allow_remote)

        elif not self.allow_remote:
            logger.warning("Remote filter packages have been disabled. To enable remote "
                           "filter packages, you need to enable the corresponding option "
                           "in the settings.")

        return self.allow_remote



app_filterpackage_providers = {}

def load_filterpackage_providers(app):
    settings = QSettings()

    # first, create our package provider manager.
    filters_factory.package_provider_manager = AppPackageProviderManager()

    settings.beginGroup('RemoteFilterPackages')
    github_auth_token = settings.value('GithubAuthToken', '').strip()
    settings.endGroup()

    app_filterpackage_providers['github'] = \
        pkgfetcher_github.GithubPackageProvider(github_auth_token if github_auth_token else None)

    filters_factory.package_provider_manager.registerPackageProvider(
        app_filterpackage_providers['github']
    )

def set_github_auth_token(github_auth_token):
    app_filterpackage_providers['github'].setAuthToken(github_auth_token)

    settings = QSettings()

    settings.beginGroup('RemoteFilterPackages')
    settings.setValue('GithubAuthToken', github_auth_token)
    settings.endGroup()

    settings.sync()


def run_app(argv):
    
    logger.debug("starting application")

    app = BibolamaziApplication(argv)


    # set up the filter package providers
    #
    load_filterpackage_providers(app)


    try:
        # load filter packages from environment ...
        main.setup_filterpackages_from_env()
        # ... and from settings.
        settingswidget.setup_filterpackages_from_settings(QSettings())
    except (filters_factory.NoSuchFilter, filters_factory.NoSuchFilterPackage, BibolamaziError):
        QMessageBox.warning(None, "Filter packages error",
                            "An error was detected in the filter packages configuration. "
                            "Please edit your settings.")


    args = app.arguments()
    _rxscript = re.compile('\.(py[co]?|exe)$', flags=re.IGNORECASE)
    for k in range(1,len(args)): # skip program name == argv[0]
        fn = str(args[k])
        if _rxscript.search(fn):
            # our own script, bug on windows?
            logger.debug("skipping own arg: %s", fn)
            continue
        
        logger.debug("opening arg: %s", fn)
        app.openFile(fn)


    sys.exit(app.exec_())
    
