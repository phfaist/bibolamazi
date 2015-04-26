################################################################################
#                                                                              #
#   This file is part of the Bibolamazi Project.                               #
#   Copyright (C) 2015 by Philippe Faist                                       #
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

from core.butils import getbool
from core.bibfilter import BibFilter, BibFilterError
from core.bibfilter.argtypes import enum_class
from core.main import verbosity_logger_level
from core import blogger

logger = logging.getLogger(__name__)

# for the arxiv info parser tool
from .util import arxivutil


HELP_AUTHOR = u"""\
ECHO filter by Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = u"""\
Echo a custom message in the bibolamazi log
"""

HELP_TEXT = """
Echo a custom message in the bibolamazi log. This does not affect the database, but might
provide someone running Bibolamazi with some important information.
"""


FMT_DEFAULT = 0
FMT_SIMPLE = 1
FMT_WARN = 2

msgformats = {
    FMT_DEFAULT:  ("-"*80 + "\n%s\n" + "-"*80),
    FMT_SIMPLE:   "%s",
    FMT_WARN:     ("\n" + "#"*80 + "\nWARNING: %s\n" + "#"*80 + "\n"),
    }

EchoFormat = enum_class('EchoFormat',
                        [('default', FMT_DEFAULT),
                         ('simple', FMT_SIMPLE),
                         ('warn', FMT_WARN)
                         ],
                       default_value='default',
                       value_attr_name='msgformat')

LogLevel = enum_class('LogLevel',
                      [('LONGDEBUG', blogger.LONGDEBUG),
                       ('DEBUG', logging.DEBUG),
                       ('WARNING', logging.WARNING),
                       ('INFO', logging.INFO),
                       ('ERROR', logging.ERROR),
                       ('CRITICAL', logging.CRITICAL)],
                      default_value='INFO',
                      value_attr_name='levelno')

class EchoFilter(BibFilter):
    
    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, message, **kwargs):
        """Echo a custom message into the bibolamazi logger.

        Arguments:
          - message: the message to echo
          - level(LogLevel): the logger level required to display the message (one of 'LONGDEBUG',
            'DEBUG', 'WARNING', 'INFO', 'ERROR' or 'CRITICAL')
          - format(EchoFormat): how to display the message (one of 'default', 'simple' or 'warn')
          - warn(bool): short for '-sFormat=warn -sLevel=WARNING'
        """
        BibFilter.__init__(self);

        self.message = message

        iswarn = kwargs.get('warn', None)
        if iswarn is not None and getbool(iswarn):
            if 'level' not in kwargs:
                kwargs['level'] = 'WARNING'
            if 'format' not in kwargs:
                kwargs['format'] = 'warn'

        self.loglevel = LogLevel(kwargs.get('level', logging.INFO))

        f = EchoFormat(kwargs.get('format', FMT_DEFAULT))
        self.fmt = msgformats[f.msgformat]


    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE;

    def filter_bibolamazifile(self, bibolamazifile):

        logger.log(self.loglevel.levelno,
                   self.fmt,
                   self.message)

        return


def bibolamazi_filter_class():
    return EchoFilter;

