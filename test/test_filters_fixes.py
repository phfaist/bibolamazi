
# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import unittest

from helpers import assert_keyentrylists_equal, assert_entries_equal
from pybtex.database import Entry, Person
from bibolamazi.filters.fixes import FixesFilter

class TestWorks(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestWorks, self).__init__(*args, **kwargs)

        self.maxDiff = None




    def test_fixSpcAfterEsc(self):

        filt = FixesFilter(fix_space_after_escape=True)

        entries = [
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
        ]
        
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
                







    def test_fixSpcAfterEsc_utf8ToLtx(self):

        filt = FixesFilter(encode_utf8_to_latex=True)

        entries = [
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
        ]

        self.assert_keyentrylists_equal(entries, entries_ok)


    def assert_keyentrylists_equal(self, e1, e2):
        assert_keyentrylists_equal(self, e1, e2)




if __name__ == '__main__':
    from bibolamazi.core import blogger
    blogger.setup_simple_console_logging(level=1)
    unittest.main()
