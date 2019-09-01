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


import re
import sys
import logging
from html import escape as htmlescape

from urllib.parse import urlsplit

import bibolamazi.init
from bibolamazi.core.blogger import logger
from bibolamazi.core import helppages

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.Qt import QT_VERSION_STR

from . import uiutils
from . import searchwidget

from .qtauto.ui_helpbrowser import Ui_HelpBrowser

logger = logging.getLogger(__name__)





def getCssHelpStyle(fontsize='medium', fontsize_big='large',
                    fontsize_code='medium', fontsize_small='small',
                    dark_mode=False):
    return (
        _HTML_CSS % {'fontsize': fontsize,
                     'fontsize_big': fontsize_big,
                     'fontsize_code': fontsize_code,
                     'fontsize_small': fontsize_small}
        + ( _HTML_CSS_COLORS if not dark_mode else _HTML_CSS_COLORS_DARK )
    )

TABLE_WIDTH = 550 # px

_HTML_CSS = '''
.content {
}
p {
  margin-top: 0pt;
  margin-bottom: 1em;
}
p, a, li, span {
  font-size: %(fontsize)s;
}
em, i {
  font-size: %(fontsize)s;
  font-style: italic;
}
strong, b {
  font-size: %(fontsize)s;
  font-style: bold;
}
code {
  font-size: %(fontsize_code)s;
}
.code-meta {
  font-style: italic;
}
.small {
  font-size: %(fontsize_small)s;
}
pre {
  margin-left: 12px;
  font-size: %(fontsize_code)s;
}
pre.txtcontent { margin-left: 0px; }
a { text-decoration: none }

.biglink{
  text-decoration: underline;
  font-size: %(fontsize_big)s;
}

li {
  margin-bottom: 0.35em;
}
dt {
  font-weight: bold;
  margin-left: 25px;
}
dd {
  margin-left: 50px;
}
table {
  margin-top: 1em;
  margin-bottom: 1em;
}
th {
  font-weight: bold;
  text-align: left;
  padding-right: 5px;
}
td {
  font-size: %(fontsize)s;
  padding-bottom: 0.3em;
}
td.indent {
  padding-left: 2em;
}
td p.inner {
  margin-bottom: 0.1em;
}
'''

_HTML_CSS_COLORS = '''
html, body {
  background-color: #ffffff;
  color: #303030;
}
.code-meta {
  color: #80b0b0;
}
.shadow {
  color: #a0a0a0;
}
a { color: #0000a0; }
th { color: #600030; }
'''

_HTML_CSS_COLORS_DARK = '''
html, body {
  background-color: #202020;
  color: #d0d0d0;
}
.code-meta {
  color: #a0d7d7;
}
.shadow {
  color: #808080;
}
a { color: #80a0ff; }
th { color: #c04080; }
'''


def wrapInHtmlContentContainer(htmlcontent, dark_mode=False, width=None):
    if width is None:
        width = TABLE_WIDTH

    html_top = ("<html><head><style type=\"text/css\">" +
                getCssHelpStyle(dark_mode=dark_mode) +
                "</style></head>" +
                "<body>")
    html_bottom = "</body></html>"

    return (html_top +
            "<table width=\""+str(width)+"\" style=\"margin-left:15px\">" +
            "<tr><td class=\"content\">" +
            htmlcontent +
            "</td></tr></table>" +
            html_bottom)





class HelpTopicPageWidget(QWidget):
    def __init__(self, helptopicpage, helpbrowser, parent):
        super().__init__(parent)

        self.lyt = QVBoxLayout(self)
        self.lyt.setContentsMargins(0,0,0,0)
        self.lyt.setSpacing(5)

        self.searchwidget = searchwidget.SearchWidget(self)
        self.lyt.addWidget(self.searchwidget)

        self.tb = QTextBrowser(self)
        self.lyt.addWidget(self.tb)

        self.setLayout(self.lyt)

        self.searchmgr = searchwidget.SearchTextEditManager(self.searchwidget, self.tb)

        font = self.tb.font()
        font.setPointSize(QFontInfo(font).pointSize()+1)
        self.tb.setFont(font)

        self.tb.setOpenLinks(False)
        self.tb.anchorClicked.connect(helpbrowser.openHelpTopicUrl)

        dark_mode = uiutils.is_dark_mode(self)

        htmlfragment = helptopicpage.contentAsHtmlFragment()
        logger.longdebug("Help page html fragment = \n%s", htmlfragment)
        html = wrapInHtmlContentContainer(htmlfragment, dark_mode=dark_mode)
        self.tb.setHtml(html)
        
        self.setProperty("HelpTabTitle", helptopicpage.title())
        if helptopicpage.desc:
            self.setProperty("HelpTabToolTip", helptopicpage.desc())


    def scrollToAnchor(self, aname):
        self.tb.scrollToAnchor(aname)


class TabAlreadyOpen(Exception):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget



_rx_scheme_frag = re.compile(
    r'^((?P<scheme>[A-Za-z0-9_.-]+):)?(?P<rest>.*)(\#(?P<fragment>[a-zA-Z0-9%_.-]+))?$'
)



