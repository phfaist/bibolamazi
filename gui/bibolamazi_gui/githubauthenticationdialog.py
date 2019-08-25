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

import re
import logging
#from html import escape as htmlescape

#import github

import bibolamazi.init

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from .uiutils import BlockedSignals #, ContextAttributeSetter
from .qtauto.ui_githubauthenticationdialog import Ui_GithubAuthenticationDialog

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------


class GithubAuthenticationDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        self.ui = Ui_GithubAuthenticationDialog()
        self.ui.setupUi(self)

        # Button screenshots: take on hi dpi mac, scale image @ 80%, export to
        # png, note dimensions; specify 1/2 of the dimensions as image sizes
        # below so that pictures appear nice on retina displays

        self.ui.lbl.setText("""\
<html><head>
<style>
h1 { font-size: 120%; font-weight: bold; }
p { margin-bottom: 1em; }
ol, li { margin: 0px; padding: 0px; }
a { color: #4040ff; }
img { vertical-align: middle; }
</style>
<body>
<h1>Authenticate to Github</h1>

<p>Please visit <a
href="https://github.com/settings/tokens">https://github.com/settings/tokens</a>
and follow the following instructions to generate a personal access token.  This
procedure ensures that bibolamazi never sees your github password.</p>

<p>1. Click on the button <img
    src=":/pic/github_generate_new_personal_access_token.png" alt="Generate new
    token" width="128" height="29" style="vertical-align: middle; width: 128px; height: 29px;"></p>

<p>2. Give a name to the access token such as “bibolamazi access” and select the “repo” scope:</p>

<p><img src=":/pic/github_generate_new_personal_access_token_details.png" alt=""
        width="312" height="236" style="width: 312px; height: 236px;"></p>

<p>3. Scroll down and click <img src=":/pic/github_generate_new_personal_access_token_generatebtn.png"
    alt="Generate token" width="117" height="32"
    style="vertical-align: middle; width: 117px; height: 32px;"></p>

<p><b>4. Paste the access token in the field below:</b></p>

</body>
</html>""")
        
        self.ui.txtToken.textChanged.connect(self._update_gui_state)
        self._update_gui_state()

        self.adjustSize()
        self.resize(self.size() + QSize(150,80))


    def getAuthToken(self):
        return self.ui.txtToken.text().strip()

    @pyqtSlot()
    def _update_gui_state(self):

        with BlockedSignals(self.ui.txtToken):
            self.ui.txtToken.setText( self.ui.txtToken.text().strip() )

        self.ui.btns.button(QDialogButtonBox.Ok).setEnabled(
            self._is_valid_token(self.ui.txtToken.text())
        )
        

    def _is_valid_token(self, token):
        logger.debug("checking token = [...]%s", token[-4:])
        return (re.match(r'^[a-fA-F0-9]{32,}$', token if token else '') is not None)
