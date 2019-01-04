
from __future__ import print_function, unicode_literals
from builtins import str as unicodestr

import unittest

from pybtex.database import Entry, Person
from bibolamazi.filters.nameinitials import NameInitialsFilter


class TestWorks(unittest.TestCase):

    def test_1(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Albert Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N Rosen')]})
        n = NameInitialsFilter()
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), 'Einstein, A.')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')
    
    def test_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Albert Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N Rosen')]})
        n = NameInitialsFilter(only_single_letter_firsts='True')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), 'Einstein, Albert')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_3(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person("Dupont, Fran\\c cois"),
                                          Person('\\AA sm\\"ussen, Erik'),
                                          Person("Fr\\'ed\\'eric Dupond"),
                                          Person("{\\AA sm\\o ssen}, Erik"),
                                          Person("{Van \\AA sm\\o ssen}, Erik"),
                                          Person("Cr{\\'e}peau, Claude"),
                                          Person("Alhambra, {\\'A}lvaro"),
                                          Person("Dupuis, Fr\\'ed{\\'e}ric"),
                                          Person("Brand{\\~{a}}o, F."),]})
        n = NameInitialsFilter(names_to_utf8=True)
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), 'Dupont, F.')
        self.assertEqual(unicodestr(entry.persons['author'][1]), u'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}sm\N{LATIN SMALL LETTER U WITH DIAERESIS}ssen, E.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Dupond, F.')
        self.assertEqual(unicodestr(entry.persons['author'][3]), '{\N{LATIN CAPITAL LETTER A WITH RING ABOVE}sm\N{LATIN SMALL LETTER O WITH STROKE}ssen}, E.')
        self.assertEqual(unicodestr(entry.persons['author'][4]), '{Van \N{LATIN CAPITAL LETTER A WITH RING ABOVE}sm\N{LATIN SMALL LETTER O WITH STROKE}ssen}, E.')
        self.assertEqual(unicodestr(entry.persons['author'][5]), 'Cr\N{LATIN SMALL LETTER E WITH ACUTE}peau, C.')
        self.assertEqual(unicodestr(entry.persons['author'][6]), 'Alhambra, \N{LATIN CAPITAL LETTER A WITH ACUTE}.')
        self.assertEqual(unicodestr(entry.persons['author'][7]), 'Dupuis, F.')
        self.assertEqual(unicodestr(entry.persons['author'][8]), 'Brand\N{LATIN SMALL LETTER A WITH TILDE}o, F.')


if __name__ == '__main__':
    from bibolamazi.core import blogger
    blogger.setup_simple_console_logging(level=1)
    unittest.main()
