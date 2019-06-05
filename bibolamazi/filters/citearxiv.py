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

import re
import os
import os.path
import io
from urllib.error import HTTPError
import logging
logger = logging.getLogger(__name__)

from pybtex.database import BibliographyData
import pybtex.database.input.bibtex as inputbibtex

from bibolamazi.core.bibfilter import BibFilter, BibFilterError
from bibolamazi.core.bibfilter.argtypes import CommaStrList
from bibolamazi.core.butils import getbool

import arxiv2bib
from .util import arxivutil

from .util import auxfile


HELP_AUTHOR = r"""
Philippe Faist, (C) 2013, GPL 3+
"""

HELP_DESC = r"""
Automatically collect bibtex entries from arxiv.org for citations of the form
\cite{1211.1037}
"""

HELP_TEXT = r"""
This filter scans a LaTeX document for citations of the form '\cite{arxiv-id}'
(i.e.  '\cite{XXXX.XXXX}', '\cite{XXXX.XXXXX}' or '\cite{quant-ph/XXXXXXX}'),
and adds the corresponding bibtex items in the combined bibtex database with the
arXiv ID as citation key. The bibtex entry is generated by querying the arXiv
API; you of course need internet access for this.

The citations are searched for in LaTeX document with the same base name as the
bibolamazi file.  For instance, if the bibolamazi file is called
"mydocument.bibolamazi.bib", we expect the LaTeX document to be in the same
directory and called "mydocument.tex".  If you would like to scan the citations
of a document that is named differently, you should provide the jobname (file
base name) of the LaTeX document using the -sJobname= option.

If the "mydocument.aux" file is in a different directory than the bibolamazi
file, you may specify where to look for the aux file with the option
'-sSearchDirs=...'.

If the option '-dJournalRefInNote' is provided, then the journal reference, as
returned by the arXiv query and if existing, is added in the 'note={}' field of
the bibtex entry.

"""



class CiteArxivFilter(BibFilter):

    helpauthor = HELP_AUTHOR
    helpdescription = HELP_DESC
    helptext = HELP_TEXT

    def __init__(self, jobname=None, search_dirs=[], prefix="", journal_ref_in_note=False):
        r"""
        CiteArxivFilter constructor.

        Arguments:

          - jobname: the base name of the latex file whose citations we should
              analyze. Will search for jobname.aux and look for '\citation{..}'
              commands as they are generated by latex.  The corresponding AUX
              file is searched for and analyzed.  If -sJobname is not specified,
              then the LaTeX file name is guessed from the bibolamazi file name,
              as for the only_used filter and the duplicates filter.

          - search_dirs(CommaStrList): the .aux file will be searched for in
              this list of directories; separate directories with commas
              e.g. 'path/to/dir1,path/to/dir2'.  Paths are absolute or relative
              to bibolamazi file.

          - journal_ref_in_note(bool): keep the journal reference given by the
              arXiv in the note={} bibtex field. (default: No)

          - prefix: if set, citations should be in the the form
              '\cite{prefix:id}' (default: no prefix)
        """

        super().__init__()

        self.jobname = jobname
        self.search_dirs = CommaStrList(search_dirs)
        self.journal_ref_in_note = getbool(journal_ref_in_note)
        self.prefix = prefix

        if not self.search_dirs:
            self.search_dirs = ['.', '_cleanlatexfiles'] # also for my cleanlatex utility :)

        logger.debug('citearxiv: jobname=%r' % (self.jobname,))


    def getRunningMessage(self):
        return "citearxiv: parsing & fetching relevant arxiv citations ..."

    
    def action(self):
        return BibFilter.BIB_FILTER_BIBOLAMAZIFILE

    def requested_cache_accessors(self):
        return [
            arxivutil.ArxivFetchedAPIInfoCacheAccessor
            ]

    def filter_bibolamazifile(self, bibolamazifile):

        arxiv_api_accessor = self.cacheAccessor(arxivutil.ArxivFetchedAPIInfoCacheAccessor)

        citearxiv_uselist = []

        #
        # find and analyze jobname.aux. Look for \citation{...}'s and collect them.
        #

        def add_to_cite_list(citekey):
            if self.prefix:
                if not citekey.startswith(self.prefix+":"):
                    return
                citekey = citekey[len(self.prefix)+1:]

            if (not arxiv2bib.NEW_STYLE.match(citekey) and
                not arxiv2bib.OLD_STYLE.match(citekey)):
                # this is not an arxiv citation key
                return

            # citekey is an arxiv ID
            arxivid = citekey
            if (arxivid not in citearxiv_uselist):
                citearxiv_uselist.append(arxivid)

        
        jobname = auxfile.get_action_jobname(self.jobname, bibolamazifile)

        auxfile.get_all_auxfile_citations(jobname, bibolamazifile,
                                          filtername=self.name(),
                                          search_dirs=self.search_dirs,
                                          return_set=False,
                                          callback=add_to_cite_list,
                                          )
        
        #
        # Now, fetch all bib entries that we need.
        #

        # if there are missing ids, fetch them
        if (citearxiv_uselist):
            arxiv_api_accessor.fetchArxivApiInfo(citearxiv_uselist)

        #
        # Now, include all the entries in citearxiv_uselist
        #
        # Variable bibdata is a pybtex.database.BibliographyData object
        #

        thebibdata = bibolamazifile.bibliographyData()


        addprefix = self.prefix+":" if self.prefix else ""

        for arxivid in citearxiv_uselist:
            dat = arxiv_api_accessor.getArxivApiInfo(arxivid)
            if (dat is None):
                errref = arxiv2bib.ReferenceErrorInfo("ArXiv info for `%s' not in cache"%(arxivid),
                                                      arxivid)
                dat = {
                    'reference': errref,
                    'bibtex': errref.bibtex(),
                    }

            # parse bibtex
            parser = inputbibtex.Parser()
            new_bib_data = None
            with io.StringIO(str(dat['bibtex'])) as stream:
                new_bib_data = parser.parse_stream(stream)
            
            # and add them to the main list
            if (len(new_bib_data.entries.keys()) != 1):
                logger.warning("Got more than one bibtex entry when retreiving `%s'!" %(arxivid))

            for val in new_bib_data.entries.values():
                if (not self.journal_ref_in_note and 'note' in val.fields):
                    del val.fields['note']
                thebibdata.add_entry(addprefix+arxivid, val)

        #
        # yay, done!
        #
        
        return


def bibolamazi_filter_class():
    return CiteArxivFilter

