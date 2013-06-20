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


import logging
from types import MethodType


class ConditionalFormatter(logging.Formatter):
    """A formatter class.

    Very much like logging.Formatter, except that different formats can be specified for
    different log levels.

    Specify the different formats to the constructor with keyword arguments. E.g.:
      ConditionalFormatter('%(message)s', DEBUG='DEBUG: %(message)s', INFO='just some info... %(message)s')
    This will use '%(message)s' as format for all messages except with level other thand DEBUG or INFO, for
    which their respective formats are used.
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
        s = fmt % record.__dict__
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






# note: DEBUG=10, INFO=20, WARNING=30 etc.
LONGDEBUG = 5
logging.addLevelName(LONGDEBUG, "LONGDEBUG");

# DEBUG/LOGGING
# create logger
logger = logging.getLogger('bibolamazi');

# add logger.longdebug() method
def longdebug(l, msg, *args, **kwargs):
    l.log(LONGDEBUG, msg, *args, **kwargs);
logger.longdebug = MethodType(longdebug, logger, logging.Logger)

# create console handler
ch = logging.StreamHandler();
ch.setLevel(logging.NOTSET); # propagate all messages

# create formatter and add it to the handlers

#formatter = logging.Formatter('%(name)s - %(asctime)-15s %(levelname)s: %(message)s');
formatter = ConditionalFormatter('%(message)s', LONGDEBUG='LONG DEBUG: %(message)s', WARNING='WARNING: %(message)s');
ch.setFormatter(formatter);
# add the handlers to the logger
logger.addHandler(ch);



def _set_verbosity(l, value):
    if (value == 0):
        l.setLevel(logging.ERROR);
    elif (value == 1):
        l.setLevel(logging.INFO);
    elif (value == 2):
        l.setLevel(logging.DEBUG);
    elif (value >= 3):
        l.setLevel(LONGDEBUG);
    else:
        raise ValueError("Bad verbosity level: %r" %(value))

    l.longdebug("set verbosity level to %d" %(value))


logger.setVerbosity = MethodType(_set_verbosity, logger, logging.Logger);
