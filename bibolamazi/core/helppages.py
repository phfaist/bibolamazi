# -*- coding: utf-8 -*-
################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2019 by Philippe Faist                                       #
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

"""
This module defines callbacks and actions for parsing the command-line arguments for
bibolamazi. You're most probably not interested in this API. (Not mentioning that it might
change if I feel the need for it.)
"""

#import re
import os
#import sys
import os.path
import textwrap
import logging
from collections import OrderedDict

# don't change this, allow the construct 'from .helppages import htmlescape'
from html import escape as htmlescape

from urllib.parse import urlencode, parse_qs
from urllib.parse import quote_plus as urlquoteplus


# pydoc.pager(text) will open a pager for text (e.g. less), or pipe it out, and do everything as
# it should automatically.
import pydoc

import bibolamazi.init
from . import butils

logger = logging.getLogger(__name__)


# See string templates at end of file


# ------------------------------------------------------------------------------
# general utilities
# ------------------------------------------------------------------------------


def run_pager(text):
    """
    Call `pydoc.pager()` in a unicode-safe way.
    """
    return pydoc.pager(text)


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



class HelpPageError(Exception):
    def __init__(self, msg):
        super().__init__()
        self.msg = msg

    def logError(self):
        logger.error('%s',self.msg)

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg

# ------------------------------------------------------------------------------
# help pages system
# ------------------------------------------------------------------------------

class HelpTopicPage:
    def __init__(self, content_dict, title=None, desc=None, canonpath=None):
        """
        A help page about a given topic.

        Fields:

          * `content_dict`: a dictionary with keys being one of 'markdown',
            'txt', 'htmlfragment', and values being the corresponding content.
            Not all keys have to be provided.
        
          * `title`: a title for the page; not necessary displayed (but might be
            used as a tab title for the GUI)

          * `desc`: a longer, more descriptive title; not necessarily displayed
            (but might be used as a tab title tooltip/mouse-over for the GUI)

          * `canonpath`: canonical path for this help page
        """
        for k in content_dict:
            if k not in ['txt', 'markdown', 'htmlfragment']:
                raise HelpPageError("Unknown format: {}".format(k))
        self._content = dict(content_dict)
        self._title = title
        self._desc = desc
        self._canonpath = canonpath

    @staticmethod
    def makeMarkdownPage(markdown, **kwargs):
        return HelpTopicPage({'markdown': markdown}, **kwargs)

    @staticmethod
    def makeTxtPage(txt, **kwargs):
        return HelpTopicPage({'txt': txt}, **kwargs)

    @staticmethod
    def makeHtmlFragmentPage(html, **kwargs):
        return HelpTopicPage({'htmlfragment': html}, **kwargs)

    def getContent(self, fmt):
        x = self._content[fmt]
        if callable(x):
            return x()
        return x

    def contentAs(self, fmt):
        if fmt == 'markdown':
            return self.contentAsMarkdown()
        if fmt == 'txt':
            return self.contentAsTxt()
        if fmt == 'htmlfragment':
            return self.contentAsHtmlFragment()
        raise HelpPageError("Unknown format: {}".format(fmt))

    def contentAsMarkdown(self):

        if 'markdown' in self._content:
            return self.getContent('markdown')

        if 'txt' in self._content:
            return self.getContent('txt')

        raise HelpPageError("Can't convert content to markdown, we have {}"
                         .format(", ".join(self._content.keys())))

    def contentAsTxt(self):

        if 'txt' in self._content:
            return self.getContent('txt')

        if 'markdown' in self._content:
            return self.getContent('markdown')

        raise HelpPageError("Can't convert content to txt, we have {}"
                            .format(", ".join(self._content.keys())))

    def contentAsHtmlFragment(self):

        if 'htmlfragment' in self._content:
            return self.getContent('htmlfragment')

        if 'markdown' in self._content:

            # format documentation using markdown2.  Import this now only, so
            # that as long as we don't need markdown->html then this module
            # doesn't have to be installed
            import markdown2

            return ( markdown2.markdown(
                self.getContent('markdown'),
                extras=["footnotes", "fenced-code-blocks",
                        "smarty-pants", "tables"]) )

        if 'txt' in self._content:
            return ("<pre class=\"txtcontent\">" + htmlescape(self.getContent('txt')) + "</pre>")

        raise HelpPageError("Can't convert content to HTML, we have {}"
                            .format(", ".join(self._content.keys())))


    def title(self):
        return self._title

    def desc(self):
        return self._desc

    def canonpath(self):
        return self._canonpath


