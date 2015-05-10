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

"""
Set up a logging framework for logging debug, information, warning and error
messages.

Modules should get their logger using Python's standard :py:mod:`logging`
mechanism::

    import logging
    logger = logging.getLogger(__name__)

This allows for the user to be rather specific about which type of messages
she/he would like to see.
"""

import os
import sys
import logging

import bibolamazi.init



# ------------------------------------------------------------------------------

# New Level: LONGDEBUG

# note: DEBUG=10, INFO=20, WARNING=30 etc.
LONGDEBUG = 5
logging.addLevelName(LONGDEBUG, "LONGDEBUG");



# ------------------------------------------------------------------------------

# our Logger class

class BibolamaziLogger(logging.getLoggerClass()):
    """
    A Logger used in Bibolamazi.

    This logger class knows about an additional log level,
    :py:const:`LONGDEBUG`.
    """
    
    def getSelfLevel(self):
        """
        Returns the level that was set on this logger. If no specific level was set, then
        returns `logging.NOTSET`. In this respect, this is NOT the same as
        `getEffectiveLevel()`.
        """
        return self.level # hacked from logging.py source... better way?

    def longdebug(self, msg, *args, **kwargs):
        """
        Produce a log message at level LONGDEBUG.
        """
        if self.isEnabledFor(LONGDEBUG):
            # Yes, _log takes its args as 'args', not '*args'
            self._log(LONGDEBUG, msg, args, **kwargs)

            
logging.setLoggerClass(BibolamaziLogger)




# ==============================================================================
# LOG FORMATTER.
# ==============================================================================


_ttycolors = {
    # 31 == red, 32 == green, 33 == yellow, 34 == blue, 35 == magenta, 36 == cyan
    # 40 == black bg
    LONGDEBUG: ('', '', ''),
    logging.DEBUG: ('', '', ''),
    logging.INFO: ('\033[0m', '\033[1m', '\033[0m'),
    logging.WARNING: ('\033[35m', '\033[35;1m', '\033[0m'), # 33 == yellow, 35 == magenta
    logging.ERROR: ('\033[31m', '\033[31;1m', '\033[0m'), # 31 == red
    logging.CRITICAL: ('\033[31m', '\033[31;1m', '\033[0m'),
    }



class BibolamaziConsoleFormatter(logging.Formatter):
    """
    Format log messages for console output. Customized for bibolamazi.
    """
    def __init__(self, ttycolors=False, show_pos_info_level=None, **kwargs):
        self.ttycolors = ttycolors
        self.show_pos_info_level = show_pos_info_level
        return logging.Formatter.__init__(self, **kwargs)

    def setShowPosInfoLevel(self, level):
        self.show_pos_info_level = level

    def format(self, record):
        #
        # taken from logging.Formatter.format() source code
        #
        message = record.getMessage()

        head = ""
        indent = ' '*4
        #ttycolorheadstart = ''
        #ttycolorstart = ''
        #ttycolorend = ''

        if self.ttycolors:
            thettycolorheadstart = lambda : _ttycolors.get(record.levelno, ('','',''))[0]
            thettycolorstart = lambda : _ttycolors.get(record.levelno, ('','',''))[1]
            thettycolorend = lambda : _ttycolors.get(record.levelno, ('','',''))[2]
        else:
            thettycolorheadstart = lambda : ''
            thettycolorstart = lambda : ''
            thettycolorend = lambda : ''

        if self.show_pos_info_level is not None and record.levelno <= self.show_pos_info_level:
            head = '[%s l.%d]: %s():\n'%(record.name, record.lineno, record.funcName)

        if record.levelno == logging.CRITICAL:
            #head += 'CRITICAL: '
            # so that 'CRITICAL' also gets the message tty color, not the head color
            message = 'CRITICAL: '+message
            #ttycolorheadstart = '\033[31m'
            #ttycolorstart = '\033[31;1m'
            #ttycolorend = '\033[0m'
        elif record.levelno == logging.ERROR:
            #head += 'ERROR: '
            # so that 'ERROR' also gets the message tty color, not the head color
            message = 'ERROR: '+message
            #ttycolorheadstart = '\033[31m'
            #ttycolorstart = '\033[31;1m'
            #ttycolorend = '\033[0m'
        elif record.levelno == logging.WARNING:
            #head += 'WARNING: '
            message = 'WARNING: '+message
            # 35 == magenta
            # 33 == yellow
        elif record.levelno == logging.INFO:
            indent = ''
            # 32 == green
            #ttycolorheadstart = '\033[32m'
            #ttycolorstart = '\033[32;1m'
            #ttycolorend = '\033[0m'
        elif record.levelno == logging.DEBUG:
            #asctime = self.formatTime(record, self.datefmt)
            indent = '-- '+ ' '*2
            head   = '-- '+head.replace('\n', '\n'+indent)
        elif record.levelno == LONGDEBUG:
            #asctime = self.formatTime(record, self.datefmt)
            indent = '  -- '+ ' '*2
            head   = '  -- '+head.replace('\n', '\n'+indent)

            
        msg = message.replace('\n', '\n'+indent)

        s = thettycolorheadstart() + head + thettycolorend() + thettycolorstart() + msg
        
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        if record.exc_text:
            s = s.rstrip() + "\n"+indent
            exc_text = record.exc_text.replace('\n', '\n'+indent)
            try:
                s = s + exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                s = s + exc_text.decode(sys.getfilesystemencoding(),
                                        'replace')

        s += thettycolorend()

        return s


