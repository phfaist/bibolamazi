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



import logging;


# DEBUG/LOGGING
# create logger
logger = logging.getLogger('bibfilter');
logger.setLevel(logging.DEBUG);
# create console handler
ch = logging.StreamHandler();
ch.setLevel(logging.DEBUG);
# create formatter and add it to the handlers
#formatter = logging.Formatter('%(name)s - %(asctime)-15s %(levelname)s: %(message)s');
formatter = logging.Formatter('%(levelname)s: %(message)s');
ch.setFormatter(formatter);
# add the handlers to the logger
logger.addHandler(ch);



def _set_verbosity(value):
    if (value == 0):
        logger.setLevel(logging.ERROR);
    if (value == 1):
        logger.setLevel(logging.INFO);
    if (value >= 2):
        logger.setLevel(logging.DEBUG);

logger.setVerbosity = _set_verbosity;