# ------------------------------------------------------------------------------
# help page dispatcher
# ------------------------------------------------------------------------------


def get_help_page(path, **kwargs):

    if path[0] != '/':
        raise HelpPageError("get_help_page() expects absolute pseudo-path")

    if '?' in path:
        (path, optstr) = path.split('?', 1)

        # parse optstr into dictionary and update kwargs
        qs = parse_qs(optstr)
        logger.debug("got options qs = %r", qs)
        kwargs.update(qs)


    pathitems = path[1:].split('/')

    # help_page_dispatchers is a global dict defined further down
    if pathitems[0] not in help_page_dispatchers:
        raise HelpPageError("Unknown help path: {}".format(path))

    return help_page_dispatchers[pathitems[0]](
        pathitems[1:],
        dict(kwargs, basepathitems=[pathitems[0]])
    )


def _get_help_canonpath_check(canonpath, kwargs):
    #
    # canonpath_check_fn= is an option that can be specified to get_help_page()
    # with a callable that is called when we identify the canonical path to a
    # page.  This is used in the GUI to see if a corresponding tab is already
    # open.
    #
    if kwargs.get('canonpath_check_fn', None) is not None:
        kwargs['canonpath_check_fn'](canonpath)


#
# /general/...
#
def _get_help_page_general(pathitems, kwargs):
    
    if pathitems == ['welcome']:

        canonpath = '/general/welcome'
        _get_help_canonpath_check(canonpath, kwargs)

        return HelpTopicPage.makeMarkdownPage(
            HELP_WELCOME,
            title="Welcome",
            canonpath=canonpath
        )

    if pathitems == ['cmdline']:

        canonpath = '/general/cmdline'
        _get_help_canonpath_check(canonpath, kwargs)

        p = kwargs.pop('parser', None)
        if p is None:
            from . import main as bibolamazimain
            p = bibolamazimain.get_args_parser()

        return HelpTopicPage.makeTxtPage(
            "\n".join(helptext_prolog_lines()) + "\n\n" +
            p.format_help(),
            title="Command-Line Help",
            canonpath=canonpath
        )

    if pathitems == ['version']:

        canonpath = '/general/version'
        _get_help_canonpath_check(canonpath, kwargs)

        return  HelpTopicPage.makeMarkdownPage(
            htmlescape("\n\n".join(
                helptext_prolog_lines())),
            title="Version",
            canonpath=canonpath
        )

    if pathitems == ['cmdlversion']:

        canonpath = '/general/cmdlversion'
        _get_help_canonpath_check(canonpath, kwargs)

        return HelpTopicPage.makeTxtPage(
            TMPL_VERSION_INFO.format(
                version=butils.get_version(),
                copyrightyear=butils.get_copyrightyear()
            ),
            title="Version",
            canonpath=canonpath
        )

    raise HelpPageError("Unknown help path: /{}".format('/'.join(kwargs['basepathitems']+pathitems)))


def _get_qs_filterpackage(kwargs):

    from bibolamazi.core.bibfilter import factory as filters_factory

    if 'filterpackage' in kwargs:
        fpkgspec = kwargs.pop('filterpackage')[0]
        fpname, fpdir = filters_factory.parse_filterpackage_argstr(fpkgspec)
        return OrderedDict( [(fpname, fpdir)] )

    return filters_factory.filterpath


