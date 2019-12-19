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
from bibolamazi.filters.apply_patches import ApplyPatchesFilter
from bibolamazi.core.bibolamazifile import BibolamaziFile

logger = logging.getLogger(__name__)


class TestWorks(unittest.TestCase, CustomAssertions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.maxDiff = None

    def test_basic(self):
        entries = [
            ("Bennett1993PRL_Teleportation",
             Entry("article", persons={"author": [
                 Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),
                 Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")
             ],}, fields={
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "journal": "Physical Review Letters",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "title": "{Teleporting an unknown quantum state via dual classical and "
                          "Einstein-Podolsky-Rosen channels}",
                 "keywords": "unknown quantum state; quantum information theory",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bennett1993PRL_Teleportation.PATCH",
             Entry("misc", fields={
                 "!type": "unpublished",
                 "-doi": "",
                 "journal": "Phys. Rev. Lett.",
                 "+keywords": "quantum teleportation",
                 "+annote": "Original quantum teleportation paper",
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "journal": "Physics",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
        ]
        entries_ok = [
            ("Bennett1993PRL_Teleportation",
             Entry("unpublished", persons={"author": [
                 Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),
                 Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")
             ],}, fields={
                 "journal": "Phys. Rev. Lett.",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "title": "{Teleporting an unknown quantum state via dual classical and "
                          "Einstein-Podolsky-Rosen channels}",
                 "keywords": "unknown quantum state; quantum information theory; quantum teleportation",
                 "annote": "Original quantum teleportation paper",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "journal": "Physics",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
        ]

        bf = BibolamaziFile(create=True)
        bf.setEntries(entries)

        filt = ApplyPatchesFilter(add_value_separator="; ")
        bf.registerFilterInstance(filt)

        filt.filter_bibolamazifile(bf)

        self.assert_keyentrylists_equal(list(bf.bibliographyData().entries.items()),
                                        entries_ok, order=False)
        

    def test_patchseries(self):
        entries = [
            ("Bennett1993PRL_Teleportation",
             Entry("article", persons={"author": [
                 Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),
                 Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")
             ],}, fields={
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "journal": "Physical Review Letters",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "title": "{Teleporting an unknown quantum state via dual classical and "
                          "Einstein-Podolsky-Rosen channels}",
                 "keywords": "unknown quantum state, quantum information theory",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bennett1993PRL_Teleportation.PATCH",
             Entry("misc", fields={
                 "!type": "unpublished",
                 "-doi": "",
                 "journal": "Phys. Rev. Lett.",
                 "+keywords": "quantum teleportation",
                 "+annote": "Original quantum teleportation paper",
             },),),
            ("Bennett1993PRL_Teleportation.PATCH.asdfjkl",
             Entry("article", fields={
                 "!type": "incollection",
                 "-number": "",
                 "journal": "{{Phys. Rev. Lett.}}",
                 "+keywords": "quantum-teleportation",
                 "+annote": "THE ORIGINAL QUANTUM TELEPORTATION PAPER",
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "journal": "Physics",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
        ]
        entries_ok = [
            ("Bennett1993PRL_Teleportation",
             Entry("incollection", persons={"author": [
                 Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),
                 Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")
             ],}, fields={
                 "journal": "{{Phys. Rev. Lett.}}",
                 "month": "March",
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "pages": "1895--1899",
                 "title": "{Teleporting an unknown quantum state via dual classical and "
                          "Einstein-Podolsky-Rosen channels}",
                 "keywords": "unknown quantum state, quantum information theory, quantum-teleportation",
                 "annote": "THE ORIGINAL QUANTUM TELEPORTATION PAPER",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bennett1993PRL_Teleportation.PATCH",
             Entry("misc", fields={
                 "!type": "unpublished",
                 "-doi": "",
                 "journal": "Phys. Rev. Lett.",
                 "+keywords": "quantum teleportation",
                 "+annote": "Original quantum teleportation paper",
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "journal": "Physics",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
        ]

        bf = BibolamaziFile(create=True)
        bf.setEntries(entries)

        filt = ApplyPatchesFilter(patch_series="asdfjkl")
        bf.registerFilterInstance(filt)

        filt.filter_bibolamazifile(bf)

        self.assert_keyentrylists_equal(list(bf.bibliographyData().entries.items()),
                                        entries_ok, order=False)
        

    def test_from_file(self):
        entries = [
            ("Bennett1993PRL_Teleportation",
             Entry("article", persons={"author": [
                 Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),
                 Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")
             ],}, fields={
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "journal": "Physical Review Letters",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "title": "{Teleporting an unknown quantum state via dual classical and "
                          "Einstein-Podolsky-Rosen channels}",
                 "keywords": "unknown quantum state, quantum information theory",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bennett1993PRL_Teleportation.PATCH",
             Entry("misc", fields={
                 "!type": "unpublished",
                 "-doi": "",
                 "journal": "Phys. Rev. Lett.",
                 "+keywords": "quantum teleportation",
                 "+annote": "Original quantum teleportation paper",
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "journal": "Physics",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
        ]
        entries_ok = [
            ("Bennett1993PRL_Teleportation",
             Entry("incollection", persons={"author": [
                 Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),
                 Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")
             ],}, fields={
                 "journal": "{{Phys. Rev. Lett.}}",
                 "month": "March",
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "pages": "1895--1899",
                 "title": "{Teleporting an unknown quantum state via dual classical and "
                          "Einstein-Podolsky-Rosen channels}",
                 "keywords": "unknown quantum state, quantum information theory, quantum-teleportation",
                 "annote": "THE ORIGINAL QUANTUM TELEPORTATION PAPER",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bennett1993PRL_Teleportation.PATCH",
             Entry("misc", fields={
                 "!type": "unpublished",
                 "-doi": "",
                 "journal": "Phys. Rev. Lett.",
                 "+keywords": "quantum teleportation",
                 "+annote": "Original quantum teleportation paper",
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "journal": "Physics",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
        ]

        patch_file_entries = [
            ("Bennett1993PRL_Teleportation.PATCH",
             Entry("article", fields={
                 "!type": "incollection",
                 "-number": "",
                 "journal": "{{Phys. Rev. Lett.}}",
                 "+keywords": "quantum-teleportation",
                 "+annote": "THE ORIGINAL QUANTUM TELEPORTATION PAPER",
             },),),
            # entries that are not patches of the given patch series will be ignored
            ('Jacobson1995',
             Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                 "doi": "10.1103/PhysRevLett.75.1260",
                 "journal": "Physical Review Letters",
                 "month": "August",
                 "number": "7",
                 "pages": "1260--1263",
                 "title": "{Thermodynamics of Spacetime: The Einstein Equation of State}",
                 "volume": "75",
                 "year": "1995"
             },),),
            ("del2011thermodynamic.PATCH.otherpatchseries",
             Entry("article", fields={
                 "+publisher": "Nature Publishing Group"
             },),),
        ]

        bf = BibolamaziFile(create=True)
        bf.setEntries(entries)

        patchbibdata = BibliographyData()
        for k, e in patch_file_entries:
            e.key = k
            patchbibdata.entries[k] = e

        def fn_read_patches_from_file(patch_source_fname):
            self.assertEqual(os.path.basename(patch_source_fname), 'xyzabc_patches.bib')
            return patchbibdata

        filt = ApplyPatchesFilter(from_file="xyzabc_patches.bib")
        filt._read_patches_from_file = fn_read_patches_from_file
        bf.registerFilterInstance(filt)

        filt.filter_bibolamazifile(bf)

        self.assert_keyentrylists_equal(list(bf.bibliographyData().entries.items()),
                                        entries_ok, order=False)
        




if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=logging.DEBUG)
    unittest.main()
