
import unittest

import os.path
import tempfile
import shutil
import logging
import time

from bibolamazi.core.bibolamazifile import BibolamaziFile
import bibolamazi.core.main

# import pybtex *after* bibolamazi (might need monkey-patching)
import pybtex.database.input.bibtex

import helpers

from bibolamazi.core import blogger

import bibolamazi.core.bibfilter.factory as filters_factory
from bibolamazi.core.bibfilter import pkgprovider, pkgfetcher_github

#
# set up remote filter package fetching, usually this is done in main.py or bibolamaziapp.py
#
filters_factory.package_provider_manager = pkgprovider.PackageProviderManager()
filters_factory.package_provider_manager.allow_remote = True
filters_factory.package_provider_manager.registerPackageProvider(
    pkgfetcher_github.GithubPackageProvider(None)
)


#
# TO DEBUG: Create an empty subdir in this directory called '_tmpdir' and set
# `use_mkdtemp=False` below.  The processed bibolamazi file will be left there,
# we can diff with the original to see what happened.  Don't forget to clean up
# the directory for each run.
#
use_mkdtemp = True #False
localtmpdir = '_tmpdir' # used if use_mkdtemp=False




class FullCaseTester:
    def __init__(self):
        super().__init__()


    def _run_full_case_test(self, name):

        logging.getLogger(__name__).info(
            "********** RUNNING \"FULL CASE\" TEST %s **********",
            name
        )
        
        if use_mkdtemp:
            tmpdir = tempfile.mkdtemp()
        else:
            tmpdir = os.path.abspath(os.path.join(os.path.dirname(__file__), localtmpdir))

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
            # symlink extra filter package source
            os.symlink(os.path.join(full_cases_dir, 'more_filters'),
                       os.path.join(tmpdir, 'more_filters'))
            # ... and any necessary tex/aux files
            for auxfext in ('.tex', '.aux', '_jobname.tex', '_jobname.aux', '_job.tex', '_job.aux'):
                if os.path.exists(os.path.join(full_cases_dir, name + auxfext)):
                    shutil.copyfile(os.path.join(full_cases_dir, name + auxfext),
                                    os.path.join(tmpdir, name + auxfext))

            time.sleep(0.5)
            
            bfile = BibolamaziFile(tmpbib)

            parser = pybtex.database.input.bibtex.Parser()
            bf_orig_data = parser.parse_string(bfile.rawRest())

            # run bibolamazi on the file -- run all filters
            for filtr in bfile.filters():
                bfile.runFilter(filtr)

            bfile.saveToFile() # for debugging

            # compare the contents before and after the run
            self.assert_keyentrylists_equal(list(bf_orig_data.entries.items()),
                                            list(bfile.bibliographyData().entries.items()))

        finally:
            if use_mkdtemp:
                shutil.rmtree(tmpdir)



class TestFullCases(unittest.TestCase, FullCaseTester, helpers.CustomAssertions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.maxDiff = None


    def test_0(self):
        self._run_full_case_test('test0')

    def test_1(self):
        self._run_full_case_test('test1')

    def test_2(self):
        self._run_full_case_test('test2')

    def test_3(self):
        self._run_full_case_test('test3')

    def test_5(self):
        self._run_full_case_test('test5')

    def test_5a(self):
        self._run_full_case_test('test5a')

    def test_6(self):
        self._run_full_case_test('test6')

    def test_7(self):
        self._run_full_case_test('test7')

    # test8 used to be inspirehep -- see now test_filters_citeinspirehep.py
    #def test_8(self):
    #    self._run_full_case_test('test8')

    def test_9(self):
        self._run_full_case_test('test9')

    def zzztest(self):
        self._run_full_case_test('zzztest')

    @helpers.test_requires_github_access()
    def test_github_remote(self):
        self._run_full_case_test('test_github_remote')



if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=logging.INFO)
    unittest.main()
