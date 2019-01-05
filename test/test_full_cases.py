
import unittest

import os.path
import tempfile
import shutil
import logging

from bibolamazi.core.bibolamazifile import BibolamaziFile
import bibolamazi.core.main

import helpers

from bibolamazi.core import blogger


class FullCaseTester(object):
    def __init__(self):
        super(FullCaseTester, self).__init__()

    def _run_full_case_test(self, name):

        logging.getLogger(__name__).info(
            "********** RUNNING \"FULL CASE\" TEST %s **********",
            name
        )
        
        tmpdir = tempfile.mkdtemp()
        try:
            tmpbib = os.path.join(tmpdir, name+'.bibolamazi.bib')
            full_cases_dir = os.path.realpath(
                os.path.abspath(os.path.join(os.path.dirname(__file__), 'full_cases'))
            )
            shutil.copyfile(os.path.join(full_cases_dir, name+'.bibolamazi.bib'),
                            tmpbib)
            # symlink source files
            os.symlink(os.path.join(full_cases_dir, 'srcbib'),
                       os.path.join(tmpdir, 'srcbib'))
            # ... and any necessary tex/aux files
            for auxfext in ('.tex', '.aux', '_jobname.tex', '_jobname.aux', '_job.tex', '_job.aux'):
                if os.path.exists(os.path.join(full_cases_dir, name + auxfext)):
                    shutil.copyfile(os.path.join(full_cases_dir, name + auxfext),
                                    os.path.join(tmpdir, name + auxfext))

            
            bf_orig = BibolamaziFile(tmpbib)

            # run bibolamazi on the file
            bibolamazi.core.main.run_bibolamazi(tmpbib)

            bf_after = BibolamaziFile(tmpbib)

            # compare the contents before and after the run
            self.assertEqual(bf_orig.bibliographyData(), bf_after.bibliographyData())

            # run bibolamazi again on the file, using the cache this time
            bibolamazi.core.main.run_bibolamazi(tmpbib)

            bf_after_2 = BibolamaziFile(tmpbib)

            # compare the contents before and after the run
            self.assertEqual(bf_orig.bibliographyData(), bf_after_2.bibliographyData())

        finally:
            shutil.rmtree(tmpdir)


class TestFullCases(unittest.TestCase, helpers.CustomAssertions, FullCaseTester):

    def test_0(self):
        self._run_full_case_test('test0')

    def test_1(self):
        self._run_full_case_test('test1')

    def test_2(self):
        self._run_full_case_test('test2')

    def test_5(self):
        self._run_full_case_test('test5')

    def test_6(self):
        self._run_full_case_test('test6')

    def test_7(self):
        self._run_full_case_test('test7')

    def test_8(self):
        self._run_full_case_test('test8')

    def test_9(self):
        self._run_full_case_test('test9')

    def zzztest(self):
        self._run_full_case_test('zzztest')



if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=logging.INFO)
    unittest.main()
