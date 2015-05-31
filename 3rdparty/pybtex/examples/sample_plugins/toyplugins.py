# Copyright (c) 2011, 2012  Andrey Golovizin
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Sample Pybtex plugins."""


import imp

from pybtex.utils import OrderedCaseInsensitiveDict

from pybtex.database.output import BaseWriter
from pybtex.database.input import BaseParser
from pybtex.database import BibliographyData
from pybtex.database import Entry, Person


class PythonWriter(BaseWriter):
    """Bibliography output plugin which formats the data as Python code."""

    def write_stream(self, bib_data, stream):
        print >>stream, repr(bib_data)


class PythonParser(BaseParser):
    """Bibliography parser plugin which loads the data from Python code."""

    def parse_stream(self, stream):
        context = {
            'BibliographyData': BibliographyData,
            'OrderedCaseInsensitiveDict': OrderedCaseInsensitiveDict,
            'Entry': Entry,
            'Person': Person,
        }
        code = stream.read()
        self.data = eval(code, context)
