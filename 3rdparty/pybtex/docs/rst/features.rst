======================
The Features of Pybtex
======================

Bibliography formats
====================

BibTeX
------

BibTeX format is quite simple. Those who have used BibTeX should be already
familiar with it. The others will probably catch the idea from the following
example:

.. sourcecode:: bibtex

    @BOOK{strunk-and-white,
        author = "Strunk, Jr., William and E. B. White",
        title = "The Elements of Style",
        publisher = "Macmillan",
        edition = "Third",
        year = 1979
    }


Here is a `more detailed description of the BibTeX format`_.

.. _more detailed description of the BibTeX format: http://www.miwie.org/tex-refs/html/bibtex-bib-files.html

BibTeXML
--------

`BibTeXML <http://bibtexml.sourceforge.net>`_ format attempts to combine the
simplicity of BibTeX format with the power of XML. Here is what the above
BibTeX bibliography entry wolud look like:

.. sourcecode:: xml

    <bibtex:entry id="strunk-and-white">
    <bibtex:book>
    <bibtex:title>The Elements of Style</bibtex:title>
    <bibtex:publisher>Macmillan<bibtex:publisher>
    <bibtex:edition>Third</bibtex:edition>
    <bibtex:year>1979</bibtex:year>
    <bibtex:author>
            <bibtex:person>
                <bibtex:first>William</bibtex:first>
                <bibtex:last>Strunk</bibtex:last>
                <bibtex:lineage>Jr.</bibtex:lineage>
            </bibtex:person>
            <bibtex:person>
                <bibtex:first>E.</bibtex:first>
                <bibtex:middle>B.</bibtex:first>
                <bibtex:last>White</bibtex:last>
            </bibtex:person>
    </bibtex:author>
    </bibtex:book>
    </bibtex:entry>

YAML
----

We chose to create our own format to use with Pybtex. It is quite similar to
`BibTeXML <http://bibtexml.sourceforge.net>`_
but based on `YAML <http://yaml.org>`_ instead of XML and therefore
is much less verbose.

.. sourcecode:: yaml

    strunk-and-white:
        type: book
        author:
            - first: William
              last: Strunk
              lineage: Jr.
            - first: E.
              middle: B.
              last: White
        title: The Elements of Style
        publisher: Macmillan
        edition: Third
        year: 1979


Bibliography style formats
==========================

- BibTeX ``.bst`` files
- Pybtex own pythonic `style API <style_api.txt>`_


Output formats
==============

Unlike BibTeX ``.bst`` styles, which can only output LaTeX or whatever is
hardcoded in them, Pybtex pythonic styles are output format agnostic and can
produce:

- LaTeX
- plain text
- HTML (work in progress)

Support for other formats can be added easily. If you really need it,
please `file a feature request`_.

.. _file a feature request: http://sourceforge.net/p/pybtex/bugs/new/


