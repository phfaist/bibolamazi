
Writing a New Filter
====================


.. toctree::
   :maxdepth: 2

   devel-filter-example


Developing Custom filters
-------------------------

Writing filters is straightforward. An example is provided here:
:ref:`devel-filter-example`. Look inside the filters/ directory at the existing filters
for further examples, e.g. ``arxiv.py``, ``duplicates.py`` or ``url.py``. They should be
rather simple to understand.

A filter can either act on individual entries (e.g. the ``arxiv.py`` filter), or on the
whole database (e.g. `duplicates.py`).

For your organization, it is recommended to develop your filter(s) in a custom filter
package which you keep a repository e.g. on github.com, so that the filter package can be
easily installed on the different locations you would like to run bibolamazi from.

Don't forget to make use of the *bibolamazi cache*, in case you fetch or compute values
which you could cache for further reuse. Look at for the documentation for
:py:class:`~core.bibusercache.BibUserCacheAccessor`.

There are a couple utilities provided for the filters, check the :py:mod:`filters.util`
module. In particular check out the :py:mod:`~filters.util.arxivutil` and
:py:mod:`~filters.util.auxfile` modules.

Feel free to contribute filters, it will only make bibolamazi more useful!


The Filter Module
-----------------

There are two main objects your module should define at the very least:

* a filter class, subclass of :py:class:`~core.bibfilter.BibFilter`.

* a method called ``bibolamazi_filter_class()``, which should return the filter class
  object. For example,::

    def bibolamazi_filter_class():
        return ArxivNormalizeFilter;

You may want to have a look at :ref:`devel-filter-example` for an example of a custom
filter.

There are several other functions the module may define, although they are not mandatory.

* `parse_args()` should parse an argument string, and return a tuple ``(args, kwargs)`` of
  how the filter constructor should be called. If the module does not provide this
  function, a very powerful default automatic filter option processor (based on python's
  :py:mod:`argparse` module) is built using the
  filter argument names as options names.

* `format_help()` should return a string with full detailed information about how to use
  the filter, and which options are accepted. If the module does not provide this
  function, the default automatic filter option processor is used to format a useful help
  text (which should be good enough for most of your purposes, especially if you don't
  want to reinvent the wheel).
  
  Note: the :py:attr:`~core.bibfilter.BibFilter.helptext` attribute of your
  :py:class:`~core.bibfilter.BibFilter` subclass is only used by the default automatic
  filter option processor; so if you implement `format_help()` manually, the ``helptext``
  attribute will be ignored.


Passing Arguments to the Filter
-------------------------------
