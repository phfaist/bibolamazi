
from __future__ import print_function, unicode_literals
from builtins import str as unicodestr

import unittest

from pybtex.database import Entry, Person
from bibolamazi.filters.markauthor import MarkAuthorFilter


class TestWorks(unittest.TestCase):

    def test_exact(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Albert Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='exact')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_exact_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('A. Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='exact')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), 'Einstein, A.')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_initial(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Albert Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='initial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_initial_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('A. Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='initial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_initial_2b(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('A Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='initial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_initial_3(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Al Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='initial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'Einstein, Al')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_partial(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Albert Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='partial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_partial_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('A Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='partial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_partial_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Al Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='partial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')

    def test_partial_2(self):
        entry = Entry('article', fields={'url': 'https://example.com/doi/xfkdnsafldasknf'},
                      persons={'author': [Person('Al. Einstein'),
                                          Person('B. Podolsky'),
                                          Person('N. Rosen')]})
        n = MarkAuthorFilter(name='Albert Einstein', replace_by=r'\alberteinstein',
                             match_mode='partial')
        n.filter_bibentry(entry)
        self.assertEqual(unicodestr(entry.persons['author'][0]), r'\alberteinstein')
        self.assertEqual(unicodestr(entry.persons['author'][1]), 'Podolsky, B.')
        self.assertEqual(unicodestr(entry.persons['author'][2]), 'Rosen, N.')



if __name__ == '__main__':
    from bibolamazi.core import blogger
    blogger.setup_simple_console_logging(level=1)
    unittest.main()
