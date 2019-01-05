
from __future__ import unicode_literals, print_function
from future.utils import iteritems
from builtins import str as unicodestr

# monkey-patch pybtex
import bibolamazi.init

import sys
import io
import pybtex.database.input.bibtex as inputbibtex
import pybtex.database.output.bibtex as outputbibtex

import fileinput
import json

parser = inputbibtex.Parser()

data = ""
for x in fileinput.input(): data += x

bib_data = None
with io.StringIO(data) as stream:
    bib_data = parser.parse_stream(stream)


def doentry(key, entry):

    persons = '{'
    for role in ('author', 'editor', ):
        if role in entry.persons:
            persons += (json.dumps(role)+": ["
                        +",".join([ "Person("+json.dumps(unicodestr(x))+")" for x in entry.persons[role]])
                        +"],")
    persons += '}'
    
    print("    ({}, Entry({}, persons={}, fields={},),),"
          .format(json.dumps(key),
                  json.dumps(entry.type),
                  persons,
                  json.dumps(dict(entry.fields),indent=8)))



print("[")
for key, entry in iteritems(bib_data.entries):
    doentry(key, entry)
print("]")
