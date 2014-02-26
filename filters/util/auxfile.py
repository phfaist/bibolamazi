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
import re

from core.bibfilter import BibFilter, BibFilterError;
from core.blogger import logger;



def get_all_auxfile_citations(jobname, bibolamazifile, filtername, search_dirs=None, callback=None, return_set=True):

    logger.debug("Retrieving citations from job name `%s'" %(jobname))

    citations_list = set()

    if (search_dirs is None):
        search_dirs = ['.', '_cleanlatexfiles']

    allaux = None
    for maybeauxfile in (os.path.join(bibolamazifile.fdir(), searchdir, jobname+'.aux')
                         for searchdir in search_dirs):
        try:
            with open(maybeauxfile, 'r') as auxf:
                allaux = auxf.read()
        except IOError:
            pass

    if (not allaux):
        raise BibFilterError(filtername, "Can't analyze citations: can't find `%s.aux'." %(jobname))

    #
    # parse allaux for \citation{...}
    #
    
    for citation in re.finditer(r'\\citation\{(?P<citekey>[^\}]+)\}', allaux):
        citekeys = (x.strip() for x in citation.group('citekey').split(','))
        if (return_set):
            for citekey in citekeys:
                citations_list.add(citekey)
        if (callback is not None):
            for citekey in citekeys:
                callback(citekey)

    if return_set:
        return citations_list

    return

