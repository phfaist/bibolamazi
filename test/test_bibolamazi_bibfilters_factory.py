
import unittest

import bibolamazi.core.bibfilter.factory as bffactory
import bibolamazi.filters


class TestWorks(unittest.TestCase):
    
    def test_works_1(self):

        m = bffactory.get_module('arxiv')
        from bibolamazi.filters import arxiv

        self.assertTrue( id(m) == id(arxiv) )


    def test_parses_options(self):

        arxivf = bffactory.make_filter('arxiv', '-sMode=eprint  --unpublished-mode=unpublished-note')

        self.assertEqual(str(arxivf.mode), 'eprint')
        self.assertEqual(str(arxivf.unpublished_mode), 'unpublished-note')



if __name__ == '__main__':
    from bibolamazi.core import blogger
    blogger.setup_simple_console_logging(level=1)
    unittest.main()