#
# /filter/...
#
def _get_help_page_filter(pathitems, kwargs):

    if len(pathitems) != 1:
        raise HelpPageError("Unknown help path, expected filter name: /filter/{}"
                         .format('/'.join(pathitems)))

    filtname = pathitems[0]

    from bibolamazi.core.bibfilter import factory as filters_factory

    filterpath = _get_qs_filterpackage(kwargs)

    try:
        filtinfo = filters_factory.FilterInfo(filtname, filterpath=filterpath)
    except Exception as e:
        raise HelpPageError(str(e))

    canonpath = ('/' + '/'.join(kwargs['basepathitems']) + '/' + filtinfo.filtername + '?'
                 + urlencode([('filterpackage', filtinfo.filterpackagespec)]))

    _get_help_canonpath_check(canonpath, kwargs)

    title = filtname + ' filter'

    def gen_htmlfragment(filtname=filtname, filtinfo=filtinfo, kwargs=dict(kwargs)):

        html = "<h1>Filter: {}</h1>\n\n".format(filtname)

        fpn = filtinfo.filterpackagename
        html += "<p class=\"shadow\">In filter package <b>" + htmlescape(fpn) + "</b></p>\n\n"

        author = filtinfo.fclass.getHelpAuthor().strip()
        if author:
            html += "<p>" + htmlescape(author) + "</p>\n\n"

        desc = filtinfo.fclass.getHelpDescription().strip()
        if desc:
            html += "<p>" + htmlescape(desc) + "</p>\n\n"

        table_width_px_str = str(kwargs.get('html_table_width_px', 550))

        html_opt = ''
        html_doc = ''

        fopt = filtinfo.defaultFilterOptions()
        if fopt:
            # we're in business -- filter options

            html_opt += "<h2><a name=\"a-filter-options\"></a>Filter Options:</h2>\n\n"

            html_opt += "<table width=\""+table_width_px_str+"\">"

            for arg in fopt.filterOptions():
                sopt_arg_name = fopt.getSOptNameFromArg(arg.argname)
                html_opt += (
                    "<tr><th><a name=\"a-filter-option-{}\"></a>"
                    .format(urlquoteplus(arg.argname))
                    + htmlescape(sopt_arg_name) + "</th></tr>"
                )
                html_opt += "<tr><td class=\"indent\" width=\""+table_width_px_str+"\">"
                html_opt += "<p class=\"inner\">" + htmlescape(arg.doc if arg.doc else '') + "</p>"

                if arg.argtypename:
                    typ = butils.resolve_type(arg.argtypename, filtinfo.fmodule)
                    if typ is bool:
                        html_opt += ("<p class=\"inner shadow\">Expects a boolean argument type" +
                                 " (True/1/Yes/On or False/0/No/Off)</p>")
                    elif typ is int:
                        html_opt += ("<p class=\"inner shadow\">Expects an integer as argument</p>")
                    elif hasattr(typ, '__doc__') and typ.__doc__: # e.g., is not None
                        docstr = typ.__doc__.strip()
                        if len(docstr):
                            html_opt += (
                                "<p class=\"inner shadow\">Expects argument type " +
                                "<code>" + htmlescape(arg.argtypename) + "</code>: "
                                # avoid line breaks at hyphens, use NON-BREAKING HYPHEN
                                + htmlescape(docstr).replace('-','&#8209;') + "</p>"
                            )

                html_opt += "</td></tr>\n"

            if fopt.filterAcceptsVarArgs():
                html_opt += "<tr><th>(...)</th></tr>"
                html_opt += (
                    "<tr><td class=\"indent\" width=\""+table_width_px_str+"\">This filter accepts "
                    "additional positional arguments (see doc below)</td></tr>"
                )
            if fopt.filterAcceptsVarKwargs():
                html_opt += "<tr><th>(...=...)</th></tr>"
                html_opt += (
                    "<tr><td class=\"indent\" width=\""+table_width_px_str+"\">This filter accepts "
                    "additional named/keyword arguments (see doc below)</td></tr>"
                )

            html_opt += "</table>"

            html_opt += """
<h2><a name=\"a-option-syntax\"></a>Option Syntax:</h2>

<p>Options can be specified as <code>&#8209;s</code><span
class="code-meta">OptionName</span><code>="</code><span class="code-meta">option
value</span><code>"</code> or <code>&#8209;d</code><span
class="code-meta">OptionName[</span><code>=True</code><span
class="code-meta">|</span><code>False</code><span class="code-meta">]</span>.
For options that require specific argument types, use <code>&#8209;sXXX</code>
or <code>&#8209;dXXX</code> as appropriate.</p>
"""

            html_doc += "<h2><a name=\"a-filter-doc\"></a>Filter Documentation:</h2>\n\n"

            html_doc += ("<div style=\"white-space: pre-wrap\">"
                         + htmlescape(filtinfo.fclass.getHelpText())
                         + "</div>\n\n")

        elif hasattr(filtinfo.fmodule, 'format_help'):

            html_doc += ("<div style=\"white-space: pre-wrap\">"
                         + htmlescape(filtinfo.fmodule.format_help())
                         + "</div>\n\n")

        else:
            
            html_doc += "<p style=\"font-style\">"+htmlescape(filtinfo.fclass.getHelpText())+"</p>\n\n"
            #html += "<p style=\"font-style\">(no additional help available)</p>"

        if html_opt and html_doc:
            html += """
<p><b>Contents:</b></p>
<ul>
  <li><a href="#a-filter-opt">Filter Options</a></li>
  <li><a href="#a-option-syntax">Option Syntax</a></li>
  <li><a href="#a-filter-doc">Filter Documentation</li>
</ul>
"""

        html += html_opt
        html += html_doc

        return html

    def gen_txt(filtname=filtname, filtinfo=filtinfo, kwargs=dict(kwargs)):
        
        fpn = filtinfo.filterpackagename
        txt = "Filter: {} [in filter package {}]\n\n".format(filtname, fpn)

        author = filtinfo.fclass.getHelpAuthor().strip()
        if author:
            txt += author + "\n\n"

        desc = filtinfo.fclass.getHelpDescription().strip()
        if desc:
            txt += desc + "\n\n"

        w = textwrap.TextWrapper(initial_indent=' '*2, subsequent_indent=' '*2, width=80)
        wi = textwrap.TextWrapper(initial_indent=' '*8, subsequent_indent=' '*8, width=80)
        wity = textwrap.TextWrapper(initial_indent=' '*2, subsequent_indent=' '*4, width=80)

        fopt = filtinfo.defaultFilterOptions()
        if fopt:
            # we're in business -- filter options

            txt += "\nFILTER OPTIONS:\n\n"

            typ_docs = {}

            for arg in fopt.filterOptions():

                typ_annot = ''
                if arg.argtypename:
                    typ = butils.resolve_type(arg.argtypename, filtinfo.fmodule)
                    if typ is bool:
                        typ_annot = "(True|False)"
                    elif typ is int:
                        typ_annot = "(integer)"
                    elif hasattr(typ, '__doc__') and typ.__doc__: # e.g., is not None
                        docstr = typ.__doc__.strip()
                        if len(docstr):
                            typ_annot = "(type: " + arg.argtypename + ", see below)"
                            if arg.argtypename not in typ_docs:
                                typ_docs[arg.argtypename] = docstr
                        else:
                            typ_annot = "(type: " + arg.argtypename + ")"

                txt += ("  * " + fopt.getSOptNameFromArg(arg.argname)
                        + (' '*3+typ_annot if typ_annot else '') + "\n\n")
                if arg.doc:
                    txt += wi.fill(arg.doc).rstrip() + "\n\n"

            if fopt.filterAcceptsVarArgs():
                txt += "  * (...)\n\n"
                txt += \
                    wi.fill("This filter accepts additional positional arguments (see doc below)") \
                    + "\n\n"
            if fopt.filterAcceptsVarKwargs():
                txt += "  * (...=...)\n\n"
                txt += \
                    wi.fill("This filter accepts additional named/keyword arguments (see doc below)") \
                    + "\n\n"

            txt += "\nOPTION SYNTAX:\n\n"

            txt += w.fill("Options can be specified as -sOptionName=\"option-value\" "
                          "or -dOptionName[=True|False]. For specific argument types, "
                          "use -sXXX or -dXXX as appropriate:") + "\n\n"
            if typ_docs:
                txt += "\n\n".join([
                    wity.fill('Type {typ}: {docstr}'.format(typ=t, docstr=typ_docs[t]))
                    for t in sorted(list(typ_docs.keys()))
                ]) + "\n\n"

            txt += "\nFILTER DOCUMENTATION:\n\n"

            txt += filtinfo.fclass.getHelpText().rstrip() + "\n\n"

        
        elif hasattr(filtinfo.fmodule, 'format_help'):

            txt += filtinfo.fmodule.format_help().rstrip() + "\n\n"

        else:
            
            txt += filtinfo.fclass.getHelpText().rstrip() + "\n\n"
            #txt += "(no additional help available)\n\n"

        return txt

        # not great ---
        #return filtinfo.formatFilterHelp()

    return HelpTopicPage(
        {'htmlfragment': gen_htmlfragment,
         'txt': gen_txt},
        title=title,
        canonpath=canonpath)