class HelpBrowser(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_HelpBrowser()
        self.ui.setupUi(self)

        if sys.platform.startswith('darwin'):
            self.setWindowFlags(Qt.Tool)

        self.ui.tabs.tabCloseRequested.connect(self.closeTab)

        self.openTabs = []

        self.shortcuts = [
            QShortcut(QKeySequence('Ctrl+W'), self, self.closeCurrentTab, self.closeCurrentTab),
            ]


        # home page
        # ---------

        self.openHelpTopic('/home') # welcome page.

        # make the home page un-closeable
        self.ui.tabs.tabBar().setTabButton(0, QTabBar.LeftSide, None)
        self.ui.tabs.tabBar().setTabButton(0, QTabBar.RightSide, None)



    @pyqtSlot()
    def closeCurrentTab(self):
        index = self.ui.tabs.currentIndex()
        if (index == 0):
            # close help browser
            self.hide()
            return
        
        self.closeTab(index)

    @pyqtSlot(int)
    def closeTab(self, index):
        if (index == 0):
            return
        del self.openTabs[index]
        self.ui.tabs.removeTab(index)

    @pyqtSlot()
    def openHelpTopicBySender(self):
        sender = self.sender()
        path = str(sender.property('helppath'))
        if (not path):
            logger.warning("Bad help topic path: %r", path)
            return

        self.openHelpTopic(path)
        

    @pyqtSlot('QUrl')
    def openHelpTopicUrl(self, url):
        urlstr = url.toString()
        if urlstr.startswith('#'):
            # pure fragment part, internal scroll
            self.sender().scrollToAnchor(urlstr[1:])
            return
        self.openHelpTopic(urlstr)


    @pyqtSlot(str)
    def openHelpTopic(self, url):

        logger.debug("Help: open topic at URL %s", url)

        # split off scheme and fragment, if any
        (scheme, netloc, path, query, fragment) = urlsplit(url)

        logger.debug("url parsed into (scheme,netloc,path,query,fragment) = %r",
                     (scheme, netloc, path, query, fragment))

        if scheme in ['http', 'https']:
            QDesktopServices.openUrl(QUrl(url))
            return
        
        if scheme and scheme != 'help':
            raise ValueError("Invalid URL scheme: {} [url={}]".format(scheme, url))

        # combine path with query string
        pathqs = path
        if query:
            pathqs += '?' + query

        def canonpath_check_fn(canonpath):
            urlcanon = 'help:'+canonpath
            logger.debug("requested page has canonical url %r", urlcanon)
            # check to see if the tab is already open
            for tab in self.openTabs:
                if (str(tab.property('helpurl')) == urlcanon):
                    # just raise this tab.
                    raise TabAlreadyOpen(tab)

        widget = None
        try:

            page = helppages.get_help_page(
                pathqs,
                html_table_width_px=TABLE_WIDTH,
                canonpath_check_fn=canonpath_check_fn, # raise tab if page already open
            )

            widget = HelpTopicPageWidget(page, self, self.ui.tabs)
            widget.setProperty("helpurl", 'help:'+page.canonpath())

            tabindex = self.ui.tabs.addTab(widget, widget.property('HelpTabTitle'))
            self.ui.tabs.setTabToolTip(tabindex, widget.property('HelpTabToolTip'))
            #self.ui.tabs.setCurrentIndex(tabindex)

            self.openTabs.append(widget)

        except TabAlreadyOpen as t:
            widget = t.widget

        if widget is None:
            logger.debug("Couldn't open help topic widget for %r", url)
            return

        self.ui.tabs.setCurrentWidget(widget)

        if fragment:
            # we were asked to scroll to a specific anchor
            widget.scrollToAnchor(fragment)






#
# initial help page for the GUI --- /home
#
def _get_help_page_home(pathitems, kwargs):

    if len(pathitems) != 0:
        raise ValueError("Invalid help path: {}".format('/'.join(kwargs['basepathitems']+pathitems)))

    def big_html_link(txt, link):
        return """<a class="biglink" href="{link}">{txt}</a>""".format(
            txt=txt, link=link
        )

    home_src = "<h1>Help &amp; Reference Browser</h1>\n\n"

    home_src += ("<p>" + big_html_link("Welcome to bibolamazi", "help:/general/welcome")
                 + " \N{EM DASH} " +
                 big_html_link("Annotated filter list", "help:/filters")
                 + " \N{EM DASH} " +
                 big_html_link("Bibolamazi online docs", "https://bibolamazi.readthedocs.org/")
                 + " \N{EM DASH} " +
                 big_html_link("Bibolamazi version information", "help:/guiabout")
                 + " \N{EM DASH} " +
                 big_html_link("Bibolamazi command-line help", "help:/general/cmdline")
                 + "</p>\n\n")

    home_src += "<h2>Filters</h2>\n\n"

    from . import filterinstanceeditor # cyclic import if done @ top of module

    home_src += "<ul>\n"
    for filt in sorted(filterinstanceeditor.get_filter_list()):
        home_src += (
            "<li>&nbsp;<a href=\"help:/filter/{filtname}\"><b>{filtname}</b></a>\n".format(filtname=filt)
            )
    home_src += "</ul>\n"

    return helppages.HelpTopicPage.makeHtmlFragmentPage(home_src, title="Home", canonpath='/home')

#
def _get_help_page_guiabout(pathitems, kwargs):

    if len(pathitems) != 0:
        raise ValueError("Invalid help path: {}".format('/'.join(kwargs['basepathitems']+pathitems)))

    canonpath = '/guiabout'
    kwargs.get('canonpath_check_fn', lambda x: None)(canonpath)

    version_lines = [
        "<br/>".join(htmlescape(x) for x in helppages.helptext_prolog_lines()),
        """Hosted on [github.com/phfaist/bibolamazi](https://github.com/phfaist/bibolamazi)""",
        """Using Python {}""".format(htmlescape(sys.version).replace('\n', '<br/>')),
        """Using Qt {} (via PyQt5)""".format(htmlescape(QT_VERSION_STR))
    ]

    return  helppages.HelpTopicPage.makeMarkdownPage(
        "\n\n".join( version_lines ),
        title="Version",
        canonpath=canonpath
    )


#
# register help page dispatcher for /home and /guiabout
#
helppages.help_page_dispatchers['home'] = _get_help_page_home
helppages.help_page_dispatchers['guiabout'] = _get_help_page_guiabout
