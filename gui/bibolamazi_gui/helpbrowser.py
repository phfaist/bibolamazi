
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

from . import settingswidget
from . import searchwidget

from .qtauto.ui_helpbrowser import Ui_HelpBrowser

logger = logging.getLogger(__name__)



def getCssHelpStyle(fontsize='medium', fontsize_big='large', fontsize_code='medium', fontsize_small='small'):
    return _HTML_CSS % {'fontsize': fontsize,
                        'fontsize_big': fontsize_big,
                        'fontsize_code': fontsize_code,
                        'fontsize_small': fontsize_small}

def wrapInHtmlContentContainer(htmlcontent, width=None):
    if width is None:
        width = TABLE_WIDTH
    return ("<table width=\""+str(width)+"\" style=\"margin-left:15px\">" +
            "<tr><td class=\"content\">" +
            htmlcontent +
            "</td></tr></table>")

TABLE_WIDTH = 550 # px

_HTML_CSS = '''
html, body {
  background-color: #ffffff;
  color: #303030;
}
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
  color: #80b0b0;
  font-style: italic;
}
.shadow {
  color: #a0a0a0;
}
.small {
  font-size: %(fontsize_small)s;
}
pre { margin-left: 12px; }
pre.txtcontent { margin-left: 0px; }
a { color: #0000a0; text-decoration: none }

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
  color: #600030;
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



class HelpTopicPage(object):
    def __init__(self, content_type=None, content=None, title=None, tooltip=None):
        self._content_type = content_type
        self._content = content
        self._title = title
        self._tooltip = tooltip

    @staticmethod
    def makeMarkdownPage(markdown, title=None, tooltip=None):
        return HelpTopicPage('markdown', markdown, title, tooltip)

    @staticmethod
    def makeTxtPage(txt, title=None, tooltip=None):
        return HelpTopicPage('txt', txt, title, tooltip)

    @staticmethod
    def makeFullHtmlPage(html, title=None, tooltip=None):
        return HelpTopicPage('html', html, title, tooltip)

    @staticmethod
    def makeHtmlFragmentPage(html, title=None, tooltip=None):
        return HelpTopicPage('htmlfragment', html, title, tooltip)


    def contentAsMarkdown(self):
        if self._content_type == 'txt':
            return self._content
        elif self._content_type == 'markdown':
            return self._content
        else:
            raise ValueError("Can't convert %s to markdown"%(self._content_type))

    def contentAsHtml(self):
        html_top = ("<html><head><style type=\"text/css\">" +
                    getCssHelpStyle() +
                    "</style></head>" +
                    "<body>")
        html_bottom = "</body></html>"
        if self._content_type == 'txt':
            return (html_top
                    + wrapInHtmlContentContainer("<pre class=\"txtcontent\">"
                                                 + htmlescape(self._content)
                                                 + "</pre>")
                    + html_bottom)
        elif self._content_type == 'markdown':
            return (html_top
                    + wrapInHtmlContentContainer(
                        markdown2.markdown(self._content,
                                           extras=["footnotes", "fenced-code-blocks",
                                                   "smarty-pants", "tables"])
                    )
                    + html_bottom)
        elif self._content_type == 'html':
            return self._content
        elif self._content_type == 'htmlfragment':
            return html_top + wrapInHtmlContentContainer(self._content) + html_bottom
        else:
            raise ValueError("Can't convert %s to markdown"%(self._content_type))

    def title(self):
        return self._title

    def tooltip(self):
        return self._tooltip



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

        html = helptopicpage.contentAsHtml()#fontsize_pt=fontsize_pt, fontsize_code_pt=fontsize_code_pt)
        logger.longdebug("Help page text = \n%s", html)
        self.tb.setHtml(html)
        
        self.setProperty("HelpTabTitle", helptopicpage.title())
        if helptopicpage.tooltip:
            self.setProperty("HelpTabToolTip", helptopicpage.tooltip())

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
                     big_html_link("Bibolamazi version information", "help:/general/version")
                     + " \N{EM DASH} " +
                     big_html_link("Bibolamazi online docs", "https://bibolamazi.readthedocs.org/")
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
            return HelpTopicPage.makeTxtPage(argparseactions.helptext_prolog(), "Version")

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

                    html += ("<tr><th><a href=\"help:/filters/{filtname}\">{filtname}</a></th></tr>"+
                             "<tr><td class=\"indent\" width=\""+str(TABLE_WIDTH)+"\">{filtdesc}</td></tr>").format(
                                 filtname=finfo.filtername,
                                 filtdesc=finfo.fclass.getHelpDescription()
                             )
                html += "</table>"

            html += ("<p style=\"margin-top: 2em\"><em>Filter packages are listed in the order " +
                     "they are searched.</em></p>")

            return HelpTopicPage.makeHtmlFragmentPage(html, "Filter List")

        logger.warning("Unknown general help page: %s", page)

        return None








HELP_WELCOME = r"""

Bibolamazi --- Prepare consistent BibTeX files for your LaTeX documents
=======================================================================

Bibolamazi lets you prepare consistent and uniform BibTeX files for your LaTeX
documents. It lets you prepare your BibTeX entries as you would like them to
be---adding missing or dropping irrelevant information, capitalizing names or
turning them into initials, converting unicode characters to latex escapes, etc.


What Bibolamazi Does
--------------------

Bibolamazi works by reading your reference bibtex files---the "sources", which
might for example have been generated by your favorite bibliography manager or
provided by your collaborators---and merging them all into a new file, applying
specific rules, or "filters", such as turning all the first names into
initials or normalizing the way arxiv IDs are presented.

The Bibolamazi file is this new file, in which all the required bibtex entries
will be merged. When you prepare you LaTeX document, you should create a new
bibolamazi file, and provide that bibolamazi file as the bibtex file for the
bibliography.

When you open a bibolamazi file, you will be prompted to edit its configuration.
This is the set of rules which will tell bibolamazi where to look for your
bibtex entries and how to handle them. You first need to specify all your
sources, and then all the filters.

The bibolamazi file is then a valid BibTeX file to include into your LaTeX
document, so if your bibolamazi file is named `main.bibolamazi.bib', you would
include the bibliography in your document with a LaTeX command similar to:

    \bibliography{main.bibolamazi}


The Bibolamazi Configuration Section
------------------------------------

If you open the Bibolamazi application and open your bibolamazi file (or create
a new one), you’ll immediately be prompted to edit its configuration section.

Sources are the normal bibtex files from which bibtex entries are read. A source
is specified using the bibolamazi command

    src: source-file.bib  [ alternative-source-file.bib  ... ]

Alternative source locations can be specified, in case the first file does not
exist. This is convenient to locate a file which might be in different locations
on different computers. Each source file name can be an absolute path or a
relative path (relative to the bibolamazi file). It can also be an HTTP URL
which will be downloaded automatically.

You can specify several sources by repeating the src: command.

    src: first-source.bib  alternative-first-source.bib
    src: second-source.bib
    ...

Remember: the *first* readable source of *each* source command will be read, and
merged into the bibolamazi file.

Filters are rules to apply on the whole bibliography database. Their syntax is

    filter: filter_name  <filter-options>

The filter is usually meant to deal with a particular task, such as for example
changing all first names of authors into initials.

For a list of filters and what they do, please refer the first page of this help
browser.

You can usually fine-tune the behavior of the filter by providing options. For
a list of options for a particular filter, please refer again to the help page
of that filter.


What now?
---------

We suggest at this point that you create a new bibolamazi file, and get started
with the serious stuff :)

You might want to have a look at the documentation. It is available at
[https://bibolamazi.readthedocs.org/en/latest/](https://bibolamazi.readthedocs.org/en/latest/).

If you want an example, you can have a look at the directory
[https://github.com/phfaist/bibolamazi/tree/master/tests_basic](https://github.com/phfaist/bibolamazi/tree/master/tests_basic)
and, in particular the bibolamazi files `testX.bibolamazi.bib`.


Command-line
------------

Please note that you can also use bibolamazi in command-line. If you installed
the precompiled application, you'll need to install the command-line version
again. Go to
[https://github.com/phfaist/bibolamazi](https://github.com/phfaist/bibolamazi)
and follow the instructions there.

"""
