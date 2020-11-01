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
from bibolamazi.filters.citeinspirehep import CiteInspireHEPFilter
from bibolamazi.core.bibolamazifile import BibolamaziFile

logger = logging.getLogger(__name__)


class TestWorks(unittest.TestCase, CustomAssertions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.maxDiff = None

    def test_fetch_basic(self):

        bf = BibolamaziFile(create=True)
        bf.setEntries([])

        test_keys = [
            "inspire:Phys.Rev.+47+777",
            "inspire:1305.1258--WWgg",
            "inspire:10.1103/PhysRev.47.777",
            "inspire:1408.4546,inspire:10.1103/PhysRev.47.777--EPR-paper",
            "inspire:hep-th/0001001",
            "inspire:1408.4546",
            "inspire:Phys.Rev.D.+66+010001",
            "inspire:Hagiwara:2002fs",
            "inspire:Nakamura:2010zzi",
            "inspire:RX-1037",
            "inspire:1302.0378",
            "inspire:'tHooft:1972fi",
            "inspire:Camb.Monogr.Part.Phys.Nucl.Phys.Cosmol.+8+1",
        ]

        tmpdir = tempfile.mkdtemp()
        try:
            # create fake aux file in that temp dir
            with open(os.path.join(tmpdir, 'testjobname.aux'), 'w') as auxf:
                auxf.write("\n".join([
                    r"""\citation{%s}"""%(inspirekey)
                    for inspirekey in test_keys
                ]))

            filt = CiteInspireHEPFilter(jobname='testjobname', search_dirs=[tmpdir])
            bf.registerFilterInstance(filt)

            filt.filter_bibolamazifile(bf)

            bibdata = bf.bibliographyData()
            
            logger.debug("bibdata = %r", bibdata)

            self.assertEqual(len(bibdata.entries), len(test_keys))
            for keylist in test_keys:
                for key in keylist.split(','):
                    self.assertIn(key, bibdata.entries)

            # see if the entries were populated correctly (probe these random parts:)
            EPR = bibdata.entries['inspire:Phys.Rev.+47+777']
            self.assertTrue(len(EPR.persons['author']) == 3)
            self.assertEqual( [ " ".join(p.last_names) for p in EPR.persons['author'] ],
                              ["Einstein", "Podolsky", "Rosen"] )

            WWgg = bibdata.entries['inspire:1305.1258--WWgg']
            self.assertTrue(WWgg.fields['doi'] == '10.1103/PhysRevD.88.012005')

        finally:
            shutil.rmtree(tmpdir)




if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=logging.DEBUG)
    unittest.main()
