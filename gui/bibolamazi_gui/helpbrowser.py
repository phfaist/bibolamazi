
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
from future.standard_library import install_aliases
install_aliases()

import sys
import logging
import os.path
from collections import OrderedDict

# don't change this, we use 'from .htmlbrowser import htmlescape'
from html import escape as htmlescape
from urllib.parse import urlparse, urlunparse, urlencode, parse_qs

import markdown2

import bibolamazi.init
from bibolamazi.core import main as bibolamazimain
from bibolamazi.core import blogger
from bibolamazi.core.blogger import logger
from bibolamazi.core import butils
from bibolamazi.core import argparseactions
from bibolamazi.core.bibfilter import factory as filters_factory

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from . import uiutils
from . import settingswidget
from . import searchwidget

from .qtauto.ui_helpbrowser import Ui_HelpBrowser

logger = logging.getLogger(__name__)



# helper for wrapping long lines -- used in other files
def forcewrap_long_lines(x, w=120):
    lines = []
    for line in x.split('\n'):
        # expand tabs first
        line = line.replace('\t', ' '*8)
        while len(line)>w:
            lines.append(line[:(w-1)]+'\\')
            line = line[(w-1):]
        lines.append(line)
    return "\n".join(lines)





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
pre { margin-left: 12px; }
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
    def __init__(self, helptopicpage, urlcanon, helpbrowser, parent):
        super(HelpTopicPageWidget, self).__init__(parent)

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

        self.setProperty("helpurl", urlcanon)




class TabAlreadyOpen(Exception):
    def __init__(self, widget):
        super(TabAlreadyOpen, self).__init__()
        self.widget = widget


