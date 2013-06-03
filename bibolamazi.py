#!/usr/bin/env python

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


import os
import os.path
import sys


if sys.hexversion < 0x02070000:
    print "FATAL ERROR: Python 2.7 or later is required."
    exit(254);

    
# setup python path correctly first.
# ----------------------------------
thisdir = os.path.dirname(os.path.realpath(__file__));
sys.path += [thisdir,
             thisdir + '/3rdparty/pybtex'];


if __name__ == "__main__":
    try:

        # run main program
        import core.main
        
    except SystemExit:
        raise
    
    except:
        
        print
        print " -- ERROR --"
        print

        import traceback
        traceback.print_exc()

        # debugging post-mortem
        import pdb

        pdb.post_mortem();

