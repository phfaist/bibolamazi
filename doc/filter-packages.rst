.. _filter-packages:

Filter Packages
===============

Bibolamazi filters are organized in *filter packages*. These are regular python
packages whose modules can be invoked as filters.

, i.e. a directory containing a
``__init__.py`` file, which contains python modules that implement the
bibolamazi filter API. (The ``__init__.py`` file is usually empty.)
..........

All built-in filters are part of the filter package ``bibolamazi.filters``.
Additional filter packages can be imported for instance using the ``package:``
directive (see :ref:`package: directive
<bibolamazi-config-section-pkg-directive>`).

It is very simple to create your own filter packages and provide your own
filters.  This section covers how filter packages can be imported, how to create
your own filter packages, and how to write your own filters.


.. toctree::
   :maxdepth: 2

   import-filter-package
   create-filter-package
   devel-filter-easy
   devel-filter

