==========================
Writing Plugins for Pybtex
==========================

Starting from version 0.15, it is possible to extend Pybtex without hacking
the sources via setuptools/distribute entry points.

Entry Points
============

Here is the list of entry points supported by Pybtex:

``pybtex.database.input`` and ``pybtex.database.output``
--------------------------------------------------------

This entry points are for extending Pybtex with new bibliography formats. The
first entry point is used for reading bibliography data, the second one is
used by for writing, so you can convert your data to another format with ``pybtex-convert``.

All input and output plugin classes should inherit
``pybtex.database.input.BaseParser`` and
``pybtex.database.output.BaseWriter``, respectively.

There are also additional entry points ``pybtex.database.input.suffixes`` and
``pybtex.database.output.suffixes``, which are used for
registering default plugins for specific file suffixes.

For example, if you are writing a JSON input plugin for Pybtex, you entry points can be:

.. sourcecode:: ini

    [pybtex.database.input]
    json = pybtexjson:JSONParser

    [pybtex.database.input.suffixes]
    .json = pybtexjson:JSONParser



``pybtex.backends``
-------------------

This entry point is for adding new markup types for Pythonic bibliography
styles. Existing plugins are ``latex``, ``html``, and ``plaintext``.


``pybtex.style.labels``
-----------------------

Label styles for Pythonic bibliography styles.


``pybtex.style.names``
----------------------

Name styles for Pythonic bibliography styles.


``pybtex.style.formatting``
---------------------------

Pythonic bibliography styles themselves. The only style existing is ``unsrt``.
Please contribute more styles. :)


Registering Plugins
===================

See `Distribute's documentation
<http://packages.python.org/distribute/setuptools.html#extensible-applications-and-frameworks>`_.


Example Plugins
===============

An example project directory with two simple plugins and a ``setup.py`` file can
be found in ``examples/sample_plugins``.
