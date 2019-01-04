
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import unittest
import logging

from pybtex.database import Entry, Person, BibliographyData

from bibolamazi.core import blogger
from helpers import CustomAssertions
from bibolamazi.filters.util import arxivutil
from bibolamazi.filters.duplicates import DuplicatesFilter, DuplicatesEntryInfoCacheAccessor, normstr, getlast, fmtjournal
from bibolamazi.core.bibolamazifile import BibolamaziFile

logger = logging.getLogger(__name__)


class TestWorks(unittest.TestCase, CustomAssertions):

    def __init__(self, *args, **kwargs):
        super(TestWorks, self).__init__(*args, **kwargs)

        self.maxDiff = None

    def test_dupli_basic(self):

        entries = self.get_entries_set()
        entries_ok = self.get_entries_set_merged()

        bf = BibolamaziFile(create=True)
        bf.setEntries(entries)

        filt = DuplicatesFilter(merge_duplicates=True)
        bf.registerFilterInstance(filt)

        filt.filter_bibolamazifile(bf)

        self.assert_keyentrylists_equal(list(bf.bibliographyData().entries.items()), entries_ok, order=False)


    def test_compare_entries(self):

        # duplicates, despite different author spellings, journal abbreviation, and incomplete page numbers
        self._check_entries_are_seen_as_duplicates(
            ("del2011thermodynamic", Entry("article", persons={"author": [Person("Del Rio, L."),Person("{\\AA}berg, J."),Person("Renner, R."),Person("Dahlsten, O."),Person("Vedral, V.")],}, fields={
                "title": "The thermodynamic meaning of negative entropy",
                "journal": "Nature",
                "volume": "474",
                "number": "7349",
                "pages": "61--63",
                "year": "2011",
                "publisher": "Nature Publishing Group"
            },),),
            ("del2011thermodynamic2", Entry("article", persons={"author": [Person("L\\'\\i{}dia del Rio"),Person("Aaberg, J."),Person("Renner, R."),Person("Dahlsten, O."),Person("Vedral, V.")],}, fields={
                "title": "The Thermodynamic Meaning of Negative Entropy",
                "journal": "Nat.",
                "volume": "474",
                "number": "7349",
                "pages": "61",
                "year": "2011"
            },),),
        )

        # mismatching author lists -- not duplicates
        self._check_entries_are_NOT_seen_as_duplicates(
            ("del2011thermodynamic", Entry("article", persons={"author": [Person("Del Rio, L."),Person("{\\AA}berg, J."),Person("Renner, R."),Person("Dahlsten, O."),Person("Vedral, V."),Person("Author, Additional")],}, fields={
                "title": "The thermodynamic meaning of negative entropy",
                "journal": "Nature",
                "volume": "474",
                "number": "7349",
                "pages": "61--63",
                "year": "2011",
                "publisher": "Nature Publishing Group"
            },),),
            ("del2011thermodynamic2", Entry("article", persons={"author": [Person("L\\'\\i{}dia del Rio"),Person("Aberg, J."),Person("Renner, R."),Person("Dahlsten, O."),Person("Vedral, V.")],}, fields={
                "title": "The Thermodynamic Meaning of Negative Entropy",
                "journal": "Nat.",
                "volume": "474",
                "number": "7349",
                "pages": "61",
                "year": "2011"
            },),),
        )



    def _check_entries_are_NOT_seen_as_duplicates(self, akeyentry, bkeyentry):
        return self._check_entries_are_seen_as_duplicates(akeyentry, bkeyentry, inverse_check=True)

    def _check_entries_are_seen_as_duplicates(self, akeyentry, bkeyentry, inverse_check=False):

        keya, a = akeyentry
        keyb, b = bkeyentry

        filt = DuplicatesFilter()

        bf = BibolamaziFile(create=True)
        bf.setEntries([])

        filt = DuplicatesFilter(merge_duplicates=True)
        bf.registerFilterInstance(filt)

        arxivaccess = arxivutil.setup_and_get_arxiv_accessor(bf)
        dupl_entryinfo_cache_accessor = filt.cacheAccessor(DuplicatesEntryInfoCacheAccessor)

        dupl_entryinfo_cache_accessor.prepare_entry_cache(keya, a, arxivaccess)
        dupl_entryinfo_cache_accessor.prepare_entry_cache(keyb, b, arxivaccess)

        same, reason = filt.compare_entries(a, b,
                                            dupl_entryinfo_cache_accessor.get_entry_cache(keya),
                                            dupl_entryinfo_cache_accessor.get_entry_cache(keyb))
        msg = "Entries {} and {} are {}the same{}".format(keya, keyb, "NOT " if not same else "",
                                                          " because "+reason if not same else "")
        logger.debug(msg)

        if not inverse_check:
            self.assertTrue(same, msg=msg)
        else:
            self.assertFalse(same, msg=msg)
        

    # --------

    def get_entries_set(self):
        return [
            ('Jacobson1995',
             Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                 "abstract": "The Einstein equation is derived from the proportionality of entropy and the horizon area together with the fundamental relation $\\delta$Q = TdS. The key idea is to demand that this relation hold for all the local Rindler causal horizons through each spacetime point, with $\\delta$Q and T interpreted as the energy flux and Unruh temperature seen by an accelerated observer just inside the horizon. This requires that gravitational lensing by matter energy distorts the causal structure of spacetime so that the Einstein equation holds. Viewed in this way, the Einstein equation is an equation of state.",
                 "annote": "arxiv:gr-qc/9504004",
                 "doi": "10.1103/PhysRevLett.75.1260",
                 "issn": "0031-9007",
                 "journal": "Physical Review Letters",
                 "keywords": "entropic gravity,general relativity,gravity,thermo",
                 "mendeley-tags": "entropic gravity,general relativity,gravity,thermo",
                 "month": "August",
                 "number": "7",
                 "pages": "1260--1263",
                 "publisher": "American Physical Society",
                 "shorttitle": "Phys. Rev. Lett.",
                 "title": "{Thermodynamics of Spacetime: The Einstein Equation of State}",
                 "url": "http://link.aps.org/doi/10.1103/PhysRevLett.75.1260",
                 "volume": "75",
                 "year": "1995"
             },),),
            ("Bennett1993PRL_Teleportation",
             Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")],}, fields={
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "issn": "0031-9007",
                 "journal": "Physical Review Letters",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "publisher": "American Physical Society",
                 "title": "{Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels}",
                 "url": "http://link.aps.org/doi/10.1103/PhysRevLett.70.1895",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "issn": "0554-128X",
                "journal": "Physics",
                "keywords": "Bell's paper,EPR paradox,entanglement,hidden variables",
                "mendeley-tags": "Bell's paper,EPR paradox,entanglement,hidden variables",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
            ("Hawking1975", Entry("article", persons={"author": [Person("Hawking, S. W.")],}, fields={
                "doi": "10.1007/BF02345020",
                "issn": "0010-3616",
                "journal": "Communications In Mathematical Physics",
                "keywords": "black holes,hawking radiation,thermo",
                "mendeley-tags": "black holes,hawking radiation,thermo",
                "month": "August",
                "number": "3",
                "pages": "199--220",
                "title": "{Particle creation by black holes}",
                "url": "http://www.springerlink.com/index/10.1007/BF02345020",
                "volume": "43",
                "year": "1975"
            },),),
            ("Einstein1935_EPR", Entry("article", persons={"author": [Person("Einstein, Albert"),Person("Podolsky, Boris"),Person("Rosen, Nathan")],}, fields={
                "doi": "10.1103/PhysRev.47.777",
                "issn": "0031-899X",
                "journal": "Physical Review",
                "month": "May",
                "number": "10",
                "pages": "777--780",
                "publisher": "American Physical Society",
                "title": "{Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?}",
                "url": "http://link.aps.org/doi/10.1103/PhysRev.47.777",
                "volume": "47",
                "year": "1935"
            },),),
            ("Feynman1949PR_TheoryOfPositrons", Entry("article", persons={"author": [Person("Feynman, R.")],}, fields={
                "doi": "10.1103/PhysRev.76.749",
                "issn": "0031-899X",
                "journal": "Physical Review",
                "month": "September",
                "number": "6",
                "pages": "749--759",
                "publisher": "American Physical Society",
                "title": "{The Theory of Positrons}",
                "url": "http://link.aps.org/doi/10.1103/PhysRev.76.749",
                "volume": "76",
                "year": "1949"
            },),),
            ("Landauer1961_5392446Erasure", Entry("article", persons={"author": [Person("Landauer, Rolf")],}, fields={
                "doi": "10.1147/rd.53.0183",
                "issn": "0018-8646",
                "journal": "IBM Journal of Research and Development",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "July",
                "number": "3",
                "pages": "183--191",
                "title": "{Irreversibility and Heat Generation in the Computing Process}",
                "volume": "5",
                "year": "1961"
            },),),
            ("Shannon1948BSTJ", Entry("article", persons={"author": [Person("Shannon, Claude E.")],}, fields={
                "journal": "The Bell System Technical Journal",
                "month": "July",
                "pages": "379--423",
                "title": "{A Mathematical Theory of Communication}",
                "url": "http://cm.bell-labs.com/cm/ms/what/shannonday/paper.html",
                "volume": "27",
                "year": "1948"
            },),),
            ("Verlinde2011_entropic", Entry("article", persons={"author": [Person("Verlinde, Erik")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "1001.0785",
                "doi": "10.1007/JHEP04(2011)029",
                "eprint": "1001.0785",
                "file": ":home/........./Verlinde - 2011 - On the origin of gravity and the laws of Newton.pdf:pdf",
                "issn": "1029-8479",
                "journal": "Journal of High Energy Physics",
                "keywords": "black holes,entropic force,gravity",
                "mendeley-tags": "black holes,entropic force,gravity",
                "month": "April",
                "number": "4",
                "pages": "29",
                "title": "{On the origin of gravity and the laws of Newton}",
                "url": "http://link.springer.com/10.1007/JHEP04(2011)029",
                "volume": "2011",
                "year": "2011"
            },),),
            ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
                "abstract": "The heat generated by computations is not only an obstacle to circuit miniaturization but also a fundamental aspect of the relationship between information theory and thermodynamics. In principle, reversible operations may be performed at no energy cost; given that irreversible computations can always be decomposed into reversible operations followed by the erasure of data, the problem of calculating their energy cost is reduced to the study of erasure. Landauer's principle states that the erasure of data stored in a system has an inherent work cost and therefore dissipates heat. However, this consideration assumes that the information about the system to be erased is classical, and does not extend to the general case where an observer may have quantum information about the system to be erased, for instance by means of a quantum memory entangled with the system. Here we show that the standard formulation and implications of Landauer's principle are no longer valid in the presence of quantum information. Our main result is that the work cost of erasure is determined by the entropy of the system, conditioned on the quantum information an observer has about it. In other words, the more an observer knows about the system, the less it costs to erase it. This result gives a direct thermodynamic significance to conditional entropies, originally introduced in information theory. Furthermore, it provides new bounds on the heat generation of computations: because conditional entropies can become negative in the quantum case, an observer who is strongly correlated with a system may gain work while erasing it, thereby cooling the environment.",
                "archivePrefix": "arXiv",
                "arxivId": "1009.1630",
                "doi": "DOI 10.1038/nature10123",
                "eprint": "1009.1630",
                "file": ":home/................./del Rio et al. - 2011 - The thermodynamic meaning of negative entropy(2).pdf:pdf;:home/................./del Rio et al. - 2011 - The thermodynamic meaning of negative entropy.pdf:pdf",
                "issn": "1476-4687",
                "journal": "Nature",
                "keywords": "Quantum Physics,thermo",
                "mendeley-tags": "thermo",
                "month": "June",
                "number": "7349",
                "pages": "61--63",
                "publisher": "Nature Publishing Group, a division of Macmillan Publishers Limited. All Rights Reserved.",
                "shorttitle": "Nature",
                "title": "{The thermodynamic meaning of negative entropy}",
                "url": "http://dx.doi.org/10.1038/nature10123",
                "volume": "474",
                "year": "2011"
            },),),
            ("Aberg2013_worklike", Entry("article", persons={"author": [Person("{\AA}berg, Johan"),],}, fields={
                "abstract": "The work content of non-equilibrium systems in relation to a heat bath is often analysed in terms of expectation values of an underlying random work variable. However, when optimizing the expectation value of the extracted work, the resulting extraction process is subject to intrinsic fluctuations, uniquely determined by the Hamiltonian and the initial distribution of the system. These fluctuations can be of the same order as the expected work content per se, in which case the extracted energy is unpredictable, thus intuitively more heat-like than work-like. This raises the question of the 'truly' work-like energy that can be extracted. Here we consider an alternative that corresponds to an essentially fluctuation-free extraction. We show that this quantity can be expressed in terms of a one-shot relative entropy measure introduced in information theory. This suggests that the relations between information theory and statistical mechanics, as illustrated by concepts like Maxwell's demon, Szilard engines and Landauer's principle, extends to the single-shot regime.",
                "archivePrefix": "arXiv",
                "arxivId": "1110.6121",
                "doi": "10.1038/ncomms2712",
                "eprint": "1110.6121",
                "issn": "2041-1723",
                "journal": "Nature Communications",
                "keywords": "single-shot,thermo",
                "language": "en",
                "month": "jun",
                "pages": "1925",
                "publisher": "Nature Publishing Group",
                "title": "{Truly work-like work extraction via a single-shot analysis}",
                "volume": "4",
                "year": "2013",
            },),),
            ("Brandao2011arXiv", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Micha\u0142"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph M."),Person("Spekkens, Robert W.")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "eprint": "1111.3882",
                "keywords": "resource theory,thermo",
                "mendeley-tags": "resource theory,thermo",
                "month": "November",
                "pages": "12",
                "title": "{The Resource Theory of Quantum States Out of Thermal Equilibrium}",
                "url": "http://arxiv.org/abs/1111.3882",
                "year": "2011"
            },),),
            ("PerezGarcia2006", Entry("article", persons={"author": [Person("P\u00e9rez-Garc\u00eda, David"),Person("Wolf, Michael M."),Person("Petz, Denes"),Person("Ruskai, Mary Beth")],}, fields={
                "doi": "10.1063/1.2218675",
                "language": "en",
                "title": "{Contractivity of positive and trace preserving maps under $L_p$ norms}",
                "journal": "Journal of Mathematical Physics",
                "abstract": "We provide a complete picture of contractivity of trace preserving positive maps with respect to $p$-norms. We show that for $p>1$ contractivity holds in general if and only if the map is unital. When the domain is restricted to the traceless subspace of Hermitian matrices, then contractivity is shown to hold in the case of qubits for arbitrary $p\\geq 1$ and in the case of qutrits if and only if $p=1,\\infty$. In all non-contractive cases best possible bounds on the $p$-norms are derived.",
                "issn": "00222488",
                "mendeley-tags": "majorization,thermo",
                "number": "8",
                "month": "August",
                "volume": "47",
                "pages": "083506",
                "file": ":home/.............../P\u00e9rez-Garc\u00eda et al. - 2006 - Contractivity of positive and trace preserving maps under $L_p$ norms.pdf:pdf",
                "year": "2006",
                "keywords": "Hermitian matrices,majorization,thermo"
            },),),
            ("Janzing2006Habil", Entry("phdthesis", persons={"author": [Person("Janzing, Dominik")],}, fields={
                "abstract": "This work considers several hypothetical control processes on the nanoscopic level and show their analogy to computation processes. It shows that measuring certain types of quantum observables is such a complex task that every instrument that is able to perform it would necessarily be an extremely powerful computer. URL https://dx.doi.org/10.5445/KSP/1000005188",
                "address": "Karlsruhe",
                "doi": "10.5445/KSP/1000005188",
                "file": ":Mendeley/Janzing - 2006 - Computer science approach to quantum control.pdf:pdf",
                "isbn": "3-86644-083-9",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "publisher": "Universit\\\"{a}tsverlag Karlsruhe",
                "school": "Universit\u00e4t Karlsruhe",
                "title": "{Computer science approach to quantum control}",
                "type": "Habilitation",
                "url": "http://digbib.ubka.uni-karlsruhe.de/volltexte/1000005188",
                "year": "2006"
            },),),
            ("PhdRenner2005_SQKD", Entry("phdthesis", persons={"author": [Person("Renner, Renato")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "quant-ph/0512258",
                "eprint": "0512258",
                "primaryClass": "quant-ph",
                "school": "ETH Z\\\"{u}rich",
                "title": "{Security of Quantum Key Distribution}",
                "type": "Ph-D Thesis",
                "url": "http://arxiv.org/abs/quant-ph/0512258",
                "year": "2005"
            },),),
            ("Uhlmann1973_EdDMII", Entry("article", persons={"author": [Person("Uhlmann, Armin")],}, fields={
                "file": ":path/to/Mendeley/Uhlmann - 1973 - Endlich-dimensionale Dichtematrizen II.pdf:pdf",
                "journal": "Wiss. Z. Karl-Marx-Univ. Leipzig, Math.-Naturwiss.",
                "pages": "139--177",
                "title": "{Endlich-dimensionale Dichtematrizen II}",
                "url": "http://www.physik.uni-leipzig.de/$\\sim$uhlmann/papers.html",
                "volume": "22",
                "year": "1973",
                "language": "de"
            },),),
            ("Szilard1929ZeitschriftFuerPhysik", Entry("article", persons={"author": [Person("Szilard, Leo")],}, fields={
                "doi": "Doi:10.1007/BF01341281",
                "issn": "1434-6001",
                "journal": "Zeitschrift f\\\"{u}r Physik",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "November",
                "number": "11-12",
                "pages": "840--856",
                "publisher": "Springer Berlin / Heidelberg",
                "title": "{\\\"{U}ber die Entropieverminderung in einem thermodynamischen System bei Eingriffen intelligenter Wesen}",
                "url": "http://www.springerlink.com/index/10.1007/BF01341281",
                "note": "URL http://www.springerlink.com/index/10.1007/BF01341281",
                "volume": "53",
                "year": "1929",
                "language": "Deutsch"
            },),),
            ("Bennett1996PRA_MSEntglQECorr", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("DiVincenzo, David P."),Person("Smolin, John A."),Person("Wootters, William K.")],}, fields={
                "abstract": "Entanglement purification protocols (EPPs) and quantum error-correcting codes (QECCs) provide two ways of protecting quantum states from interaction with the environment. In an EPP, perfectly entangled pure states are extracted, with some yield D, from a mixed state M shared by two parties; with a QECC, an arbitrary quantum state |$\\xi$\u3009 can be transmitted at some rate Q through a noisy channel $\\chi$ without degradation. We prove that an EPP involving one-way classical communication and acting on mixed state M\\^{}($\\chi$) (obtained by sharing halves of Einstein-Podolsky-Rosen pairs through a channel $\\chi$) yields a QECC on $\\chi$ with rate Q=D, and vice versa. We compare the amount of entanglement E(M) required to prepare a mixed state M by local actions with the amounts D1(M) and D2(M) that can be locally distilled from it by EPPs using one- and two-way classical communication, respectively, and give an exact expression for E(M) when M is Bell diagonal. While EPPs require classical communication, QECCs do not, and we prove Q is not increased by adding one-way classical communication. However, both D and Q can be increased by adding two-way communication. We show that certain noisy quantum channels, for example a 50\\% depolarizing channel, can be used for reliable transmission of quantum states if two-way communication is available, but cannot be used if only one-way communication is available. We exhibit a family of codes based on universal hashing able to achieve an asymptotic Q (or D) of 1-S for simple noise models, where S is the error entropy. We also obtain a specific, simple 5-bit single-error-correcting quantum block code. We prove that iff a QECC results in high fidelity for the case of no error then the QECC can be recast into a form where the encoder is the matrix inverse of the decoder. \u00a9 1996 The American Physical Society.",
                "annote": "An annotation might go here; Preprint available at https://arXiv.org/abs/quant-ph/9604024",
                "archivePrefix": "arXiv",
                "arxivId": "quant-ph/9604024",
                "doi": "doi:10.1103/PhysRevA.54.3824",
                "eprint": "9604024",
                "file": ":path/to/Mendeley/Bennett et al. - 1996 - Mixed-state entanglement and quantum error correction.pdf:pdf",
                "issn": "1050-2947",
                "journal": "Physical Review A",
                "keywords": "entanglement,quantum error correction",
                "mendeley-tags": "entanglement,quantum error correction",
                "month": "November",
                "number": "5",
                "pages": "3824--3851",
                "primaryClass": "quant-ph",
                "publisher": "American Physical Society",
                "shorttitle": "Phys. Rev. A",
                "title": "Mixed-state entanglement and quantum error correction",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.54.3824",
                "volume": "54",
                "year": "1996"
            },),),
            ("Earman1999_ExorcistXIVp2", Entry("article", persons={"author": [Person("Earman, John"),Person("Norton, John D.")],}, fields={
                "doi": "10.1016/S1355-2198(98)00026-4",
                "issn": "13552198",
                "journal": "Studies In History and Philosophy of Science Part B: Studies In History and Philosophy of Modern Physics",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "March",
                "number": "1",
                "pages": "1--40",
                "title": "Exorcist XIV: The Wrath of Maxwell\u2019s Demon. Part II. From Szilard to Landauer and Beyond",
                "url": "http://linkinghub.elsevier.com/retrieve/pii/S1355219898000264",
                "volume": "30",
                "year": "1999"
            },),),
            ("Molmer1998PRA_reply", Entry("article", persons={"author": [Person("M{\\o}lmer, Klaus")],}, fields={
                "abstract": "We conjecture that optical coherences, i.e., quantum-mechanical coherences between states separated by Bohr frequencies in the optical regime, do not exist in optics experiments. We claim the exact vanishing of optical field amplitudes and atomic dipole expectation values, and we discuss the seemingly contradictory success of assigning finite values to such quantities in theoretical calculations. We show that our conjecture is not at variance with the observed interference between different light sources. The connection to the concept of spontaneous symmetry breaking and the identification of entangled states as pointer basis states is discussed.",
                "doi": "10.1103/PhysRevA.58.4247",
                "file": ":Users/philippe/ref/articles/Mendeley/M{\\o}lmer - 1998 - Reply to \u201cComment on \u2018Optical coherence A convenient fiction'\u201d.pdf:pdf",
                "issn": "1050-2947",
                "journal": "Physical Review A",
                "month": "nov",
                "number": "5",
                "pages": "4247--4247",
                "title": "Reply to ``Comment on `Optical coherence: A convenient fiction'''",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.58.4247",
                "volume": "58",
                "year": "1998"
            },),),
            ("gour_measuring_2009", Entry("article", persons={"author": [Person("Gour, Gilad"),Person("Marvian, Iman"),Person("Spekkens, Robert W.")],}, fields={
                "title": "Measuring the quality of a quantum reference frame: The relative entropy of frameness",
                "volume": "80",
                "shorttitle": "Measuring the quality of a quantum reference frame",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.80.012307",
                "doi": "10.1103/PhysRevA.80.012307",
                "abstract": "In the absence of a reference frame for transformations associated with group G, any quantum state that is noninvariant under the action of G may serve as a token of the missing reference frame. We here present a measure of the quality of such a token: the relative entropy of frameness. This is defined as the relative entropy distance between the state of interest and the nearest G-invariant state. Unlike the relative entropy of entanglement, this quantity is straightforward to calculate, and we find it to be precisely equal to the G-asymmetry, a measure of frameness introduced by Vaccaro et al. It is shown to provide an upper bound on the mutual information between the group element encoded into the token and the group element that may be extracted from it by measurement. In this sense, it quantifies the extent to which the token successfully simulates a full reference frame. We also show that despite a suggestive analogy from entanglement theory, the regularized relative entropy of frameness is zero and therefore does not quantify the rate of interconversion between the token and some standard form of quantum reference frame. Finally, we show how these investigations yield an approach to bounding the relative entropy of entanglement.",
                "number": "1",
                "journal": "Physical Review A",
                "month": "July",
                "year": "2009",
                "pages": "012307"
            },),),
            # test with typo:
            ("aberg_2013_worklike", Entry("article", persons={"author": [Person("Aaberg, J.")],}, fields={
                "title": "Truly work-like work extraction via a single-shot analysis.",
                "journal": "Nature communications",
                "volume": "4",
                "pages": "1925",
                "year": "2013"
            },),),
            ("gour_measuring_2009_dupl", Entry("article", persons={"author": [Person("Gour, Gilad"),Person("Marvian, Iman"),Person("Spekkens, Robert W.")],}, fields={
                "title": "Measuring the quality of a quantum reference frame: The relative entropy of frameness",
                "volume": "80",
                "shorttitle": "Measuring the quality of a quantum reference frame",
                "number": "1",
                "journal": "PRA",
                "month": "July",
                "year": "2009",
                "pages": "012307"
            },),),
            ("aberg_2009_cumul", Entry("article", persons={"author": [Person("\\AA{}berg, Johan"),Person("Mitchison, Graeme")],}, fields={
                "journal": "Journal of Mathematical Physics",
                "month": "April",
                "number": "4",
                "pages": "042103",
                "publisher": "AIP Publishing",
                "title": "{Cumulants and the moment algebra: Tools for analyzing weak measurements}",
                "volume": "50",
                "year": "2009"
            },),),
            ("BBPS1996", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Bernstein, Herbert J."),Person("Popescu, Sandu"),Person("Schumacher, Benjamin")],}, fields={
                "title": "Concentrating Partial Entanglement by Local Operations",
                "journal": "Phys. Rev. A",
                "year": "1996",
                "volume": "53",
                "pages": "2046-2052",
                "eprint": "quant-ph/9511030",
                "doi": "10.1103/PhysRevA.53.2046"
            },),),
            ("BBPSSW1996", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Popescu, Sandu"),Person("Schumacher, Benjamin"),Person("Smolin, John A."),Person("Wootters, William K.")],}, fields={
                "title": "Purification of noisy entanglement and faithful teleportation via noisy channels",
                "journal": "Phys. Rev. Lett.",
                "year": "1996",
                "volume": "76",
                "pages": "722--725",
                "eprint": "quant-ph/9511027",
                "doi": "10.1103/PhysRevLett.76.722"
            },),),
            ("BDSW1996", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("DiVincenzo, David P."),Person("Smolin, John A."),Person("Wootters, William K.")],}, fields={
                "title": "Mixed-state entanglement and quantum error correction",
                "journal": "Phys. Rev. A",
                "year": "1996",
                "volume": "54",
                "pages": "3824--3851",
                "eprint": "quant-ph/9604024",
                "doi": "10.1103/PhysRevA.54.3824"
            },),),
            ("VidalC-irre", Entry("article", persons={"author": [Person("Vidal, G."),Person("Cirac, J. I.")],}, fields={
                "title": "Irreversibility in asymptotic manipulations of entanglement",
                "journal": "Phys. Rev. Lett.",
                "year": "2001",
                "volume": "86",
                "pages": "5803--5806",
                "eprint": "quant-ph/0102036",
                "doi": "10.1103/PhysRevLett.86.5803"
            },),),
            ("linden2010small", Entry("article", persons={"author": [Person("Linden, N."),Person("Popescu, S."),Person("Skrzypczyk, P.")],}, fields={
                "title": "How small can thermal machines be? The smallest possible refrigerator",
                "journal": "Physical Review Letters",
                "volume": "105",
                "number": "13",
                "pages": "130401",
                "year": "2010",
                "publisher": "APS"
            },),),
            ("del2011thermodynamic", Entry("article", persons={"author": [Person("Del Rio, L."),Person("{\\AA}berg, J."),Person("Renner, R."),Person("Dahlsten, O."),Person("Vedral, V.")],}, fields={
                "title": "The thermodynamic meaning of negative entropy",
                "journal": "Nature",
                "volume": "474",
                "number": "7349",
                "pages": "61--63",
                "year": "2011",
                "publisher": "Nature Publishing Group"
            },),),
            ("dahlsten2011inadequacy", Entry("article", persons={"author": [Person("Dahlsten, O.C.O."),Person("Renner, R."),Person("Rieper, E."),Person("Vedral, V.")],}, fields={
                "title": "Inadequacy of von Neumann entropy for characterizing extractable work",
                "journal": "New Journal of Physics",
                "volume": "13",
                "pages": "053015",
                "year": "2011",
                "publisher": "IOP Publishing"
            },),),
            ("horodecki_are_2002", Entry("article", persons={"author": [Person("Horodecki, {Micha\\l}"),Person("Oppenheim, Jonathan"),Person("Horodecki, Ryszard")],}, fields={
                "title": "Are the Laws of Entanglement Theory Thermodynamical?",
                "volume": "89",
                "url": "http://link.aps.org/doi/10.1103/PhysRevLett.89.240403",
                "doi": "10.1103/PhysRevLett.89.240403",
                "abstract": "We argue that on its face, entanglement theory satisfies laws equivalent to thermodynamics if the theory can be made reversible by adding certain bound entangled states as a free resource during entanglement manipulation. Subject to plausible conjectures, we prove that this is not the case in general, and discuss the implications of this for the thermodynamics of entanglement.",
                "number": "24",
                "journal": "Physical Review Letters",
                "month": "November",
                "year": "2002",
                "pages": "240403"
            },),),
            ("linden_reversibility_2005", Entry("article", persons={"author": [Person("Linden, Noah"),Person("Popescu, Sandu"),Person("Schumacher, Benjamin"),Person("Westmoreland, Michael")],}, fields={
                "title": "Reversibility of Local Transformations of Multiparticle Entanglement",
                "volume": "4",
                "url": "http://www.springerlink.com/content/hjvh868467m04122/",
                "doi": "10.1007/s11128-005-4608-0",
                "abstract": "We consider the transformation of multisystem entangled states by local quantum operations and classical communication. We show that, for any reversible transformation, the relative entropy of entanglement for any two parties must remain constant. This shows, for example, that it is not possible to convert {2N} three-party {GHZ} states into {3N} singlets, even in an asymptotic sense. Thus there is true three-party non-locality (i.e. not all three party entanglement is equivalent to two-party entanglement). Our results also allow us to make quantitative. statements about concentrating multi-particle entanglement. Finally, we show that there is true n-party entanglement for any n.",
                "number": "3",
                "journal": "Quantum Information Processing",
                "month": "August",
                "year": "2005",
                "pages": "241--250"
            },),),
            ("synak-radtke_asymptotic_2006", Entry("article", persons={"author": [Person("{Synak-Radtke}, Barbara"),Person("Horodecki, Michal")],}, fields={
                "title": "On asymptotic continuity of functions of quantum states",
                "volume": "39",
                "url": "http://iopscience.iop.org/0305-4470/39/26/L02/",
                "doi": "10.1088/0305-4470/39/26/L02",
                "number": "26",
                "journal": "Journal of a Physics A: Mathematical and General",
                "month": "June",
                "year": "2006",
                "pages": "L423"
            },),),
            ("Brandao2013_secondlaws", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Micha\u0142"),Person("Ng, Nelly Huei Ying"),Person("Oppenheim, Jonathan"),Person("Wehner, Stephanie")],}, fields={
                "abstract": "The second law of thermodynamics tells us which state transformations are so statistically unlikely that they are effectively forbidden. Its original formulation, due to Clausius, states that \"Heat can never pass from a colder to a warmer body without some other change, connected therewith, occurring at the same time.\" The second law applies to systems composed of many particles, however, we are seeing that one can make sense of thermodynamics in the regime where we only have a small number of particles interacting with a heat bath, or when we have highly correlated systems and wish to make non-statistical statements about them. Is there a second law of thermodynamics in this regime? Here, we find that for processes which are cyclic or very close to cyclic, the second law for microscopic or highly correlated systems takes on a very different form than it does at the macroscopic scale, imposing not just one constraint on what state transformations are possible, but an entire family of constraints. In particular, we find that the Renyi relative entropy distances to the equilibrium state can never increase. We further find that there are three regimes which govern which family of second laws govern state transitions, depending on how cyclic the process is. In one regime one can cause an apparent violation of the usual second law, through a process of embezzling work from a large system which remains arbitrarily close to its original state.",
                "archivePrefix": "arXiv",
                "arxivId": "1305.5278",
                "eprint": "1305.5278",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "May",
                "title": "{The second laws of quantum thermodynamics}",
                "url": "http://arxiv.org/abs/1305.5278",
                "year": "2013"
            },),),
            ("Brandao2012_exponential", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Michal")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "1206.2947",
                "eprint": "1206.2947",
                "month": "June",
                "title": "{Exponential Decay of Correlations Implies Area Law}",
                "url": "http://arxiv.org/abs/1206.2947",
                "year": "2012"
            },),),
            ("Brandao2013_resource", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando"),Person("Horodecki, Micha\u0142"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph"),Person("Spekkens, Robert")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "doi": "10.1103/PhysRevLett.111.250404",
                "eprint": "1111.3882",
                "file": ":home/pfaist/ref/articles/Mendeley/Brand\\~{a}o et al. - 2013 - Resource Theory of Quantum States Out of Thermal Equilibrium.pdf:pdf",
                "issn": "0031-9007",
                "journal": "Physical Review Letters",
                "keywords": "resource theory,thermo",
                "mendeley-tags": "resource theory,thermo",
                "month": "December",
                "number": "25",
                "pages": "250404",
                "title": "{Resource Theory of Quantum States Out of Thermal Equilibrium}",
                "url": "http://link.aps.org/doi/10.1103/PhysRevLett.111.250404",
                "volume": "111",
                "year": "2013"
            },),),
            ("Brandao2012_local", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Harrow, Aram W."),Person("Horodecki, Michal")],}, fields={
                "abstract": "We prove that local random quantum circuits acting on n qubits composed of polynomially many nearest neighbor two-qubit gates form an approximate unitary poly(n)-design. Previously it was unknown whether random quantum circuits were a t-design for any t > 3. The proof is based on an interplay of techniques from quantum many-body theory, representation theory, and the theory of Markov chains. In particular we employ a result of Nachtergaele for lower bounding the spectral gap of quantum local Hamiltonians; a quasi-orthogonality property of permutation matrices; a result of Oliveira which extends to the unitary group the path-coupling method for bounding the mixing time of random walks; and a result of Bourgain and Gamburd showing that dense subgroups of the special unitary group, composed of elements with algebraic entries, are infinity-copy tensor-product expanders. We also consider pseudo-randomness properties of local random quantum circuits of small depth and prove they constitute a quantum poly(n)-copy tensor-product expander. The proof also rests on techniques from quantum many-body theory, in particular on the detectability lemma of Aharonov et al. We give three applications of the results. First we show that almost every circuit U of size n\\^{}k on n qubits cannot be distinguished from a Haar uniform unitary by circuits of size n\\^{}[(k+3)/6] that are given oracle access to U; this provides a data-hiding scheme against computationally bounded adversaries. Second we reconsider a recent argument of Masanes et al concerning local equilibration of time-evolving quantum systems, and strengthen the connection between fast equilibration of small subsystems and the circuit complexity of the Hamiltonian. Third we show that in one dimension almost every parallel local circuit of linear depth generates topological order, matching an upper bound to the problem due to Bravyi et al.",
                "archivePrefix": "arXiv",
                "arxivId": "1208.0692",
                "eprint": "1208.0692",
                "month": "August",
                "pages": "36",
                "title": "{Local random quantum circuits are approximate polynomial-designs}",
                "url": "http://arxiv.org/abs/1208.0692",
                "year": "2012"
            },),),
            ("2015PNAS..112.3275B", Entry("article", persons={"author": [Person("{Brand{\\~a}o}, F."),Person("{Horodecki}, M."),Person("{Ng}, N."),Person("{Oppenheim}, J."),Person("{Wehner}, S.")],}, fields={
                "title": "{The second laws of quantum thermodynamics}",
                "journal": "Proceedings of the National Academy of Science",
                "archivePrefix": "arXiv",
                "eprint": "1305.5278",
                "primaryClass": "quant-ph",
                "year": "2015",
                "month": "March",
                "volume": "112",
                "pages": "3275-3279",
                "doi": "10.1073/pnas.1411728112",
                "adsurl": "http://adsabs.harvard.edu/abs/2015PNAS..112.3275B",
                "adsnote": "Provided by the SAO/NASA Astrophysics Data System"
            },),),
            ("brandao_2011-arxiv-2ndlaws", Entry("article", persons={"author": [Person("Brandao, F."),Person("{Horodecki}, M."),Person("{Ng}, N."),Person("{Oppenheim}, J."),Person("Wehner, S.")],}, fields={
                "title": "{The second laws of quantum thermodynamics}",
                "journal": "Proceedings of the National Academy of Science",
                "archivePrefix": "arXiv",
                "eprint": "1305.5278",
                "primaryClass": "quant-ph",
                "year": "2013",
                "month": "March"
            },),),
        ]

    def get_entries_set_merged(self):
        return [
            ('Jacobson1995',
             Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                 "abstract": "The Einstein equation is derived from the proportionality of entropy and the horizon area together with the fundamental relation $\\delta$Q = TdS. The key idea is to demand that this relation hold for all the local Rindler causal horizons through each spacetime point, with $\\delta$Q and T interpreted as the energy flux and Unruh temperature seen by an accelerated observer just inside the horizon. This requires that gravitational lensing by matter energy distorts the causal structure of spacetime so that the Einstein equation holds. Viewed in this way, the Einstein equation is an equation of state.",
                 "annote": "arxiv:gr-qc/9504004",
                 "doi": "10.1103/PhysRevLett.75.1260",
                 "issn": "0031-9007",
                 "journal": "Physical Review Letters",
                 "keywords": "entropic gravity,general relativity,gravity,thermo",
                 "mendeley-tags": "entropic gravity,general relativity,gravity,thermo",
                 "month": "August",
                 "number": "7",
                 "pages": "1260--1263",
                 "publisher": "American Physical Society",
                 "shorttitle": "Phys. Rev. Lett.",
                 "title": "{Thermodynamics of Spacetime: The Einstein Equation of State}",
                 "url": "http://link.aps.org/doi/10.1103/PhysRevLett.75.1260",
                 "volume": "75",
                 "year": "1995"
             },),),
            ("Bennett1993PRL_Teleportation",
             Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr\u00e9peau, Claude"),Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")],}, fields={
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "issn": "0031-9007",
                 "journal": "Physical Review Letters",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "publisher": "American Physical Society",
                 "title": "{Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels}",
                 "url": "http://link.aps.org/doi/10.1103/PhysRevLett.70.1895",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "issn": "0554-128X",
                "journal": "Physics",
                "keywords": "Bell's paper,EPR paradox,entanglement,hidden variables",
                "mendeley-tags": "Bell's paper,EPR paradox,entanglement,hidden variables",
                "pages": "195",
                "publisher": "Physics Publishing Company",
                "title": "{On the Einstein-Podolsky-Rosen paradox}",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
            ("Hawking1975", Entry("article", persons={"author": [Person("Hawking, S. W.")],}, fields={
                "doi": "10.1007/BF02345020",
                "issn": "0010-3616",
                "journal": "Communications In Mathematical Physics",
                "keywords": "black holes,hawking radiation,thermo",
                "mendeley-tags": "black holes,hawking radiation,thermo",
                "month": "August",
                "number": "3",
                "pages": "199--220",
                "title": "{Particle creation by black holes}",
                "url": "http://www.springerlink.com/index/10.1007/BF02345020",
                "volume": "43",
                "year": "1975"
            },),),
            ("Einstein1935_EPR", Entry("article", persons={"author": [Person("Einstein, Albert"),Person("Podolsky, Boris"),Person("Rosen, Nathan")],}, fields={
                "doi": "10.1103/PhysRev.47.777",
                "issn": "0031-899X",
                "journal": "Physical Review",
                "month": "May",
                "number": "10",
                "pages": "777--780",
                "publisher": "American Physical Society",
                "title": "{Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?}",
                "url": "http://link.aps.org/doi/10.1103/PhysRev.47.777",
                "volume": "47",
                "year": "1935"
            },),),
            ("Feynman1949PR_TheoryOfPositrons", Entry("article", persons={"author": [Person("Feynman, R.")],}, fields={
                "doi": "10.1103/PhysRev.76.749",
                "issn": "0031-899X",
                "journal": "Physical Review",
                "month": "September",
                "number": "6",
                "pages": "749--759",
                "publisher": "American Physical Society",
                "title": "{The Theory of Positrons}",
                "url": "http://link.aps.org/doi/10.1103/PhysRev.76.749",
                "volume": "76",
                "year": "1949"
            },),),
            ("Landauer1961_5392446Erasure", Entry("article", persons={"author": [Person("Landauer, Rolf")],}, fields={
                "doi": "10.1147/rd.53.0183",
                "issn": "0018-8646",
                "journal": "IBM Journal of Research and Development",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "July",
                "number": "3",
                "pages": "183--191",
                "title": "{Irreversibility and Heat Generation in the Computing Process}",
                "volume": "5",
                "year": "1961"
            },),),
            ("Shannon1948BSTJ", Entry("article", persons={"author": [Person("Shannon, Claude E.")],}, fields={
                "journal": "The Bell System Technical Journal",
                "month": "July",
                "pages": "379--423",
                "title": "{A Mathematical Theory of Communication}",
                "url": "http://cm.bell-labs.com/cm/ms/what/shannonday/paper.html",
                "volume": "27",
                "year": "1948"
            },),),
            ("Verlinde2011_entropic", Entry("article", persons={"author": [Person("Verlinde, Erik")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "1001.0785",
                "doi": "10.1007/JHEP04(2011)029",
                "eprint": "1001.0785",
                "file": ":home/........./Verlinde - 2011 - On the origin of gravity and the laws of Newton.pdf:pdf",
                "issn": "1029-8479",
                "journal": "Journal of High Energy Physics",
                "keywords": "black holes,entropic force,gravity",
                "mendeley-tags": "black holes,entropic force,gravity",
                "month": "April",
                "number": "4",
                "pages": "29",
                "title": "{On the origin of gravity and the laws of Newton}",
                "url": "http://link.springer.com/10.1007/JHEP04(2011)029",
                "volume": "2011",
                "year": "2011"
            },),),
            ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
                "abstract": "The heat generated by computations is not only an obstacle to circuit miniaturization but also a fundamental aspect of the relationship between information theory and thermodynamics. In principle, reversible operations may be performed at no energy cost; given that irreversible computations can always be decomposed into reversible operations followed by the erasure of data, the problem of calculating their energy cost is reduced to the study of erasure. Landauer's principle states that the erasure of data stored in a system has an inherent work cost and therefore dissipates heat. However, this consideration assumes that the information about the system to be erased is classical, and does not extend to the general case where an observer may have quantum information about the system to be erased, for instance by means of a quantum memory entangled with the system. Here we show that the standard formulation and implications of Landauer's principle are no longer valid in the presence of quantum information. Our main result is that the work cost of erasure is determined by the entropy of the system, conditioned on the quantum information an observer has about it. In other words, the more an observer knows about the system, the less it costs to erase it. This result gives a direct thermodynamic significance to conditional entropies, originally introduced in information theory. Furthermore, it provides new bounds on the heat generation of computations: because conditional entropies can become negative in the quantum case, an observer who is strongly correlated with a system may gain work while erasing it, thereby cooling the environment.",
                "archivePrefix": "arXiv",
                "arxivId": "1009.1630",
                "doi": "DOI 10.1038/nature10123",
                "eprint": "1009.1630",
                "file": ":home/................./del Rio et al. - 2011 - The thermodynamic meaning of negative entropy(2).pdf:pdf;:home/................./del Rio et al. - 2011 - The thermodynamic meaning of negative entropy.pdf:pdf",
                "issn": "1476-4687",
                "journal": "Nature",
                "keywords": "Quantum Physics,thermo",
                "mendeley-tags": "thermo",
                "month": "June",
                "number": "7349",
                "pages": "61--63",
                "publisher": "Nature Publishing Group, a division of Macmillan Publishers Limited. All Rights Reserved.",
                "shorttitle": "Nature",
                "title": "{The thermodynamic meaning of negative entropy}",
                "url": "http://dx.doi.org/10.1038/nature10123",
                "volume": "474",
                "year": "2011"
            },),),
            ("Aberg2013_worklike", Entry("article", persons={"author": [Person("{\AA}berg, Johan"),],}, fields={
                "abstract": "The work content of non-equilibrium systems in relation to a heat bath is often analysed in terms of expectation values of an underlying random work variable. However, when optimizing the expectation value of the extracted work, the resulting extraction process is subject to intrinsic fluctuations, uniquely determined by the Hamiltonian and the initial distribution of the system. These fluctuations can be of the same order as the expected work content per se, in which case the extracted energy is unpredictable, thus intuitively more heat-like than work-like. This raises the question of the 'truly' work-like energy that can be extracted. Here we consider an alternative that corresponds to an essentially fluctuation-free extraction. We show that this quantity can be expressed in terms of a one-shot relative entropy measure introduced in information theory. This suggests that the relations between information theory and statistical mechanics, as illustrated by concepts like Maxwell's demon, Szilard engines and Landauer's principle, extends to the single-shot regime.",
                "archivePrefix": "arXiv",
                "arxivId": "1110.6121",
                "doi": "10.1038/ncomms2712",
                "eprint": "1110.6121",
                "issn": "2041-1723",
                "journal": "Nature Communications",
                "keywords": "single-shot,thermo",
                "language": "en",
                "month": "jun",
                "pages": "1925",
                "publisher": "Nature Publishing Group",
                "title": "{Truly work-like work extraction via a single-shot analysis}",
                "volume": "4",
                "year": "2013",
            },),),
            ("Brandao2011arXiv", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Micha\u0142"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph M."),Person("Spekkens, Robert W.")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "eprint": "1111.3882",
                "keywords": "resource theory,thermo",
                "mendeley-tags": "resource theory,thermo",
                "month": "November",
                "pages": "12",
                "title": "{The Resource Theory of Quantum States Out of Thermal Equilibrium}",
                "url": "http://arxiv.org/abs/1111.3882",
                "year": "2011"
            },),),
            ("PerezGarcia2006", Entry("article", persons={"author": [Person("P\u00e9rez-Garc\u00eda, David"),Person("Wolf, Michael M."),Person("Petz, Denes"),Person("Ruskai, Mary Beth")],}, fields={
                "doi": "10.1063/1.2218675",
                "language": "en",
                "title": "{Contractivity of positive and trace preserving maps under $L_p$ norms}",
                "journal": "Journal of Mathematical Physics",
                "abstract": "We provide a complete picture of contractivity of trace preserving positive maps with respect to $p$-norms. We show that for $p>1$ contractivity holds in general if and only if the map is unital. When the domain is restricted to the traceless subspace of Hermitian matrices, then contractivity is shown to hold in the case of qubits for arbitrary $p\\geq 1$ and in the case of qutrits if and only if $p=1,\\infty$. In all non-contractive cases best possible bounds on the $p$-norms are derived.",
                "issn": "00222488",
                "mendeley-tags": "majorization,thermo",
                "number": "8",
                "month": "August",
                "volume": "47",
                "pages": "083506",
                "file": ":home/.............../P\u00e9rez-Garc\u00eda et al. - 2006 - Contractivity of positive and trace preserving maps under $L_p$ norms.pdf:pdf",
                "year": "2006",
                "keywords": "Hermitian matrices,majorization,thermo"
            },),),
            ("Janzing2006Habil", Entry("phdthesis", persons={"author": [Person("Janzing, Dominik")],}, fields={
                "abstract": "This work considers several hypothetical control processes on the nanoscopic level and show their analogy to computation processes. It shows that measuring certain types of quantum observables is such a complex task that every instrument that is able to perform it would necessarily be an extremely powerful computer. URL https://dx.doi.org/10.5445/KSP/1000005188",
                "address": "Karlsruhe",
                "doi": "10.5445/KSP/1000005188",
                "file": ":Mendeley/Janzing - 2006 - Computer science approach to quantum control.pdf:pdf",
                "isbn": "3-86644-083-9",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "publisher": "Universit\\\"{a}tsverlag Karlsruhe",
                "school": "Universit\u00e4t Karlsruhe",
                "title": "{Computer science approach to quantum control}",
                "type": "Habilitation",
                "url": "http://digbib.ubka.uni-karlsruhe.de/volltexte/1000005188",
                "year": "2006"
            },),),
            ("PhdRenner2005_SQKD", Entry("phdthesis", persons={"author": [Person("Renner, Renato")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "quant-ph/0512258",
                "eprint": "0512258",
                "primaryClass": "quant-ph",
                "school": "ETH Z\\\"{u}rich",
                "title": "{Security of Quantum Key Distribution}",
                "type": "Ph-D Thesis",
                "url": "http://arxiv.org/abs/quant-ph/0512258",
                "year": "2005"
            },),),
            ("Uhlmann1973_EdDMII", Entry("article", persons={"author": [Person("Uhlmann, Armin")],}, fields={
                "file": ":path/to/Mendeley/Uhlmann - 1973 - Endlich-dimensionale Dichtematrizen II.pdf:pdf",
                "journal": "Wiss. Z. Karl-Marx-Univ. Leipzig, Math.-Naturwiss.",
                "pages": "139--177",
                "title": "{Endlich-dimensionale Dichtematrizen II}",
                "url": "http://www.physik.uni-leipzig.de/$\\sim$uhlmann/papers.html",
                "volume": "22",
                "year": "1973",
                "language": "de"
            },),),
            ("Szilard1929ZeitschriftFuerPhysik", Entry("article", persons={"author": [Person("Szilard, Leo")],}, fields={
                "doi": "Doi:10.1007/BF01341281",
                "issn": "1434-6001",
                "journal": "Zeitschrift f\\\"{u}r Physik",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "November",
                "number": "11-12",
                "pages": "840--856",
                "publisher": "Springer Berlin / Heidelberg",
                "title": "{\\\"{U}ber die Entropieverminderung in einem thermodynamischen System bei Eingriffen intelligenter Wesen}",
                "url": "http://www.springerlink.com/index/10.1007/BF01341281",
                "note": "URL http://www.springerlink.com/index/10.1007/BF01341281",
                "volume": "53",
                "year": "1929",
                "language": "Deutsch"
            },),),
            ("Bennett1996PRA_MSEntglQECorr", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("DiVincenzo, David P."),Person("Smolin, John A."),Person("Wootters, William K.")],}, fields={
                "abstract": "Entanglement purification protocols (EPPs) and quantum error-correcting codes (QECCs) provide two ways of protecting quantum states from interaction with the environment. In an EPP, perfectly entangled pure states are extracted, with some yield D, from a mixed state M shared by two parties; with a QECC, an arbitrary quantum state |$\\xi$\u3009 can be transmitted at some rate Q through a noisy channel $\\chi$ without degradation. We prove that an EPP involving one-way classical communication and acting on mixed state M\\^{}($\\chi$) (obtained by sharing halves of Einstein-Podolsky-Rosen pairs through a channel $\\chi$) yields a QECC on $\\chi$ with rate Q=D, and vice versa. We compare the amount of entanglement E(M) required to prepare a mixed state M by local actions with the amounts D1(M) and D2(M) that can be locally distilled from it by EPPs using one- and two-way classical communication, respectively, and give an exact expression for E(M) when M is Bell diagonal. While EPPs require classical communication, QECCs do not, and we prove Q is not increased by adding one-way classical communication. However, both D and Q can be increased by adding two-way communication. We show that certain noisy quantum channels, for example a 50\\% depolarizing channel, can be used for reliable transmission of quantum states if two-way communication is available, but cannot be used if only one-way communication is available. We exhibit a family of codes based on universal hashing able to achieve an asymptotic Q (or D) of 1-S for simple noise models, where S is the error entropy. We also obtain a specific, simple 5-bit single-error-correcting quantum block code. We prove that iff a QECC results in high fidelity for the case of no error then the QECC can be recast into a form where the encoder is the matrix inverse of the decoder. \u00a9 1996 The American Physical Society.",
                "annote": "An annotation might go here; Preprint available at https://arXiv.org/abs/quant-ph/9604024",
                "archivePrefix": "arXiv",
                "arxivId": "quant-ph/9604024",
                "doi": "doi:10.1103/PhysRevA.54.3824",
                "eprint": "9604024",
                "file": ":path/to/Mendeley/Bennett et al. - 1996 - Mixed-state entanglement and quantum error correction.pdf:pdf",
                "issn": "1050-2947",
                "journal": "Physical Review A",
                "keywords": "entanglement,quantum error correction",
                "mendeley-tags": "entanglement,quantum error correction",
                "month": "November",
                "number": "5",
                "pages": "3824--3851",
                "primaryClass": "quant-ph",
                "publisher": "American Physical Society",
                "shorttitle": "Phys. Rev. A",
                "title": "Mixed-state entanglement and quantum error correction",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.54.3824",
                "volume": "54",
                "year": "1996"
            },),),
            ("Earman1999_ExorcistXIVp2", Entry("article", persons={"author": [Person("Earman, John"),Person("Norton, John D.")],}, fields={
                "doi": "10.1016/S1355-2198(98)00026-4",
                "issn": "13552198",
                "journal": "Studies In History and Philosophy of Science Part B: Studies In History and Philosophy of Modern Physics",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "March",
                "number": "1",
                "pages": "1--40",
                "title": "Exorcist XIV: The Wrath of Maxwell\u2019s Demon. Part II. From Szilard to Landauer and Beyond",
                "url": "http://linkinghub.elsevier.com/retrieve/pii/S1355219898000264",
                "volume": "30",
                "year": "1999"
            },),),
            ("Molmer1998PRA_reply", Entry("article", persons={"author": [Person("M{\\o}lmer, Klaus")],}, fields={
                "abstract": "We conjecture that optical coherences, i.e., quantum-mechanical coherences between states separated by Bohr frequencies in the optical regime, do not exist in optics experiments. We claim the exact vanishing of optical field amplitudes and atomic dipole expectation values, and we discuss the seemingly contradictory success of assigning finite values to such quantities in theoretical calculations. We show that our conjecture is not at variance with the observed interference between different light sources. The connection to the concept of spontaneous symmetry breaking and the identification of entangled states as pointer basis states is discussed.",
                "doi": "10.1103/PhysRevA.58.4247",
                "file": ":Users/philippe/ref/articles/Mendeley/M{\\o}lmer - 1998 - Reply to \u201cComment on \u2018Optical coherence A convenient fiction'\u201d.pdf:pdf",
                "issn": "1050-2947",
                "journal": "Physical Review A",
                "month": "nov",
                "number": "5",
                "pages": "4247--4247",
                "title": "Reply to ``Comment on `Optical coherence: A convenient fiction'''",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.58.4247",
                "volume": "58",
                "year": "1998"
            },),),
            ("gour_measuring_2009", Entry("article", persons={"author": [Person("Gour, Gilad"),Person("Marvian, Iman"),Person("Spekkens, Robert W.")],}, fields={
                "title": "Measuring the quality of a quantum reference frame: The relative entropy of frameness",
                "volume": "80",
                "shorttitle": "Measuring the quality of a quantum reference frame",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.80.012307",
                "doi": "10.1103/PhysRevA.80.012307",
                "abstract": "In the absence of a reference frame for transformations associated with group G, any quantum state that is noninvariant under the action of G may serve as a token of the missing reference frame. We here present a measure of the quality of such a token: the relative entropy of frameness. This is defined as the relative entropy distance between the state of interest and the nearest G-invariant state. Unlike the relative entropy of entanglement, this quantity is straightforward to calculate, and we find it to be precisely equal to the G-asymmetry, a measure of frameness introduced by Vaccaro et al. It is shown to provide an upper bound on the mutual information between the group element encoded into the token and the group element that may be extracted from it by measurement. In this sense, it quantifies the extent to which the token successfully simulates a full reference frame. We also show that despite a suggestive analogy from entanglement theory, the regularized relative entropy of frameness is zero and therefore does not quantify the rate of interconversion between the token and some standard form of quantum reference frame. Finally, we show how these investigations yield an approach to bounding the relative entropy of entanglement.",
                "number": "1",
                "journal": "Physical Review A",
                "month": "July",
                "year": "2009",
                "pages": "012307"
            },),),
            #
            ("aberg_2009_cumul", Entry("article", persons={"author": [Person("\\AA{}berg, Johan"),Person("Mitchison, Graeme")],}, fields={
                "journal": "Journal of Mathematical Physics",
                "month": "April",
                "number": "4",
                "pages": "042103",
                "publisher": "AIP Publishing",
                "title": "{Cumulants and the moment algebra: Tools for analyzing weak measurements}",
                "volume": "50",
                "year": "2009"
            },),),
            ("BBPS1996", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Bernstein, Herbert J."),Person("Popescu, Sandu"),Person("Schumacher, Benjamin")],}, fields={
                "title": "Concentrating Partial Entanglement by Local Operations",
                "journal": "Phys. Rev. A",
                "year": "1996",
                "volume": "53",
                "pages": "2046-2052",
                "eprint": "quant-ph/9511030",
                "doi": "10.1103/PhysRevA.53.2046"
            },),),
            ("BBPSSW1996", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Popescu, Sandu"),Person("Schumacher, Benjamin"),Person("Smolin, John A."),Person("Wootters, William K.")],}, fields={
                "title": "Purification of noisy entanglement and faithful teleportation via noisy channels",
                "journal": "Phys. Rev. Lett.",
                "year": "1996",
                "volume": "76",
                "pages": "722--725",
                "eprint": "quant-ph/9511027",
                "doi": "10.1103/PhysRevLett.76.722"
            },),),
            ("VidalC-irre", Entry("article", persons={"author": [Person("Vidal, G."),Person("Cirac, J. I.")],}, fields={
                "title": "Irreversibility in asymptotic manipulations of entanglement",
                "journal": "Phys. Rev. Lett.",
                "year": "2001",
                "volume": "86",
                "pages": "5803--5806",
                "eprint": "quant-ph/0102036",
                "doi": "10.1103/PhysRevLett.86.5803"
            },),),
            ("linden2010small", Entry("article", persons={"author": [Person("Linden, N."),Person("Popescu, S."),Person("Skrzypczyk, P.")],}, fields={
                "title": "How small can thermal machines be? The smallest possible refrigerator",
                "journal": "Physical Review Letters",
                "volume": "105",
                "number": "13",
                "pages": "130401",
                "year": "2010",
                "publisher": "APS"
            },),),
            ("dahlsten2011inadequacy", Entry("article", persons={"author": [Person("Dahlsten, O.C.O."),Person("Renner, R."),Person("Rieper, E."),Person("Vedral, V.")],}, fields={
                "title": "Inadequacy of von Neumann entropy for characterizing extractable work",
                "journal": "New Journal of Physics",
                "volume": "13",
                "pages": "053015",
                "year": "2011",
                "publisher": "IOP Publishing"
            },),),
            ("horodecki_are_2002", Entry("article", persons={"author": [Person("Horodecki, {Micha\\l}"),Person("Oppenheim, Jonathan"),Person("Horodecki, Ryszard")],}, fields={
                "title": "Are the Laws of Entanglement Theory Thermodynamical?",
                "volume": "89",
                "url": "http://link.aps.org/doi/10.1103/PhysRevLett.89.240403",
                "doi": "10.1103/PhysRevLett.89.240403",
                "abstract": "We argue that on its face, entanglement theory satisfies laws equivalent to thermodynamics if the theory can be made reversible by adding certain bound entangled states as a free resource during entanglement manipulation. Subject to plausible conjectures, we prove that this is not the case in general, and discuss the implications of this for the thermodynamics of entanglement.",
                "number": "24",
                "journal": "Physical Review Letters",
                "month": "November",
                "year": "2002",
                "pages": "240403"
            },),),
            ("linden_reversibility_2005", Entry("article", persons={"author": [Person("Linden, Noah"),Person("Popescu, Sandu"),Person("Schumacher, Benjamin"),Person("Westmoreland, Michael")],}, fields={
                "title": "Reversibility of Local Transformations of Multiparticle Entanglement",
                "volume": "4",
                "url": "http://www.springerlink.com/content/hjvh868467m04122/",
                "doi": "10.1007/s11128-005-4608-0",
                "abstract": "We consider the transformation of multisystem entangled states by local quantum operations and classical communication. We show that, for any reversible transformation, the relative entropy of entanglement for any two parties must remain constant. This shows, for example, that it is not possible to convert {2N} three-party {GHZ} states into {3N} singlets, even in an asymptotic sense. Thus there is true three-party non-locality (i.e. not all three party entanglement is equivalent to two-party entanglement). Our results also allow us to make quantitative. statements about concentrating multi-particle entanglement. Finally, we show that there is true n-party entanglement for any n.",
                "number": "3",
                "journal": "Quantum Information Processing",
                "month": "August",
                "year": "2005",
                "pages": "241--250"
            },),),
            ("synak-radtke_asymptotic_2006", Entry("article", persons={"author": [Person("{Synak-Radtke}, Barbara"),Person("Horodecki, Michal")],}, fields={
                "title": "On asymptotic continuity of functions of quantum states",
                "volume": "39",
                "url": "http://iopscience.iop.org/0305-4470/39/26/L02/",
                "doi": "10.1088/0305-4470/39/26/L02",
                "number": "26",
                "journal": "Journal of a Physics A: Mathematical and General",
                "month": "June",
                "year": "2006",
                "pages": "L423"
            },),),
            ("Brandao2013_secondlaws", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Micha\u0142"),Person("Ng, Nelly Huei Ying"),Person("Oppenheim, Jonathan"),Person("Wehner, Stephanie")],}, fields={
                "abstract": "The second law of thermodynamics tells us which state transformations are so statistically unlikely that they are effectively forbidden. Its original formulation, due to Clausius, states that \"Heat can never pass from a colder to a warmer body without some other change, connected therewith, occurring at the same time.\" The second law applies to systems composed of many particles, however, we are seeing that one can make sense of thermodynamics in the regime where we only have a small number of particles interacting with a heat bath, or when we have highly correlated systems and wish to make non-statistical statements about them. Is there a second law of thermodynamics in this regime? Here, we find that for processes which are cyclic or very close to cyclic, the second law for microscopic or highly correlated systems takes on a very different form than it does at the macroscopic scale, imposing not just one constraint on what state transformations are possible, but an entire family of constraints. In particular, we find that the Renyi relative entropy distances to the equilibrium state can never increase. We further find that there are three regimes which govern which family of second laws govern state transitions, depending on how cyclic the process is. In one regime one can cause an apparent violation of the usual second law, through a process of embezzling work from a large system which remains arbitrarily close to its original state.",
                "archivePrefix": "arXiv",
                "arxivId": "1305.5278",
                "eprint": "1305.5278",
                "keywords": "thermo",
                "mendeley-tags": "thermo",
                "month": "May",
                "title": "{The second laws of quantum thermodynamics}",
                "url": "http://arxiv.org/abs/1305.5278",
                "year": "2013"
            },),),
            ("Brandao2012_exponential", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Michal")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "1206.2947",
                "eprint": "1206.2947",
                "month": "June",
                "title": "{Exponential Decay of Correlations Implies Area Law}",
                "url": "http://arxiv.org/abs/1206.2947",
                "year": "2012"
            },),),
            ("Brandao2013_resource", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando"),Person("Horodecki, Micha\u0142"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph"),Person("Spekkens, Robert")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "doi": "10.1103/PhysRevLett.111.250404",
                "eprint": "1111.3882",
                "file": ":home/pfaist/ref/articles/Mendeley/Brand\\~{a}o et al. - 2013 - Resource Theory of Quantum States Out of Thermal Equilibrium.pdf:pdf",
                "issn": "0031-9007",
                "journal": "Physical Review Letters",
                "keywords": "resource theory,thermo",
                "mendeley-tags": "resource theory,thermo",
                "month": "December",
                "number": "25",
                "pages": "250404",
                "title": "{Resource Theory of Quantum States Out of Thermal Equilibrium}",
                "url": "http://link.aps.org/doi/10.1103/PhysRevLett.111.250404",
                "volume": "111",
                "year": "2013"
            },),),
            ("Brandao2012_local", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Harrow, Aram W."),Person("Horodecki, Michal")],}, fields={
                "abstract": "We prove that local random quantum circuits acting on n qubits composed of polynomially many nearest neighbor two-qubit gates form an approximate unitary poly(n)-design. Previously it was unknown whether random quantum circuits were a t-design for any t > 3. The proof is based on an interplay of techniques from quantum many-body theory, representation theory, and the theory of Markov chains. In particular we employ a result of Nachtergaele for lower bounding the spectral gap of quantum local Hamiltonians; a quasi-orthogonality property of permutation matrices; a result of Oliveira which extends to the unitary group the path-coupling method for bounding the mixing time of random walks; and a result of Bourgain and Gamburd showing that dense subgroups of the special unitary group, composed of elements with algebraic entries, are infinity-copy tensor-product expanders. We also consider pseudo-randomness properties of local random quantum circuits of small depth and prove they constitute a quantum poly(n)-copy tensor-product expander. The proof also rests on techniques from quantum many-body theory, in particular on the detectability lemma of Aharonov et al. We give three applications of the results. First we show that almost every circuit U of size n\\^{}k on n qubits cannot be distinguished from a Haar uniform unitary by circuits of size n\\^{}[(k+3)/6] that are given oracle access to U; this provides a data-hiding scheme against computationally bounded adversaries. Second we reconsider a recent argument of Masanes et al concerning local equilibration of time-evolving quantum systems, and strengthen the connection between fast equilibration of small subsystems and the circuit complexity of the Hamiltonian. Third we show that in one dimension almost every parallel local circuit of linear depth generates topological order, matching an upper bound to the problem due to Bravyi et al.",
                "archivePrefix": "arXiv",
                "arxivId": "1208.0692",
                "eprint": "1208.0692",
                "month": "August",
                "pages": "36",
                "title": "{Local random quantum circuits are approximate polynomial-designs}",
                "url": "http://arxiv.org/abs/1208.0692",
                "year": "2012"
            },),),
            ("2015PNAS..112.3275B", Entry("article", persons={"author": [Person("{Brand{\\~a}o}, F."),Person("{Horodecki}, M."),Person("{Ng}, N."),Person("{Oppenheim}, J."),Person("{Wehner}, S.")],}, fields={
                "title": "{The second laws of quantum thermodynamics}",
                "journal": "Proceedings of the National Academy of Science",
                "archivePrefix": "arXiv",
                "eprint": "1305.5278",
                "primaryClass": "quant-ph",
                "year": "2015",
                "month": "March",
                "volume": "112",
                "pages": "3275-3279",
                "doi": "10.1073/pnas.1411728112",
                "adsurl": "http://adsabs.harvard.edu/abs/2015PNAS..112.3275B",
                "adsnote": "Provided by the SAO/NASA Astrophysics Data System"
            },),),
            ("brandao_2011-arxiv-2ndlaws", Entry("article", persons={"author": [Person("Brandao, F."),Person("{Horodecki}, M."),Person("{Ng}, N."),Person("{Oppenheim}, J."),Person("Wehner, S.")],}, fields={
                "title": "{The second laws of quantum thermodynamics}",
                "journal": "Proceedings of the National Academy of Science",
                "archivePrefix": "arXiv",
                "eprint": "1305.5278",
                "primaryClass": "quant-ph",
                "year": "2013",
                "month": "March"
            },),),
        ]





if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=1)
    unittest.main()
