# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2018 by Philippe Faist                                       #
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

import logging
from html import escape as htmlescape

import github

import bibolamazi.init

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .uiutils import BlockedSignals #, ContextAttributeSetter
from .qtauto.ui_githubreposelector import Ui_GithubRepoSelector

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------


class GithubRepoSelector(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_GithubRepoSelector()
        self.ui.setupUi(self)

        self.ui.stk.setCurrentWidget(self.ui.pageUsername)

        self.ui.cbxRepos.repolist = []

        self._update_gui_state()

    def getUsernameRepo(self):
        return (self.ui.txtUser.text(), self.ui.cbxRepos.currentText())

    def getFilterPackageUrl(self):
        return 'github:' + self.ui.txtUser.text() + '/' + self.ui.cbxRepos.currentText()

    @pyqtSlot(str)
    def on_txtUser_textChanged(self, txt):
        self._update_gui_state()

    @pyqtSlot()
    def on_btnBack_clicked(self):
        self.ui.stk.setCurrentWidget(self.ui.pageUsername)
        self._update_gui_state()

    @pyqtSlot()
    def on_btnNext_clicked(self):
        self.ui.stk.setCurrentWidget(self.ui.pageRepo)
        self._update_gui_state()

    @pyqtSlot(str)
    def on_cbxRepos_editTextChanged(self, text):
        self._update_gui_state()

    @pyqtSlot()
    def on_btnOk_clicked(self):
        self.accept()

    def _update_gui_state(self):
        if self.ui.stk.currentWidget() == self.ui.pageUsername:
            self.ui.stk.setCurrentWidget(self.ui.pageUsername)
            self.ui.btnBack.setVisible(False)
            self.ui.btnNext.setVisible(True)
            self.ui.btnNext.setEnabled(True if self.ui.txtUser.text() else False)
            self.ui.btnOk.setVisible(False)
        elif self.ui.stk.currentWidget() == self.ui.pageRepo:
            username = self.ui.txtUser.text()
            self.ui.lblPromptRepo.setTextFormat(Qt.RichText)
            self.ui.lblPromptRepo.setText("Repositories for <b>{}</b>".format(htmlescape(username)))
            try:
                repolist = self._get_repolist_for_user(username)
                if self.ui.cbxRepos.repolist != repolist:
                    with BlockedSignals(self.ui.cbxRepos):
                        self.ui.cbxRepos.clear()
                        for repo in repolist:
                            self.ui.cbxRepos.addItem(repo)
                        self.ui.cbxRepos.repolist = repolist
            except Exception as e:
                logger.debug("Ignoring exception ... %r", e)
                logger.exception("Ignoring exception")

            self.ui.btnBack.setVisible(True)
            self.ui.btnNext.setVisible(False)
            self.ui.btnOk.setVisible(True)
            self.ui.btnOk.setEnabled(True if self.ui.cbxRepos.currentText() else False)
            

    def _get_repolist_for_user(self, username):

        # use auth_token, if set
        from . import bibolamaziapp
        auth_token = bibolamaziapp.app_filterpackage_providers['github'].getAuthToken()

        if auth_token:
            G = github.Github(auth_token)
        else:
            G = github.Github()

        repo_list = []
        for repo in G.get_user(username).get_repos():
            repo_list.append(repo.name)

        logger.debug("Got repository list for user %r -> %r", username, repo_list)

        return repo_list

            
