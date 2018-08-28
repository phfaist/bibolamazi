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


# Py2/Py3 support
from __future__ import unicode_literals, print_function
from past.builtins import basestring
from future.utils import python_2_unicode_compatible, iteritems
from builtins import range
from builtins import str as unicodestr

import sys
import os
import os.path
import re
import logging
import subprocess
import datetime

#if sys.platform.startswith("win"):
#    # why do we need this??!??!?!
#    logging.basicConfig(level=logging.DEBUG)

import bibolamazi.init

# set up basic logging
from bibolamazi.core import blogger

from bibolamazi.core import bibolamazifile
#from bibolamazi.core import main as bibolamazi_main
from bibolamazi.core.butils import BibolamaziError
from bibolamazi.core.bibfilter import factory as filters_factory
from bibolamazi.core.bibfilter import argtypes
from bibolamazi.core import version as bibolamaziversion

# Important: Do not import Qt5 yet
#
# We need to set some environment variables, etc., to make sure Qt can find all
# its libraries and plugins well when using PyInstaller.



#print("Bibolamazi: loading main script")

logger = logging.getLogger(__name__)


def setup_qt5_plugins_path():
    try:
        basePath = sys._MEIPASS
    except Exception:
        return

    qt_platform_plugins_path = os.path.join(basePath, "PyQt5", "Qt", "plugins")

    logger.debug("Setting QT_QPA_PLATFORM_PLUGIN_PATH to %r", qt_platform_plugins_path)

    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_platform_plugins_path



def exception_handler(etype, evalue, tb):
    if etype is KeyboardInterrupt:
        print("*** interrupt (ignoring)")
        return

    import traceback
    logger.warning("Internal Error: Uncaught Python Exception. Ignoring and hoping for the best.\n%s",
                   "".join(traceback.format_exception(etype, evalue, tb)))

# override Python's exception handler, 
sys.excepthook = exception_handler




def main():

    blogger.setup_simple_console_logging(level=logging.DEBUG)

    argv = list(sys.argv)

    # default level: set to root logger.  May be set externally via environment variable
    # (e.g. for debugging) or with --verbose

    log_level = logging.INFO
    if '--verbose' in argv:
        argv.remove('--verbose')
        log_level = logging.DEBUG

    if 'BIBOLAMAZI_LOG_LEVEL' in os.environ and os.environ['BIBOLAMAZI_LOG_LEVEL']:
        logging.getLogger().setLevel(argtypes.LogLevel(os.environ['BIBOLAMAZI_LOG_LEVEL']).levelno)
    else:
        logging.getLogger().setLevel(log_level)

    logger.debug("main: log level set to %r", log_level)


    # setup Qt paths!
    setup_qt5_plugins_path()


    # ## Seems we still need this for pyinstaller, I'm not sure why....
    #
    # load precompiled filters, if we've got any
    try:
        import bibolamazi_compiled_filter_list as pc
        filters_factory.load_precompiled_filters('bibolamazi.filters', dict([
            (fname, pc.__dict__[fname])  for fname in pc.filter_list
            ]))
    except ImportError:
        pass


    from . import bibolamaziapp

    return bibolamaziapp.run_app(argv)


if __name__ == '__main__':

    main()
