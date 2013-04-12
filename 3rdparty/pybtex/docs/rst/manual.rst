=============================
The Friendly Manual of Pybtex
=============================

Using Pybtex instead of BibTeX
==============================

Pybtex is compatible with BibTeX — just type ``pybtex`` instead of
``bibtex``:

.. sourcecode:: bash

    latex foo
    pybtex foo
    latex foo
    latex foo

Unlike BibTeX, Pybtex supports multiple bibliography data formats. If you run

.. sourcecode:: bash

    pybtex -f bibtexml foo

Pybtex will read bibliography data in BibTeXML format from ``foo.bibtexml``
file instead of ``foo.bib``.
    
Using Pybtex with (experimental) pythonic bibliography styles
=============================================================

Pybtex supports bibliography styles written in Python, although this feature
is still in development. If you want to give it a try, first examine the
sources in the ``pybtex/style`` subdirectory, then run:

.. sourcecode:: bash

    pybtex -l python foo

As of now the only pythonic style available is
``pybtex/style/formatting/unsrt.py``. It is a partial and very incomplete port
of ``unsrt.bst``.

Pythonic styles are markup-independent, it is possible to format the
bibliography as HTML or plain text:

.. sourcecode:: bash

    pybtex -e pybtex -b html foo
    pybtex -e pybtex -b plaintext foo

Label and name styes are configurable:

.. sourcecode:: bash

    pybtex -e pybtex --label-style number --name-style last_first foo

Label and name styles are defined in ``pybtex/style/labels.py`` and
``pybtex/style/names.py``, look there for details.

Using Pybtex as a bibliography files converter
==============================================

Pybtex has a simple ``pybtex-convert`` utility, which can convert bibliography
files between supported formats:

.. sourcecode:: bash

    pybtex-convert foo.bib foo.yaml

The conversion is not always lossless due to limitations of storage formats:

- Native BibTeX format stores personal names as single strings, while BibTexML
  and Pybtex' YAML format store first name, last name, and other name parts
  seprately.

- BibTeXML format does not support LaTeX preambles.

- The order of keys is not preserved during the conversion (this may be fixed some day).

Using Pybtex programmatically
=============================

Using the BibTeX parser
-----------------------

.. sourcecode:: pycon

    >>> from pybtex.database.input import bibtex
    >>> parser = bibtex.Parser()
    >>> bib_data = parser.parse_file('examples/foo.bib')
    >>> bib_data.entries.keys()
    [u'ruckenstein-diffusion', u'viktorov-metodoj', u'test-inbook', u'test-booklet']
    >>> print bib_data.entries['ruckenstein-diffusion'].fields['title']
    Predicting the Diffusion Coefficient in Supercritical Fluids

(to be continued)
