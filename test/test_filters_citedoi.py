# -*- coding: utf-8 -*-

import unittest
import logging
import tempfile
import os.path
import re
import shutil

from pybtex.database import Entry, Person, BibliographyData

from bibolamazi.core import blogger
from helpers import CustomAssertions
from bibolamazi.filters.citedoi import (CiteDoiFilter, DoiOrgFetchedInfoCacheAccessor)
from bibolamazi.core.bibolamazifile import BibolamaziFile

logger = logging.getLogger(__name__)


class TestWorks(unittest.TestCase, CustomAssertions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.maxDiff = None

    def test_fetch_basic_noprefix(self):

        bf = BibolamaziFile(create=True)
        bf.setEntries([])

        tmpdir = tempfile.mkdtemp()
        try:
            # create fake aux file in that temp dir
            with open(os.path.join(tmpdir, 'testjobname.aux'), 'w') as auxf:
                auxf.write(r"""
\citation{10.1103/PhysRev.76.749}
\citation{SomeOtherCitation2013_stuff,MoreCitations}
\citation{10.1147/rd.53.0183}
\citation{10.1147/rd.53.0183,10.1103/RevModPhys.20.367}
""")

            filt = CiteDoiFilter(jobname='testjobname', search_dirs=[tmpdir], prefix='')
            bf.registerFilterInstance(filt)

            filt.filter_bibolamazifile(bf)

            bibdata = bf.bibliographyData()
            self.assertTrue(len(bibdata.entries) == 3)
            self.assertTrue('10.1147/rd.53.0183' in bibdata.entries)
            self.assertTrue('10.1103/RevModPhys.20.367' in bibdata.entries)
            self.assertTrue('10.1103/PhysRev.76.749' in bibdata.entries)

            # see if the entries were populated correctly (probe these random parts:)
            Landauer = bibdata.entries['10.1147/rd.53.0183']
            self.assertTrue(len(Landauer.persons['author']) == 1 and
                            " ".join(Landauer.persons['author'][0].get_part('last')).strip().upper()
                            == 'LANDAUER')
            self.assertTrue(re.match(r'\s*Rev(iews)?[. ]*(of)?[. ]*Mod(ern)?[. ]*Phys(ics)?[. ]*$',
                                     bibdata.entries['10.1103/RevModPhys.20.367'].fields['journal']))

        finally:
            shutil.rmtree(tmpdir)

    def test_fetch_prefix(self):

        bf = BibolamaziFile(create=True)
        bf.setEntries([])

        tmpdir = tempfile.mkdtemp()
        try:
            # create fake aux file in that temp dir
            with open(os.path.join(tmpdir, 'testjobname.aux'), 'w') as auxf:
                auxf.write(r"""
\citation{doi:10.1103/PhysRev.76.749}
\citation{10.1080/09500340008244031}
\citation{SomeOtherCitation2013_stuff,And,MoreCitations}
\citation{doi:10.1147/rd.53.0183,More,10.1080/09500340008244031,Citations}
\citation{doi:10.1147/rd.53.0183,doi:10.1103/RevModPhys.20.367}
""") # don't pick up the ones without the prefix

            filt = CiteDoiFilter(jobname='testjobname', search_dirs=[tmpdir])
            bf.registerFilterInstance(filt)

            filt.filter_bibolamazifile(bf)

            bibdata = bf.bibliographyData()

            # logger.debug("All entries =\n%s", bibdata.to_string('bibtex'))

            self.assertTrue(len(bibdata.entries) == 3)
            self.assertTrue('doi:10.1147/rd.53.0183' in bibdata.entries)
            self.assertTrue('doi:10.1103/RevModPhys.20.367' in bibdata.entries)
            self.assertTrue('doi:10.1103/PhysRev.76.749' in bibdata.entries)

            # see if the entries were populated correctly (probe these random parts:)
            Landauer = bibdata.entries['doi:10.1147/rd.53.0183']
            self.assertTrue(len(Landauer.persons['author']) == 1 and
                            " ".join(Landauer.persons['author'][0].get_part('last')).strip().upper()
                            == 'LANDAUER')
            self.assertTrue(re.match(r'\s*Rev(iews)?[. ]*(of)?[. ]*Mod(ern)?[. ]*Phys(ics)?[. ]*$',
                                     bibdata.entries['doi:10.1103/RevModPhys.20.367'].fields['journal']))

        finally:
            shutil.rmtree(tmpdir)




if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=logging.DEBUG)
    unittest.main()
