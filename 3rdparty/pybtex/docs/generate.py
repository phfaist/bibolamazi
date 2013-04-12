#!/usr/bin/env python

import sys
from os import path

from pybtex.docgen import generate_docs

if __name__ == '__main__':
    doc_types = sys.argv[1:]
    if not doc_types:
        doc_types = ['html', 'manpages']
    generate_docs(path.dirname(__file__), doc_types)