#
# /filters
#
def _get_help_page_filters(pathitems, kwargs):

    if len(pathitems) != 0:
        raise HelpPageError("Invalid help path: /{}".format('/'.join(kwargs['basepathitems']+pathitems)))

    canonpath = '/filters'
    _get_help_canonpath_check(canonpath, kwargs)

    # first, make an inventory of filterpackages, filters and corresponding
    # description; store in a big list/dict

    fdata = []

    from bibolamazi.core.bibfilter import factory as filters_factory

    filterpath = filters_factory.filterpath

    for (fp,fplist) in filters_factory.detect_filter_package_listings(filterpath=filterpath).items():
        fdata.append({
            'fp': fp,
            'filterinfolist': sorted(fplist, key=lambda x: x.filtername)
        })

    def gen_txt(d=fdata):
        
        def fmt_filter_helpline(finfo, fpkg):

            nlindentstr = "\n%16s"%("") # newline, followed by 16 whitespaces
            return ( "  %-12s  " %(finfo.filtername) +
                     nlindentstr.join(textwrap.wrap(finfo.fclass.getHelpDescription(),
                                                    (80-16) # 80 line width, -16 indent chars
                                                    ))
                     )

        full_filter_list = []
        for fd in d:
            fp = fd['fp']
            finfolist = fd['filterinfolist']
            filter_list = [
                fmt_filter_helpline(f, fp)
                for f in finfolist
                ]
            full_filter_list.append(
                TMPL_FILTER_HELP_INNER_PACKAGE_LIST.format(
                    filterpackage=fp,
                    filterlistcontents="\n".join(filter_list)
                )
            )

        return TMPL_FILTERS_HELP.format(full_filter_list="\n\n".join(full_filter_list))

    def gen_htmlfragment(d=fdata, kwargs=dict(kwargs)):

        html = "<h1>List of filters</h1>\n\n"

        for fd in d:
            fp = fd['fp']
            finfolist = fd['filterinfolist']

            html += "<h2>Filter package <b>{filterpackage}</b></h2>\n\n".format(filterpackage=fp)

            html += "<table>"
            for finfo in finfolist:

                html += (
                    "<tr><th><a href=\"help:/filter/{filtname}\">{filtname}</a></th></tr>"+
                    "<tr><td class=\"indent\" width=\""+str(kwargs.get('html_table_width_px', 550))
                    +"\">{filtdesc}</td></tr>\n"
                ).format(
                    filtname=finfo.filtername,
                    filtdesc=finfo.fclass.getHelpDescription()
                )
            html += "</table>"

        html += ("<p style=\"margin-top: 2em\"><em>Filter packages are listed in the order " +
                 "they are searched.</em></p>")

        return html

    return HelpTopicPage(
        {'txt': gen_txt,
         'htmlfragment': gen_htmlfragment},
        title="Filter List",
        canonpath=canonpath
    )


