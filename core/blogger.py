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


# note: DEBUG=10, INFO=20, WARNING=30 etc.
LONGDEBUG = 5
logging.addLevelName(LONGDEBUG, "LONGDEBUG");

# DEBUG/LOGGING
# create logger
logger = logging.getLogger('bibolamazi');
def longdebug(l, msg, *args, **kwargs):
    l.log(LONGDEBUG, msg, *args, **kwargs);
    
logger.longdebug = MethodType(longdebug, logger, logging.Logger)
# create console handler
ch = logging.StreamHandler();
ch.setLevel(logging.DEBUG);
# create formatter and add it to the handlers
#formatter = logging.Formatter('%(name)s - %(asctime)-15s %(levelname)s: %(message)s');
formatter = logging.Formatter('%(message)s');
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

    l.longdebug("Set verbosity level to %d" %(value))


logger.setVerbosity = MethodType(_set_verbosity, logger, logging.Logger);
