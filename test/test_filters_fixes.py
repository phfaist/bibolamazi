
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

if __name__ == '__main__':
    # install custom logger, especially .longdebug()
    from bibolamazi.core import blogger
    blogger.setup_simple_console_logging(level=1)

import unittest

import bibolamazi.init

from helpers import CustomAssertions
from pybtex.database import Entry, Person
from bibolamazi.core.bibfilter.argtypes import CommaStrList
from bibolamazi.filters.fixes import FixesFilter

class TestWorks(unittest.TestCase, CustomAssertions):

    def __init__(self, *args, **kwargs):
        super(TestWorks, self).__init__(*args, **kwargs)

        self.maxDiff = None

    def test_fixSpcAfterEsc(self):

        filt = FixesFilter(fix_space_after_escape=True)

        entries = self.get_std_test_entries()
        
        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
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
            ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA{}berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
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
                "abstract": "We provide a complete picture of contractivity of trace preserving positive maps with respect to $p$-norms. We show that for $p>1$ contractivity holds in general if and only if the map is unital. When the domain is restricted to the traceless subspace of Hermitian matrices, then contractivity is shown to hold in the case of qubits for arbitrary $p\\geq{}1$ and in the case of qutrits if and only if $p=1,\\infty$. In all non-contractive cases best possible bounds on the $p$-norms are derived.",
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
        ]

        self.assert_keyentrylists_equal(entries, entries_ok)
                







    def test_utf8ToLtx(self):

        filt = FixesFilter(encode_utf8_to_latex=True)

        entries = self.get_std_test_entries()

        entries += [
            ("TestTestTest3", Entry("article", persons={"author": [Person("H\u00e9l\u00e0, Xavier"),
                                                                   Person("Abc, Xyz")],}, fields={
                "language": "en",
                "title": "{Contractivity of stuff & more things}",
                "journal": "Journal of Blah Blou",
                "abstract": "We provide a ton of # LaTeX special % characters to & encode and have fun with.",
                "year": "2020",
            },),),
            ]

        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
            ("Jacobson1995", Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                "abstract": "The Einstein equation is derived from the proportionality of entropy and the horizon area together with the fundamental relation $\\delta$Q~=~TdS. The key idea is to demand that this relation hold for all the local Rindler causal horizons through each spacetime point, with $\\delta$Q and T interpreted as the energy flux and Unruh temperature seen by an accelerated observer just inside the horizon. This requires that gravitational lensing by matter energy distorts the causal structure of spacetime so that the Einstein equation holds. Viewed in this way, the Einstein equation is an equation of state.",
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
            ("Bennett1993PRL_Teleportation", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Cr{\\'e}peau, Claude"),Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")],}, fields={
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
                "doi": "10.1007/JHEP04(2011)029",
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
                "year": "2011",
                "archivePrefix": "arXiv",
                "arxivId": "1001.0785",
                "eprint": "1001.0785",
            },),),
            ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
                "abstract": "The heat generated by computations is not only an obstacle to circuit miniaturization but also a fundamental aspect of the relationship between information theory and thermodynamics. In principle, reversible operations may be performed at no energy cost; given that irreversible computations can always be decomposed into reversible operations followed by the erasure of data, the problem of calculating their energy cost is reduced to the study of erasure. Landauer's principle states that the erasure of data stored in a system has an inherent work cost and therefore dissipates heat. However, this consideration assumes that the information about the system to be erased is classical, and does not extend to the general case where an observer may have quantum information about the system to be erased, for instance by means of a quantum memory entangled with the system. Here we show that the standard formulation and implications of Landauer's principle are no longer valid in the presence of quantum information. Our main result is that the work cost of erasure is determined by the entropy of the system, conditioned on the quantum information an observer has about it. In other words, the more an observer knows about the system, the less it costs to erase it. This result gives a direct thermodynamic significance to conditional entropies, originally introduced in information theory. Furthermore, it provides new bounds on the heat generation of computations: because conditional entropies can become negative in the quantum case, an observer who is strongly correlated with a system may gain work while erasing it, thereby cooling the environment.",
                "doi": "DOI 10.1038/nature10123",
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
                'url': 'http://dx.doi.org/10.1038/nature10123',
                "volume": "474",
                "year": "2011",
                "archivePrefix": "arXiv",
                "arxivId": "1009.1630",
                "eprint": "1009.1630",
            },),),
            ("Brandao2011arXiv", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Micha{\\l}"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph M."),Person("Spekkens, Robert W.")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "keywords": "resource theory,thermo",
                "mendeley-tags": "resource theory,thermo",
                "month": "November",
                "title": "{The Resource Theory of Quantum States Out of Thermal Equilibrium}",
                "year": "2011",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "eprint": "1111.3882",
                'pages': '12',
                'url': 'http://arxiv.org/abs/1111.3882',
            },),),
            ("PerezGarcia2006", Entry("article", persons={"author": [Person("P{\\'e}rez-Garc{\\'\\i}a, David"),Person("Wolf, Michael M."),Person("Petz, Denes"),Person("Ruskai, Mary Beth")],}, fields={
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
                "file": ":home/.............../P{\\'e}rez-Garc{\\'\\i}a et al. - 2006 - Contractivity of positive and trace preserving maps under $L_p$ norms.pdf:pdf",
                "year": "2006",
                "keywords": "Hermitian matrices,majorization,thermo"
            },),),
            ("TestTestTest3", Entry("article", persons={"author": [Person("H{\\'e}l{\\`a}, Xavier"),
                                                                   Person("Abc, Xyz")],}, fields={
                "language": "en",
                "title": "{Contractivity of stuff \\& more things}",
                "journal": "Journal of Blah Blou",
                "abstract": "We provide a ton of \\# LaTeX special \\% characters to \\& encode and have fun with.",
                "year": "2020",
            },),),
        ]

        self.assert_keyentrylists_equal(entries, entries_ok)


    


    def test_encodeLatexToUtf8(self):

        entries = self.get_std_test_entries(except_keys='delRio2011Nature')
        entries += [
                ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA{}berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
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
                ]
        filt = FixesFilter(encode_latex_to_utf8=True)

        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
            ('Jacobson1995',
             Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                "abstract": "The Einstein equation is derived from the proportionality of entropy and the horizon area together with the fundamental relation δQ = TdS. The key idea is to demand that this relation hold for all the local Rindler causal horizons through each spacetime point, with δQ and T interpreted as the energy flux and Unruh temperature seen by an accelerated observer just inside the horizon. This requires that gravitational lensing by matter energy distorts the causal structure of spacetime so that the Einstein equation holds. Viewed in this way, the Einstein equation is an equation of state.",
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
                "title": "Thermodynamics of Spacetime: The Einstein Equation of State",
                "url": "http://link.aps.org/doi/10.1103/PhysRevLett.75.1260",
                "volume": "75",
                "year": "1995"
            },),),
            ("Bennett1993PRL_Teleportation",
             Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("Brassard, Gilles"),Person("Crépeau, Claude"),Person("Jozsa, Richard"),Person("Peres, Asher"),Person("Wootters, William K.")],}, fields={
                 "doi": "10.1103/PhysRevLett.70.1895",
                 "issn": "0031-9007",
                 "journal": "Physical Review Letters",
                 "month": "March",
                 "number": "13",
                 "pages": "1895--1899",
                 "publisher": "American Physical Society",
                 "title": "Teleporting an unknown quantum state via dual classical and Einstein-Podolsky-Rosen channels",
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
                "title": "On the Einstein-Podolsky-Rosen paradox",
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
                "title": "Particle creation by black holes",
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
                "title": "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?",
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
                "title": "The Theory of Positrons",
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
                "title": "Irreversibility and Heat Generation in the Computing Process",
                "volume": "5",
                "year": "1961"
            },),),
            ("Shannon1948BSTJ", Entry("article", persons={"author": [Person("Shannon, Claude E.")],}, fields={
                "journal": "The Bell System Technical Journal",
                "month": "July",
                "pages": "379--423",
                "title": "A Mathematical Theory of Communication",
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
                "title": "On the origin of gravity and the laws of Newton",
                "url": "http://link.springer.com/10.1007/JHEP04(2011)029",
                "volume": "2011",
                "year": "2011"
            },),),
            ("Brandao2011arXiv", Entry("article", persons={"author": [Person("Brandão, Fernando G. S. L."),Person("Horodecki, Michał"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph M."),Person("Spekkens, Robert W.")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "eprint": "1111.3882",
                "keywords": "resource theory,thermo",
                "mendeley-tags": "resource theory,thermo",
                "month": "November",
                "pages": "12",
                "title": "The Resource Theory of Quantum States Out of Thermal Equilibrium",
                "url": "http://arxiv.org/abs/1111.3882",
                "year": "2011"
            },),),
            ("PerezGarcia2006", Entry("article", persons={"author": [Person("Pérez-García, David"),Person("Wolf, Michael M."),Person("Petz, Denes"),Person("Ruskai, Mary Beth")],}, fields={
                "doi": "10.1063/1.2218675",
                "language": "en",
                "title": "Contractivity of positive and trace preserving maps under L_p norms",
                "journal": "Journal of Mathematical Physics",
                "abstract": "We provide a complete picture of contractivity of trace preserving positive maps with respect to p-norms. We show that for p>1 contractivity holds in general if and only if the map is unital. When the domain is restricted to the traceless subspace of Hermitian matrices, then contractivity is shown to hold in the case of qubits for arbitrary p≥1 and in the case of qutrits if and only if p=1,∞. In all non-contractive cases best possible bounds on the p-norms are derived.",
                "issn": "00222488",
                "mendeley-tags": "majorization,thermo",
                "number": "8",
                "month": "August",
                "volume": "47",
                "pages": "083506",
                "file": ":home/.............../Pérez-García et al. - 2006 - Contractivity of positive and trace preserving maps under L_p norms.pdf:pdf",
                "year": "2006",
                "keywords": "Hermitian matrices,majorization,thermo"
            },),),
            ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, Lídia"),Person("Åberg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
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
                "title": "The thermodynamic meaning of negative entropy",
                "url": "http://dx.doi.org/10.1038/nature10123",
                "volume": "474",
                "year": "2011"
            },),),
        ]
        

        self.assert_keyentrylists_equal(entries, entries_ok)



    def test_protect_names(self):

        entries = self.get_std_test_entries()
        entries += [
            ('Test20XX',
             Entry("article", persons={"author": [Person("Zzyzkx, Aaouoosuoa")]}, fields={
                     "abstract": "Maxwell's demon and Szilard in the i.i.d. regime and more Bell names with R{\\'{e}}nyi entropies here.",
                     "journal": "Physical Review Letters",
                     "publisher": "American Physical Society",
                     "title": "{Part I: Maxwell's demon in the i.i.d. regime with R{\\'{e}}nyi entropies}",
                     "volume": "1",
                     "year": "1990"
                 },),),
            ]

        filt = FixesFilter(
                 remove_full_braces=True,
            # test: empty fields are ignored; {i.i.d.} gets replaced before
            # {I}., and substrings are stripped of leading and trailing
            # whitespace
                 protect_names=CommaStrList("Einstein,Maxwell, , Landauer ,Podolsky,Rosen, Hawking, Newton,i.i.d.,R{\\'{e}}nyi,Neumann,Szilard,Bell,I,II,XIV"),
        )

        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
                ('Jacobson1995',
                 Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                     "abstract": "The {Einstein} equation is derived from the proportionality of entropy and the horizon area together with the fundamental relation $\\delta$Q = TdS. The key idea is to demand that this relation hold for all the local Rindler causal horizons through each spacetime point, with $\\delta$Q and T interpreted as the energy flux and Unruh temperature seen by an accelerated observer just inside the horizon. This requires that gravitational lensing by matter energy distorts the causal structure of spacetime so that the {Einstein} equation holds. Viewed in this way, the {Einstein} equation is an equation of state.",
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
                     "title": "Thermodynamics of Spacetime: The {Einstein} Equation of State",
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
                     "title": "Teleporting an unknown quantum state via dual classical and {Einstein}-{Podolsky}-{Rosen} channels",
                     "url": "http://link.aps.org/doi/10.1103/PhysRevLett.70.1895",
                     "volume": "70",
                     "year": "1993"
                 },),),
                ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                    "issn": "0554-128X",
                    "journal": "Physics",
                    "keywords": "{Bell}'s paper,EPR paradox,entanglement,hidden variables",
                    "mendeley-tags": "{Bell}'s paper,EPR paradox,entanglement,hidden variables",
                    "pages": "195",
                    "publisher": "Physics Publishing Company",
                    "title": "On the {Einstein}-{Podolsky}-{Rosen} paradox",
                    "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                    "volume": "1",
                    "year": "1964"
                },),),
                ("Hawking1975", Entry("article", persons={"author": [Person("Hawking, S. W.")],}, fields={
                    "doi": "10.1007/BF02345020",
                    "issn": "0010-3616",
                    "journal": "Communications In Mathematical Physics",
                    "keywords": "black holes,{Hawking} radiation,thermo",
                    "mendeley-tags": "black holes,{Hawking} radiation,thermo",
                    "month": "August",
                    "number": "3",
                    "pages": "199--220",
                    "title": "Particle creation by black holes",
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
                    "title": "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?",
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
                    "title": "The Theory of Positrons",
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
                    "title": "Irreversibility and Heat Generation in the Computing Process",
                    "volume": "5",
                    "year": "1961"
                },),),
                ("Shannon1948BSTJ", Entry("article", persons={"author": [Person("Shannon, Claude E.")],}, fields={
                    "journal": "The {Bell} System Technical Journal",
                    "month": "July",
                    "pages": "379--423",
                    "title": "A Mathematical Theory of Communication",
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
                    "title": "On the origin of gravity and the laws of {Newton}",
                    "url": "http://link.springer.com/10.1007/JHEP04(2011)029",
                    "volume": "2011",
                    "year": "2011"
                },),),
                ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
                    "abstract": "The heat generated by computations is not only an obstacle to circuit miniaturization but also a fundamental aspect of the relationship between information theory and thermodynamics. In principle, reversible operations may be performed at no energy cost; given that irreversible computations can always be decomposed into reversible operations followed by the erasure of data, the problem of calculating their energy cost is reduced to the study of erasure. {Landauer}'s principle states that the erasure of data stored in a system has an inherent work cost and therefore dissipates heat. However, this consideration assumes that the information about the system to be erased is classical, and does not extend to the general case where an observer may have quantum information about the system to be erased, for instance by means of a quantum memory entangled with the system. Here we show that the standard formulation and implications of {Landauer}'s principle are no longer valid in the presence of quantum information. Our main result is that the work cost of erasure is determined by the entropy of the system, conditioned on the quantum information an observer has about it. In other words, the more an observer knows about the system, the less it costs to erase it. This result gives a direct thermodynamic significance to conditional entropies, originally introduced in information theory. Furthermore, it provides new bounds on the heat generation of computations: because conditional entropies can become negative in the quantum case, an observer who is strongly correlated with a system may gain work while erasing it, thereby cooling the environment.",
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
                    "title": "The thermodynamic meaning of negative entropy",
                    "url": "http://dx.doi.org/10.1038/nature10123",
                    "volume": "474",
                    "year": "2011"
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
                    "title": "The Resource Theory of Quantum States Out of Thermal Equilibrium",
                    "url": "http://arxiv.org/abs/1111.3882",
                    "year": "2011"
                },),),
                ("PerezGarcia2006", Entry("article", persons={"author": [Person("P\u00e9rez-Garc\u00eda, David"),Person("Wolf, Michael M."),Person("Petz, Denes"),Person("Ruskai, Mary Beth")],}, fields={
                    "doi": "10.1063/1.2218675",
                    "language": "en",
                    "title": "Contractivity of positive and trace preserving maps under $L_p$ norms",
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
                ('Test20XX',
                 Entry("article", persons={"author": [Person("Zzyzkx, Aaouoosuoa")]}, fields={
                     "abstract": "{Maxwell}'s demon and {Szilard} in the {i.i.d.} regime and more {Bell} names with {R{\\'{e}}nyi} entropies here.",
                     "journal": "Physical Review Letters",
                     "publisher": "American Physical Society",
                     "title": "Part {I}: {Maxwell}'s demon in the {i.i.d.} regime with {R{\\'{e}}nyi} entropies",
                     "volume": "1",
                     "year": "1990"
                 },),),
        ]

        self.assert_keyentrylists_equal(entries, entries_ok)


    def test_rest(self):

        entries = self.get_std_test_entries()
        # test more stuff:
        entries += [
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
        ]

        filt = FixesFilter(
                 remove_type_from_phd=True,
                 remove_full_braces=True,
                 remove_full_braces_not_lang=['Deutsch'],
                 protect_names=CommaStrList('Einstein,Maxwell,Landauer,Newton,Neumann,Szilard,Bell,I,II,XIV'),
                 remove_file_field=True,
                 remove_fields=['mendeley-tags', 'keywords'],
                 remove_doi_prefix=True,
                 map_annote_to_note=True,
                 auto_urlify=['abstract','note','annote'],
                 rename_language={'de':'Deutsch'},
                 fix_mendeley_bug_urls=True,
                 protect_capital_letter_after_dot=['title','annote'],
                 protect_capital_letter_at_begin=['publisher'],
                 convert_dbl_quotes=True,
                 convert_sgl_quotes=True,
                 dbl_quote_macro=r'\enquote',
                 sgl_quote_macro=r'\enquote*')

        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
            ('Jacobson1995',
             Entry("article", persons={"author": [Person("Jacobson, Ted")]}, fields={
                 "abstract": "The {Einstein} equation is derived from the proportionality of entropy and the horizon area together with the fundamental relation $\\delta$Q = TdS. The key idea is to demand that this relation hold for all the local Rindler causal horizons through each spacetime point, with $\\delta$Q and T interpreted as the energy flux and Unruh temperature seen by an accelerated observer just inside the horizon. This requires that gravitational lensing by matter energy distorts the causal structure of spacetime so that the {Einstein} equation holds. Viewed in this way, the {Einstein} equation is an equation of state.",
                 "note": "arxiv:gr-qc/9504004",
                 "doi": "10.1103/PhysRevLett.75.1260",
                 "issn": "0031-9007",
                 "journal": "Physical Review Letters",
                 "month": "August",
                 "number": "7",
                 "pages": "1260--1263",
                 "publisher": "{A}merican Physical Society",
                 "shorttitle": "Phys. Rev. Lett.",
                 "title": "Thermodynamics of Spacetime: {T}he {Einstein} Equation of State",
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
                 "publisher": "{A}merican Physical Society",
                 "title": "Teleporting an unknown quantum state via dual classical and {Einstein}-Podolsky-Rosen channels",
                 "url": "http://link.aps.org/doi/10.1103/PhysRevLett.70.1895",
                 "volume": "70",
                 "year": "1993"
             },),),
            ("Bell1964", Entry("article", persons={"author": [Person("Bell, J. S.")],}, fields={
                "issn": "0554-128X",
                "journal": "Physics",
                "pages": "195",
                "publisher": "{P}hysics Publishing Company",
                "title": "On the {Einstein}-Podolsky-Rosen paradox",
                "url": "http://books.google.co.uk/books?id=c3JDAQAAIAAJ",
                "volume": "1",
                "year": "1964"
            },),),
            ("Hawking1975", Entry("article", persons={"author": [Person("Hawking, S. W.")],}, fields={
                "doi": "10.1007/BF02345020",
                "issn": "0010-3616",
                "journal": "Communications In Mathematical Physics",
                "month": "August",
                "number": "3",
                "pages": "199--220",
                "title": "Particle creation by black holes",
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
                "publisher": "{A}merican Physical Society",
                "title": "Can Quantum-Mechanical Description of Physical Reality Be Considered Complete?",
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
                "publisher": "{A}merican Physical Society",
                "title": "The Theory of Positrons",
                "url": "http://link.aps.org/doi/10.1103/PhysRev.76.749",
                "volume": "76",
                "year": "1949"
            },),),
            ("Landauer1961_5392446Erasure", Entry("article", persons={"author": [Person("Landauer, Rolf")],}, fields={
                "doi": "10.1147/rd.53.0183",
                "issn": "0018-8646",
                "journal": "IBM Journal of Research and Development",
                "month": "July",
                "number": "3",
                "pages": "183--191",
                "title": "Irreversibility and Heat Generation in the Computing Process",
                "volume": "5",
                "year": "1961"
            },),),
            ("Shannon1948BSTJ", Entry("article", persons={"author": [Person("Shannon, Claude E.")],}, fields={
                "journal": "The {Bell} System Technical Journal",
                "month": "July",
                "pages": "379--423",
                "title": "A Mathematical Theory of Communication",
                "url": "http://cm.bell-labs.com/cm/ms/what/shannonday/paper.html",
                "volume": "27",
                "year": "1948"
            },),),
            ("Verlinde2011_entropic", Entry("article", persons={"author": [Person("Verlinde, Erik")],}, fields={
                "archivePrefix": "arXiv",
                "arxivId": "1001.0785",
                "doi": "10.1007/JHEP04(2011)029",
                "eprint": "1001.0785",
                "issn": "1029-8479",
                "journal": "Journal of High Energy Physics",
                "month": "April",
                "number": "4",
                "pages": "29",
                "title": "On the origin of gravity and the laws of {Newton}",
                "url": "http://link.springer.com/10.1007/JHEP04(2011)029",
                "volume": "2011",
                "year": "2011"
            },),),
            ("delRio2011Nature", Entry("article", persons={"author": [Person("del Rio, L\\'{\\i}dia"),Person("\\AA berg, Johan"),Person("Renner, Renato"),Person("Dahlsten, Oscar"),Person("Vedral, Vlatko")],}, fields={
                "abstract": "The heat generated by computations is not only an obstacle to circuit miniaturization but also a fundamental aspect of the relationship between information theory and thermodynamics. In principle, reversible operations may be performed at no energy cost; given that irreversible computations can always be decomposed into reversible operations followed by the erasure of data, the problem of calculating their energy cost is reduced to the study of erasure. {Landauer}'s principle states that the erasure of data stored in a system has an inherent work cost and therefore dissipates heat. However, this consideration assumes that the information about the system to be erased is classical, and does not extend to the general case where an observer may have quantum information about the system to be erased, for instance by means of a quantum memory entangled with the system. Here we show that the standard formulation and implications of {Landauer}'s principle are no longer valid in the presence of quantum information. Our main result is that the work cost of erasure is determined by the entropy of the system, conditioned on the quantum information an observer has about it. In other words, the more an observer knows about the system, the less it costs to erase it. This result gives a direct thermodynamic significance to conditional entropies, originally introduced in information theory. Furthermore, it provides new bounds on the heat generation of computations: because conditional entropies can become negative in the quantum case, an observer who is strongly correlated with a system may gain work while erasing it, thereby cooling the environment.",
                "archivePrefix": "arXiv",
                "arxivId": "1009.1630",
                "doi": "10.1038/nature10123",
                "eprint": "1009.1630",
                "issn": "1476-4687",
                "journal": "Nature",
                "month": "June",
                "number": "7349",
                "pages": "61--63",
                "publisher": "{N}ature Publishing Group, a division of Macmillan Publishers Limited. All Rights Reserved.",
                "shorttitle": "Nature",
                "title": "The thermodynamic meaning of negative entropy",
                "url": "http://dx.doi.org/10.1038/nature10123",
                "volume": "474",
                "year": "2011"
            },),),
            ("Brandao2011arXiv", Entry("article", persons={"author": [Person("Brand\\~{a}o, Fernando G. S. L."),Person("Horodecki, Micha\u0142"),Person("Oppenheim, Jonathan"),Person("Renes, Joseph M."),Person("Spekkens, Robert W.")],}, fields={
                "abstract": "The ideas of thermodynamics have proved fruitful in the setting of quantum information theory, in particular the notion that when the allowed transformations of a system are restricted, certain states of the system become useful resources with which one can prepare previously inaccessible states. The theory of entanglement is perhaps the best-known and most well-understood resource theory in this sense. Here we return to the basic questions of thermodynamics using the formalism of resource theories developed in quantum information theory and show that the free energy of thermodynamics emerges naturally from the resource theory of energy-preserving transformations. Specifically, the free energy quantifies the amount of useful work which can be extracted from asymptotically-many copies of a quantum system when using only reversible energy-preserving transformations and a thermal bath at fixed temperature. The free energy also quantifies the rate at which resource states can be reversibly interconverted asymptotically, provided that a sublinear amount of coherent superposition over energy levels is available, a situation analogous to the sublinear amount of classical communication required for entanglement dilution.",
                "archivePrefix": "arXiv",
                "arxivId": "1111.3882",
                "eprint": "1111.3882",
                "month": "November",
                "pages": "12",
                "title": "The Resource Theory of Quantum States Out of Thermal Equilibrium",
                "url": "http://arxiv.org/abs/1111.3882",
                "year": "2011"
            },),),
            ("PerezGarcia2006", Entry("article", persons={"author": [Person("P\u00e9rez-Garc\u00eda, David"),Person("Wolf, Michael M."),Person("Petz, Denes"),Person("Ruskai, Mary Beth")],}, fields={
                "doi": "10.1063/1.2218675",
                "language": "en",
                "title": "Contractivity of positive and trace preserving maps under $L_p$ norms",
                "journal": "Journal of Mathematical Physics",
                "abstract": "We provide a complete picture of contractivity of trace preserving positive maps with respect to $p$-norms. We show that for $p>1$ contractivity holds in general if and only if the map is unital. When the domain is restricted to the traceless subspace of Hermitian matrices, then contractivity is shown to hold in the case of qubits for arbitrary $p\\geq 1$ and in the case of qutrits if and only if $p=1,\\infty$. In all non-contractive cases best possible bounds on the $p$-norms are derived.",
                "issn": "00222488",
                "number": "8",
                "month": "August",
                "volume": "47",
                "pages": "083506",
                "year": "2006",
            },),),
            # more stuff:
            ("Janzing2006Habil", Entry("phdthesis", persons={"author": [Person("Janzing, Dominik")],}, fields={
                "abstract": "This work considers several hypothetical control processes on the nanoscopic level and show their analogy to computation processes. It shows that measuring certain types of quantum observables is such a complex task that every instrument that is able to perform it would necessarily be an extremely powerful computer. URL \\url{https://dx.doi.org/10.5445/KSP/1000005188}",
                "address": "Karlsruhe",
                "doi": "10.5445/KSP/1000005188",
                "isbn": "3-86644-083-9",
                "publisher": "{U}niversit\\\"{a}tsverlag Karlsruhe",
                "school": "Universit\u00e4t Karlsruhe",
                "title": "Computer science approach to quantum control",
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
                "title": "Security of Quantum Key Distribution",
                "url": "http://arxiv.org/abs/quant-ph/0512258",
                "year": "2005"
            },),),
            ("Uhlmann1973_EdDMII", Entry("article", persons={"author": [Person("Uhlmann, Armin")],}, fields={
                "journal": "Wiss. Z. Karl-Marx-Univ. Leipzig, Math.-Naturwiss.",
                "pages": "139--177",
                "title": "{Endlich-dimensionale Dichtematrizen II}",
                "url": "http://www.physik.uni-leipzig.de/~uhlmann/papers.html",
                "volume": "22",
                "year": "1973",
                "language": "Deutsch"
            },),),
            ("Szilard1929ZeitschriftFuerPhysik", Entry("article", persons={"author": [Person("Szilard, Leo")],}, fields={
                "doi": "10.1007/BF01341281",
                "issn": "1434-6001",
                "journal": "Zeitschrift f\\\"{u}r Physik",
                "month": "November",
                "number": "11-12",
                "pages": "840--856",
                "publisher": "{S}pringer Berlin / Heidelberg",
                "title": "{\\\"{U}ber die Entropieverminderung in einem thermodynamischen System bei Eingriffen intelligenter Wesen}",
                "url": "http://www.springerlink.com/index/10.1007/BF01341281",
                "note": "URL \\url{http://www.springerlink.com/index/10.1007/BF01341281}",
                "volume": "53",
                "year": "1929",
                "language": "Deutsch"
            },),),
            ("Bennett1996PRA_MSEntglQECorr", Entry("article", persons={"author": [Person("Bennett, Charles H."),Person("DiVincenzo, David P."),Person("Smolin, John A."),Person("Wootters, William K.")],}, fields={
                "abstract": "Entanglement purification protocols (EPPs) and quantum error-correcting codes (QECCs) provide two ways of protecting quantum states from interaction with the environment. In an EPP, perfectly entangled pure states are extracted, with some yield D, from a mixed state M shared by two parties; with a QECC, an arbitrary quantum state |$\\xi$\u3009 can be transmitted at some rate Q through a noisy channel $\\chi$ without degradation. We prove that an EPP involving one-way classical communication and acting on mixed state M\\^{}($\\chi$) (obtained by sharing halves of {Einstein}-Podolsky-Rosen pairs through a channel $\\chi$) yields a QECC on $\\chi$ with rate Q=D, and vice versa. We compare the amount of entanglement E(M) required to prepare a mixed state M by local actions with the amounts D1(M) and D2(M) that can be locally distilled from it by EPPs using one- and two-way classical communication, respectively, and give an exact expression for E(M) when M is {Bell} diagonal. While EPPs require classical communication, QECCs do not, and we prove Q is not increased by adding one-way classical communication. However, both D and Q can be increased by adding two-way communication. We show that certain noisy quantum channels, for example a 50\\% depolarizing channel, can be used for reliable transmission of quantum states if two-way communication is available, but cannot be used if only one-way communication is available. We exhibit a family of codes based on universal hashing able to achieve an asymptotic Q (or D) of 1-S for simple noise models, where S is the error entropy. We also obtain a specific, simple 5-bit single-error-correcting quantum block code. We prove that iff a QECC results in high fidelity for the case of no error then the QECC can be recast into a form where the encoder is the matrix inverse of the decoder. \u00a9 1996 The American Physical Society.",
                "note": "An annotation might go here; Preprint available at \\url{https://arXiv.org/abs/quant-ph/9604024}",
                "archivePrefix": "arXiv",
                "arxivId": "quant-ph/9604024",
                "doi": "10.1103/PhysRevA.54.3824",
                "eprint": "9604024",
                "issn": "1050-2947",
                "journal": "Physical Review A",
                "month": "November",
                "number": "5",
                "pages": "3824--3851",
                "primaryClass": "quant-ph",
                "publisher": "{A}merican Physical Society",
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
                "month": "March",
                "number": "1",
                "pages": "1--40",
                "title": "Exorcist {XIV}: {T}he Wrath of {Maxwell}\u2019s Demon. {P}art {II}. {F}rom {Szilard} to {Landauer} and Beyond",
                "url": "http://linkinghub.elsevier.com/retrieve/pii/S1355219898000264",
                "volume": "30",
                "year": "1999"
            },),),
            ("Molmer1998PRA_reply", Entry("article", persons={"author": [Person("M{\\o}lmer, Klaus")],}, fields={
                "abstract": "We conjecture that optical coherences, {I}.e., quantum-mechanical coherences between states separated by Bohr frequencies in the optical regime, do not exist in optics experiments. We claim the exact vanishing of optical field amplitudes and atomic dipole expectation values, and we discuss the seemingly contradictory success of assigning finite values to such quantities in theoretical calculations. We show that our conjecture is not at variance with the observed interference between different light sources. The connection to the concept of spontaneous symmetry breaking and the identification of entangled states as pointer basis states is discussed.",
                "doi": "10.1103/PhysRevA.58.4247",
                "issn": "1050-2947",
                "journal": "Physical Review A",
                "month": "nov",
                "number": "5",
                "pages": "4247--4247",
                "title": "Reply to \enquote{Comment on \enquote*{Optical coherence: {A} convenient fiction}}",
                "url": "http://link.aps.org/doi/10.1103/PhysRevA.58.4247",
                "volume": "58",
                "year": "1998"
            },),),
        ]

        self.assert_keyentrylists_equal(entries, entries_ok)





    def get_std_test_entries(self, only_keys=[], except_keys=[]):
        def ok_key(k):
            return ((not only_keys) or (k in only_keys)) and (k not in except_keys)
        return [
            k for k in (
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
            )
            if ok_key(k[0])
        ]






if __name__ == '__main__':
    unittest.main()
