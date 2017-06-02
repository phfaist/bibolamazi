
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
        self.assertEqual(str(entry.persons['author'][0]), 'Einstein, A.')
        self.assertEqual(str(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(str(entry.persons['author'][2]), 'Rosen, N.')
    
    def test_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Albert Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N Rosen')]})
        n = NameInitialsFilter(only_single_letter_firsts='True')
        n.filter_bibentry(entry)
        self.assertEqual(str(entry.persons['author'][0]), 'Einstein, Albert')
        self.assertEqual(str(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(str(entry.persons['author'][2]), 'Rosen, N.')


if __name__ == '__main__':
    from bibolamazi.core import blogger
    blogger.setup_simple_console_logging(level=1)
    unittest.main()