#
# Since 2.1, we don't use this ConditionalFormatter, but our new
# BibolamaziConsoleFormatter instaad.
#
# We'll keep this for convenience, and also because the GUI uses it.
#
class ConditionalFormatter(logging.Formatter):
    """
    A formatter class.

    Very much like logging.Formatter, except that different formats can be specified for
    different log levels.

    Specify the different formats to the constructor with keyword arguments. E.g.::
    
      ConditionalFormatter('%(message)s',
                           DEBUG='DEBUG: %(message)s',
                           INFO='just some info... %(message)s')
    
    This will use `'%(message)s'` as format for all messages except with level other thand
    DEBUG or INFO, for which their respective formats are used.
    """
    
    def __init__(self, defaultfmt=None, datefmt=None, **kwargs):
        self.default_format = defaultfmt;
        self.special_formats = kwargs;
        return logging.Formatter.__init__(self, defaultfmt, datefmt);


    def format(self, record):
        if (record.levelname in self.special_formats):
            return self.do_format(record, self.special_formats[record.levelname]);
        return self.do_format(record, self.default_format);
    
    def do_format(self, record, fmt):
        #
        # taken from logging.Formatter.format() source code
        #
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        u = dict([(k,v) for k,v in record.__dict__.iteritems()])
        msg = record.message
        if callable(fmt):
            u['message'] = msg
            s = fmt(u)
        else:
            s = []
            for line in msg.split('\n'):
                u['message'] = line
                s.append(fmt % u)
            s = '\n'.join(s)

        
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            try:
                s = s + record.exc_text
            except UnicodeError:
                # Sometimes filenames have non-ASCII chars, which can lead
                # to errors when s is Unicode and record.exc_text is str
                # See issue 8924.
                # We also use replace for when there are multiple
                # encodings, e.g. UTF-8 for the filesystem and latin-1
                # for a script. See issue 13232.
                s = s + record.exc_text.decode(sys.getfilesystemencoding(),
                                               'replace')
        return s





# DEBUG/LOGGING
# create logger
logger = logging.getLogger('bibolamazi.old_logger');
"""
(OBSOLETE) The main logger object. This is a :py:class:`logging.Logger` object.

.. deprecated:: 2.1

   This object is still here to keep old code functioning. New code should use
   the following idiom somewhere at the top of their module::
   
     import logging
     logger = logging.getLogger(__name__)

   (Just make sure the logging mechanism has been set up correctly already, see
   doc for :py:mod:`~core.blogger` module.)

This object has an additional method `longdebug()` (which behaves similarly to
`debug()`), for logging long debug output such as dumping the database during
intermediate steps, etc.  This corresponds to bibolamazi command-line verbosity
level 3.
"""


_simple_console_logging_setup_done = False

def setup_simple_console_logging(logger=logging.getLogger(), stream=sys.stderr):
    """
    Sets up the given logger object for simple console output.

    The main program module may for example invoke this function on the root
    logger to provide a basic logging mechanism.
    """

    global _simple_console_logging_setup_done

    if _simple_console_logging_setup_done:
        logger.warning("Simple console logging already set up!")
        return
    
    _simple_console_logging_setup_done = True

    # create console handler
    ch = logging.StreamHandler(stream=stream);
    ch.setLevel(logging.NOTSET); # propagate all messages

    # create formatter and add it to the handlers

    ttycolors = None
    
    if sys.platform.startswith('win32'):
        ttycolors = False
    else:
        s_ttycolors = os.environ.get("BIBOLAMAZI_TTY_COLORS", None)
        if s_ttycolors is not None:
            if s_ttycolors.strip().lower() == 'yes':
                ttycolors = True
            elif s_ttycolors.strip().lower() == 'no':
                ttycolors = False
            elif s_ttycolors.strip().lower() == 'auto':
                ttycolors = None
            else:
                sys.stderr.write("Warning: Can't parse value of env['BIBOLAMAZI_TTY_COLORS']. "
                                 "Expected 'yes', 'no', or 'auto'")

        if ttycolors is None:
            ttycolors = stream.isatty()

    # instance of our personalized log messages formatter
    formatter = BibolamaziConsoleFormatter(ttycolors=ttycolors)
    ch.setFormatter(formatter);
    
    # add the handlers to the logger
    logger.addHandler(ch);

    # for accessing the bibolamazi formatter. This is so that the main module
    # can set the level at which the logrecord position info (module, line no,
    # function) is reproduced
    logger.bibolamazi_formatter = formatter

    



# ------------------------------------------------------------------------------

# utility: enum_class for a log level

from bibolamazi.core.bibfilter.argtypes import enum_class

LogLevel = enum_class('LogLevel',
                      [('CRITICAL', logging.CRITICAL),
                       ('ERROR', logging.ERROR),
                       ('WARNING', logging.WARNING),
                       ('INFO', logging.INFO),
                       ('DEBUG', logging.DEBUG),
                       ('LONGDEBUG', LONGDEBUG)],
                      default_value='INFO',
                      value_attr_name='levelno')
