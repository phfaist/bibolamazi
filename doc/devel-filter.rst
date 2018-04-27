
.. _devel-filter:

Writing a New Filter (Full Version)
===================================


Here we document how filters work in their full glory. For a quick start, you
might want to read first :ref:`how to develop a quick-n-dirty filter
<devel-filter-easy>`.

.. toctree::
   :maxdepth: 2

   devel-filter-example


Developing Custom filters
-------------------------

Writing filters is straightforward. An example is provided here:
:ref:`devel-filter-example`. Look inside the ``bibolamazi/filters/`` directory at the
existing filters for further examples, e.g. ``arxiv.py``, ``duplicates.py`` or
``url.py``. They should be rather simple to understand.

A filter can either act on individual entries (e.g. the ``arxiv.py`` filter), or on the
whole database (e.g. `duplicates.py`).

For your organization, it is recommended to develop your filter(s) in a custom filter
package which you keep a repository e.g. on github.com, so that the filter package can be
easily installed on the different locations you would like to run bibolamazi from.

Don't forget to make use of the *bibolamazi cache*, in case you fetch or compute values
which you could cache for further reuse. You should access caches through the
:py:class:`~bibolamazi.core.bibusercache.BibUserCacheAccessor` class. Look at for the
documentation for the :py:mod:`~bibolamazi.core.bibusercache` module. Look at examples
most of all!! *(TODO: add documentation about caches)*

There are a couple utilities provided for the filters, check the
:py:mod:`bibolamazi.filters.util` module. In particular check out the
:py:mod:`~bibolamazi.filters.util.arxivutil` and
:py:mod:`~bibolamazi.filters.util.auxfile` modules.

Feel free to contribute filters, it will only make bibolamazi more useful!


The Filter Module
-----------------

There are two main objects your module should define at the very least:

* a filter class, subclass of :py:class:`~bibolamazi.core.bibfilter.BibFilter`.

* a method called ``bibolamazi_filter_class()``, which should return the filter class
  object. For example::

    def bibolamazi_filter_class():
        return ArxivNormalizeFilter

You may want to have a look at :ref:`devel-filter-example` for an example of a custom
filter.

Your filter should log error, warning, information and debug messages to a logger obtained
via Python's `logging mechanism <https://docs.python.org/2/library/logging.html>`_, as
demonstrated in the example.


Passing Arguments to the Filter
-------------------------------

Command line arguments passed to the filter in the user's bibolamazi config section are
parsed into Python arguments to the filter class' constructor. The translation is rather
intuitive: each argument to the filter may be specified as an option, either using the
syntax ``--use-uppercase=value`` or ``--use-uppercase value``, where underscores are
replaced by dashes, or using the Ghostscript-like syntax ``-dUseUppercase`` or
``-dUseUppercase=false``, or for other types ``-sMode=fixed``.

Some remarks:

- to each filter argument corresponds a command-line option starting with ``--``, where
  underscores are replaced by dashes. The command-line takes a single mandatory argument
  (except for arguments declared as booleans in their arg-docs, see :ref:`filter_argdocs`
  below).

- to each filter argument, corresponds a command-line option starting with ``-d`` or
  ``-s``, using the syntax ``-dFilterOptionName``, ``-dFilterOptionName=Value`` or
  ``-sFilterOptionName=Value``. The ``-d`` variant is used to specify boolean option
  values, the ``-s`` variant any other type. The ``FilterOptionName`` is obtained by
  camel-casing the filter python argument: for example, if the filter constructor accepts
  an argument named ``use_uppercase_chars``, then the corresponding camel-cased version
  will be ``UseUppercaseChars``. (See note below on case sensitivity.)

- each filter argument may be documented using :ref:`filter_argdocs`. This information
  will appear in the filter help text.

- if the filter constructor accepts a ``**kwargs``, then any additional option-value pairs
  given as ``-sKey=Value`` or ``-dKey`` or ``-dKey=Value`` are passed on to the filter
  constructor's ``kwargs``.

- if the filter constructor accepts a ``*args``, then any additional positional arguments
  on the command line is passed to that ``*args`` parameter. The ordering of positional
  and optional arguments on the command-line make no difference. (Note that this also
  works this way if not all the previous declared arguments are specified. There's some
  python hacking in there ;) )


.. note::

   If even a single filter argument uses an uppercase letter, then the option parser will
   not convert any letter casing, and all option names will have the exact same letter
   casing as the filter arguments. Similarly, no camel-casing will occur with the
   ``-s...`` or ``-d...`` options.


Filter General Help Documentation
---------------------------------

The filter class should declare the members ``helpauthor``, ``helpdescription`` and
``helptext`` with meaningful help text:

  - ``helpauthor`` should be a short one-line description of the filter and contributor
    with license. E.g.::

      ArXiv clean-up filter by Philippe Faist, (C) 2013, GPL 3+

  - ``helpdescription`` is a brief description of what the filter does. This is displayed
    right after the *Usage* section in the help text, and before the filter arguments
    description.

  - ``helptext`` is a long description of what the filter exactly does, how to use it, the
    advantages, tricks, pitfalls, etc.

In the built-in filters, as well as the examples, the text is declared outside of the
class (see ``HELP_AUTHOR`` etc.) so that we don't have to deal with the indentation (and
in the class, we only have ``helpauthor=HELP_AUTHOR`` etc.). That's perfectly fair and
completely optional.


.. _filter_argdocs:

Argdocs: Filter Argument Documentation
--------------------------------------

The docstring of the filter constructor is parsed in a special way. Documentation of the
function arguments are specially parsed: they should have the form::

  - argument_name(type): Description of the argument. The description may
    span over several lines.
  - other_argument_name: Description of the other option. Notice that the
    type is optional and will default to a simple string.

This information will be displayed when running ``bibolamazi --help filtername``.

If a `type` is specified, it should be a name of a python type, or a type which is
available in the namespace of the filter module. The filter factory will attempt to
convert the given string to the specified type when calling the filter constructor. If the
given `type` is a custom type, and it has a docstring, then the docstring is included in
the "Note on Filter Options Syntax" section of the help text.

There are some convenient predefined types for filter arguments, all defined in the module
:py:mod:`bibolamazi.bibfilter.argtypes`:

    - :py:class:`~bibolamazi.core.bibfilter.argtypes.CommaStrList`: a comma-separated list
      of strings. This type may directly be used as a list type.

    - :py:func:`~bibolamazi.core.bibfilter.argtypes.enum_class`: a function which returns
      a custom class which represents an enumeration value of several options.

Maybe look at the built-in filters and other examples to get an idea.

More doc should come here at some point in the future..........


Customizing Default Behavior
----------------------------

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
