.. _create-filter-package:

Creating a new filter package
=============================

Creating a filter package is as easy as creating a directory and putting an
empty ``__init__.py`` file in there. That's it. That's your minimal Python
package.

For instance, let us create a filter package called `mypackage`.  Create a
folder called `mypackage`.  Then create an empty file called ``__init__.py`` in
that folder.  Instead of `mypackage`, you may use the name that you like.  Keep
in mind, though, that filter package names must be valid Python identifiers, so
you need to avoid hyphens, spaces, and accents; you should only use letters,
underscores and digits, and the name can't start with a digit.

Then you can put other python files in the package (say ``myfirstfilter.py`` and
``mysecondfilter.py``), which define filters.  The Python file name without the
`.py` extension is the name of the filter that you can use in the bibolamazi
file.  For instance, we sould have the following file structure::

  mypackage/
    - __init__.py        (empty file)
    - myfirstfilter.py   (definition of filter myfirstfilter)
    - mysecondfilter.py  (definition of filter mysecondfilter)

You can then import this filter package in your bibolamazi file using, for
instance, the directive::

  package: /path/to/mypackage

You can then use `myfirstfilter` and `mysecondfilter` as normal filters in your
bibolamazi file.  In the following sections, we'll detail how to write custom
filters so that they can do useful stuff, i.e., we'll see how we should go about
to code the contents of ``myfirstfilter.py`` and ``mysecondfilter.py``.