class HelpBrowser(QWidget):
    def __init__(self):
        super(HelpBrowser, self).__init__()

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

        self.openHelpTopic('/') # welcome page.

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
        self.openHelpTopic(url.toString())


    @pyqtSlot(str)
    def openHelpTopic(self, url):

        logger.debug("Help: open topic at URL %s", url)

        urlparts = urlparse(url)

        if urlparts.scheme in ['http', 'https']:
            QDesktopServices.openUrl(QUrl(url))
            return
        
        if urlparts.scheme and urlparts.scheme != 'help':
            raise ValueError("Invalid URL scheme: %s [url=%s]"%(urlparts.scheme, url))

        

        import posixpath
        path = posixpath.normpath(urlparts.path)
        qs = parse_qs(urlparts.query) # any options etc.

        logger.debug("got options qs = %r", qs)

        opt = {}

        if 'filterpackage' in qs:
            fpkgspec = qs.pop('filterpackage')[0]
            fpname, fpdir = filters_factory.parse_filterpackage_argstr(fpkgspec)
            opt['filterpackage'] = (fpname, fpdir)
        # add other url options here ...
        if qs:
            raise ValueError("Unknown help topic url options: %r"%(qs))

        pathitems = [x for x in path.split('/') if x]

        widget = None
        try:
            widget = self._gethelptopicwidget(pathitems, opt=opt, parent=self.ui.tabs)
        except TabAlreadyOpen as t:
            self.ui.tabs.setCurrentWidget(t.widget)
            return

        if widget is None:
            logger.debug("Couldn't open help topic widget for %r", url)
            return

        tabindex = self.ui.tabs.addTab(widget, widget.property('HelpTabTitle'))
        self.ui.tabs.setTabToolTip(tabindex, widget.property('HelpTabToolTip'))
        self.ui.tabs.setCurrentIndex(tabindex)

        self.openTabs.append(widget)


    def _findopenhelptopicwidget(self, urlcanon):

        # check to see if the tab is already open
        for tab in self.openTabs:
            if (str(tab.property('helpurl')) == urlcanon):
                # just raise this tab.
                raise TabAlreadyOpen(tab)

    def _mkhelptopicwidget(self, helptopicpage, urlcanon, parent):

        return HelpTopicPageWidget(helptopicpage, urlcanon, self, parent)

    
    def _gethelptopicwidget(self, pathitems, opt, parent):

        logger.debug("_gethelptopicwidget(): pathitems=%r, opt=%r", pathitems, opt)

        if len(pathitems) == 0:
            # home page

            urlcanon = 'help:/'
            self._findopenhelptopicwidget(urlcanon)
            return self._mkhelptopicwidget(self._gethelptopic_home(), urlcanon, parent=parent)

        if (pathitems[0] == 'general'):
            if (len(pathitems) < 2):
                logger.warning("_gethelptopicwidget(): No help topic general page specified!!")
                return None

            urlcanon = 'help:/' + '/'.join(pathitems)
            self._findopenhelptopicwidget(urlcanon)
            return self._mkhelptopicwidget(self._gethelptopic_general('/'.join(pathitems[1:])),
                                           urlcanon, parent=parent)


        if pathitems[0] == 'filters' or pathitems[0] == 'rawfilterdoc':

            if (len(pathitems) < 2):
                logger.warning("_gethelptopicwidget(): No filter specified!!")
                return None

            filtname = pathitems[1]

            if 'filterpackage' in opt:
                filterpath = OrderedDict([opt['filterpackage']])
            else:
                filterpath = filters_factory.filterpath

            finfo = filters_factory.FilterInfo(filtname, filterpath=filterpath)

            urlcanon = ('help:/' + pathitems[0] + '/' + finfo.filtername + '?'
                        + urlencode([('filterpackage', finfo.filterpackagespec)]))

            self._findopenhelptopicwidget(urlcanon)

            page = None
            if pathitems[0] == 'filters':
                page = self._gethelptopic_filters(finfo)
            elif pathitems[0] == 'rawfilterdoc':
                page = self._gethelptopic_rawfilterdoc(finfo)
            else:
                raise RuntimeError("pathitems[0]=%r ??"%(pathitems[0]))

            return self._mkhelptopicwidget(page, urlcanon, parent=parent)
        
        logger.warning("_gethelptopicwidget(): Unknown help topic: %r", "/".join(pathitems))
        return None

            

    def _gethelptopic_home(self):
        """
        Return a `HelpTopicPage` object or `None`.
        """

        def big_html_link(txt, link):
            return """<a class="biglink" href="{link}">{txt}</a>""".format(
                txt=txt, link=link
                )

        home_src = "<h1>Help &amp; Reference Browser</h1>\n\n"

        home_src += ("<p>" + big_html_link("Welcome to bibolamazi", "help:/general/welcome")
                     + " \N{EM DASH} " +
                     big_html_link("Annotated filter list", "help:/general/filter-list")
                     + " \N{EM DASH} " +
                     big_html_link("Bibolamazi online docs", "https://bibolamazi.readthedocs.org/")
                     + " \N{EM DASH} " +
                     big_html_link("Bibolamazi version information", "help:/general/version")
                     + " \N{EM DASH} " +
                     big_html_link("Bibolamazi command-line help", "help:/general/cmdline")
                     + "</p>\n\n")

        home_src += "<h2>Filters</h2>\n\n"

        from . import filterinstanceeditor # cyclic import if done @ top of module

        home_src += "<ul>\n"
        for filt in sorted(filterinstanceeditor.get_filter_list()):
            home_src += (
                "<li>&nbsp;<a href=\"help:/filters/{filtname}\"><b>{filtname}</b></a>\n".format(filtname=filt)
                )
        home_src += "</ul>\n"

        return HelpTopicPage.makeHtmlFragmentPage(home_src, "Home")

    def _gethelptopic_filters(self, filtinfo):

        filtname = filtinfo.filtername

        title = filtname + ' filter'

        html = "<h1>Filter: {}</h1>\n\n".format(filtname)

        fpn = filtinfo.filterpackagename
        html += "<p class=\"shadow\">In filter package <b>" + htmlescape(fpn) + "</b></p>\n\n"

        author = filtinfo.fclass.getHelpAuthor().strip()
        if author:
            html += "<p>" + htmlescape(author) + "</p>\n\n"

        desc = filtinfo.fclass.getHelpDescription().strip()
        if desc:
            html += "<p>" + htmlescape(desc) + "</p>\n\n"

        fopt = filtinfo.defaultFilterOptions()
        if fopt:
            # we're in business -- filter options

            html += "<h2>Filter Options:</h2>\n\n"

            html += "<table width=\""+str(TABLE_WIDTH)+"\">"

            for arg in fopt.filterOptions():
                html += "<tr><th>" + htmlescape(fopt.getSOptNameFromArg(arg.argname)) + "</th></tr>"
                html += "<tr><td class=\"indent\" width=\""+str(TABLE_WIDTH)+"\">"
                html += "<p class=\"inner\">" + htmlescape(arg.doc if arg.doc else '') + "</p>"

                if arg.argtypename:
                    typ = butils.resolve_type(arg.argtypename, filtinfo.fmodule)
                    if typ is bool:
                        html += ("<p class=\"inner shadow\">Expects a boolean argument type" +
                                 " (True/1/Yes/On or False/0/No/Off)</p>")
                    elif typ is int:
                        html += ("<p class=\"inner shadow\">Expects an integer as argument</p>")
                    elif hasattr(typ, '__doc__') and typ.__doc__: # e.g., is not None
                        docstr = typ.__doc__.strip()
                        if len(docstr):
                            html += ("<p class=\"inner shadow\">Expects argument type " +
                                     "<code>" + htmlescape(arg.argtypename) + "</code>: "
                                     + docstr + "</p>")

                html += "</td></tr>\n"

            if fopt.filterAcceptsVarArgs():
                html += "<tr><th>(...)</th></tr>"
                html += ("<tr><td class=\"indent\" width=\""+str(TABLE_WIDTH)+"\">This filter accepts "
                         "additional positional arguments (see doc below)</td></tr>")
            if fopt.filterAcceptsVarKwargs():
                html += "<tr><th>(...=...)</th></tr>"
                html += ("<tr><td class=\"indent\" width=\""+str(TABLE_WIDTH)+"\">This filter accepts "
                         "additional named/keyword arguments (see doc below)</td></tr>")

            html += "</table>"

            html += """

<p>Pass options with the syntax <code>-s</code><span
class="code-meta">OptionName</span><code>="</code><span class="code-meta">option
value</span><code>"</code> or <code>-d</code><span
class="code-meta">OptionName[</span><code>=True</code><span
class="code-meta">|</span><code>False</code><span class="code-meta">]</span>.
The form <code>-sXXX</code> is for passing strings (which must be quoted if
comprising spaces or special characters), and the form <code>-dXXX</code> is for
specifying boolean ON/OFF switches.</p>

"""

            html += "<h2>Filter Documentation:</h2>\n\n"

            html += "<div style=\"white-space: pre-wrap\">" + htmlescape(filtinfo.fclass.getHelpText()) + "</div>\n\n"

            urlrawdoc = ('help:/rawfilterdoc/' + filtinfo.filtername + '?' +
                         urlencode([('filterpackage', filtinfo.filterpackagespec)]))

            html += ("<p style=\"margin-top: 2em\"><a href=\""+htmlescape(urlrawdoc)+"\">" +
                     "View this filter's raw documentation</a></p>\n\n")

            return HelpTopicPage.makeHtmlFragmentPage(html, title)

        if hasattr(filtinfo.fmodule, 'format_help'):
            html += "<div style=\"white-space: pre-wrap\">" + filtinfo.fmodule.format_help() + "</div>"
            return HelpTopicPage.makeHtmlFragmentPage(html, title)


        return HelpTopicPage.makeMarkdownPage(
            "*No documentation available for filter {}*".format(filtname),
            title
        )
    

    def _gethelptopic_rawfilterdoc(self, finfo):

        filtertxt = finfo.formatFilterHelp()
        title = '%s filter (raw doc)'%(finfo.filtername)
        desc = finfo.fclass.getHelpDescription()

        return HelpTopicPage.makeTxtPage(filtertxt, title, desc)


    def _gethelptopic_general(self, page):

        if page == 'welcome':
            return HelpTopicPage.makeMarkdownPage(HELP_WELCOME, "Welcome")

        elif page == 'version':
            return HelpTopicPage.makeMarkdownPage(
                htmlescape(argparseactions.helptext_prolog().replace("\n", "\n\n")),
                "Version")

        elif page == 'cmdline':
            return HelpTopicPage.makeTxtPage(
                argparseactions.helptext_prolog() +
                bibolamazimain.get_args_parser().format_help(),
                "Command-Line Help")

        elif page == 'filter-list':
            html = "<h1>List of filters</h1>\n\n"

            filterpath = filters_factory.filterpath

            for (fp,fplist) in iteritems(filters_factory.detect_filter_package_listings(filterpath=filterpath)):

                html += "<h2>Filter package <b>{filterpackage}</b></h2>\n\n".format(filterpackage=fp)

                html += "<table>"
                for finfo in sorted(fplist, key=lambda x: x.filtername):

                    html += (
                        "<tr><th><a href=\"help:/filters/{filtname}\">{filtname}</a></th></tr>"+
                        "<tr><td class=\"indent\" width=\""+str(TABLE_WIDTH)+"\">{filtdesc}</td></tr>"
                    ).format(
                        filtname=finfo.filtername,
                        filtdesc=finfo.fclass.getHelpDescription()
                    )
                html += "</table>"

            html += ("<p style=\"margin-top: 2em\"><em>Filter packages are listed in the order " +
                     "they are searched.</em></p>")

            return HelpTopicPage.makeHtmlFragmentPage(html, "Filter List")

        logger.warning("Unknown general help page: %s", page)

        return None