#
# list of dispatchers
#
help_page_dispatchers = {
    'general': _get_help_page_general,
    'filter': _get_help_page_filter,
    'filters': _get_help_page_filters,
}



# ------------------------------------------------------------------------------
# command-line actions
# ------------------------------------------------------------------------------


def cmdl_show_help(path, **kwargs):

    try:
        page = get_help_page(path, **kwargs)
    except Exception as e:
        logger.error('%s', str(e))
        return

    fmt = os.environ.get('BIBOLAMAZI_HELP_FORMAT', 'txt')

    run_pager(page.contentAs(fmt))


# # --help
# def cmdl_help(parser=None):
#     p = get_help_page('/general/cmdline', parser=parser)
#     run_pager(p.contentAsTxt())

# # --help /help/topic
# def cmdl_help(path, parser=None):
#     p = get_help_page(path, parser=parser)
#     run_pager(p.contentAsTxt())

# # --version    
# def cmdl_version():
#     p = get_help_page('/general/cmdlversion')
#     sys.stdout.write(p.contentAsTxt())

# # --help <filtername>
# def cmdl_filter_info(thefilter):
#     p = get_help_page('/filter/'+thefilter)
#     run_pager(p.contentAsTxt())

# # --list-filters
# def cmdl_list_filters():
#     p = get_help_page('/filters')
#     run_pager(p.contentAsTxt())



# ------------------------------------------------------------------------------
# string templates
# ------------------------------------------------------------------------------


def helptext_prolog_lines():
    return [x.format(
        version=butils.get_version(),
        copyrightyear=butils.get_copyrightyear()
    ) for x in TMPL_PROLOG]


TMPL_PROLOG = [
    """Bibolamazi Version {version} by Philippe Faist (C) {copyrightyear}""",
    """Licensed under the terms of the GNU Public License GPL, version 3 or higher."""
]

TMPL_VERSION_INFO = """\
Version: {version}
Bibolamazi by Philippe Faist
(C) {copyrightyear} Philippe Faist
Licensed under the terms of the GNU Public License GPL, version 3 or higher.
"""


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



TMPL_FILTERS_HELP = """

List of available filters:
--------------------------

{full_filter_list}

--------------------------

Filter packages are listed in the order they are searched.

Use  bibolamazi --help <filter>  for more information about a specific filter
and its options.


"""

TMPL_FILTER_HELP_INNER_PACKAGE_LIST = """\
Package '{filterpackage}':

{filterlistcontents}
""".rstrip() # no trailing '\n'


