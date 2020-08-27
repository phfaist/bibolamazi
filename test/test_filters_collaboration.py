import unittest
import logging
import tempfile
import os.path
import re
import shutil

from pybtex.database import Entry, Person, BibliographyData

from bibolamazi.core import blogger
from helpers import CustomAssertions
from bibolamazi.filters import collaboration
from bibolamazi.core.bibolamazifile import BibolamaziFile

logger = logging.getLogger(__name__)


class TestWorks(unittest.TestCase, CustomAssertions):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.maxDiff = None

    def _get_test_entries(self):
        return [
            ('Test2005',
             Entry("article", persons={"author": [Person("Bar, Foo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "pages": "123",
                 "journal": "Journal of Cool Stuff",
                 "title": "{Cool title goes here}",
                 "year": "2005"
             },),),
            ('Foo2007',
             Entry("article", persons={"author": [Person("{FOO Collaboration}"),
                                                  Person("Zolo", "Zoyo"),
                                                  Person("Yolo", "Yoyo"),
                                                  Person("Wolo", "Woyo")]}, fields={
                 "pages": "12",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2007"
             },),),
            ('Bar2009',
             Entry("article", persons={"author": [Person("Zolo", "Zoyo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "pages": "12132",
                 "collaboration": "BAR Collaboration",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2009"
             },),),
        ]

    def test_sets_as_author(self):

        filt = collaboration.CollaborationFilter(
            use_mode=collaboration.UseCollaborationMode('set-as-author'),
            long_list_threshold=3,
        )

        entries = self._get_test_entries()
        
        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
            ('Test2005',
             Entry("article", persons={"author": [Person("Bar, Foo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "pages": "123",
                 "journal": "Journal of Cool Stuff",
                 "title": "{Cool title goes here}",
                 "year": "2005"
             },),),
            ('Foo2007',
             Entry("article", persons={"author": [Person(last="{FOO Collaboration}")]}, fields={
                 "pages": "12",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2007"
             },),),
            ('Bar2009',
             Entry("article", persons={"author": [Person(last="{BAR Collaboration}")]}, fields={
                 "pages": "12132",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2009"
             },),),
        ]
        self.assert_keyentrylists_equal(entries, entries_ok)


    def test_sets_as_author_if_long(self):

        filt = collaboration.CollaborationFilter(
            use_mode=collaboration.UseCollaborationMode('set-as-author-if-long-list'),
            long_list_threshold=3,
        )

        entries = self._get_test_entries()
        
        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
            ('Test2005',
             Entry("article", persons={"author": [Person("Bar, Foo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "pages": "123",
                 "journal": "Journal of Cool Stuff",
                 "title": "{Cool title goes here}",
                 "year": "2005"
             },),),
            ('Foo2007',
             Entry("article", persons={"author": [Person(last="{FOO Collaboration}")]}, fields={
                 "pages": "12",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2007"
             },),),
            ('Bar2009',
             Entry("article", persons={"author": [Person(last="{BAR Collaboration}"),
                                                  Person("Zolo", "Zoyo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "pages": "12132",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2009"
             },),),
        ]
        self.assert_keyentrylists_equal(entries, entries_ok)

    def test_sets_collaboration_field(self):

        filt = collaboration.CollaborationFilter(
            use_mode=collaboration.UseCollaborationMode('set-collaboration-field'),
            long_list_threshold=3,
        )

        entries = self._get_test_entries()
        
        for k,e in entries:
            e.key = k
            filt.filter_bibentry(e)

        entries_ok = [
            ('Test2005',
             Entry("article", persons={"author": [Person("Bar, Foo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "pages": "123",
                 "journal": "Journal of Cool Stuff",
                 "title": "{Cool title goes here}",
                 "year": "2005"
             },),),
            ('Foo2007',
             Entry("article", persons={"author": [Person("Zolo", "Zoyo"),
                                                  Person("Yolo", "Yoyo"),
                                                  Person("Wolo", "Woyo")]}, fields={
                 "collaboration": "{FOO Collaboration}",
                 "pages": "12",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2007"
             },),),
            ('Bar2009',
             Entry("article", persons={"author": [Person("Zolo", "Zoyo"),
                                                  Person("Yolo", "Yoyo")]}, fields={
                 "collaboration": "{BAR Collaboration}",
                 "pages": "12132",
                 "journal": "Journal of Really Cool Stuff",
                 "title": "{Super-duper cool title goes here}",
                 "year": "2009"
             },),),
        ]
        self.assert_keyentrylists_equal(entries, entries_ok)




if __name__ == '__main__':
    blogger.setup_simple_console_logging(level=logging.DEBUG)
    unittest.main()
