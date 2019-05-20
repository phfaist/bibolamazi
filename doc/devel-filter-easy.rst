.. _devel-filter-easy:

Writing a Simple Filter
=======================

There are two ways of writing filters.  The first one, presented here, is the
quick-and-easy way, where you basically only have to define a function.  The
more elaborate way gives you additional control about more stuff you can do, but
requires a little more coding, and will be covered in the section
:ref:`devel-filter`.

First of all, before create a custom filter, you should :ref:`create your own
filter package <create-filter-package>`.  The python files here will refer to
individual python files within the filter package that you will have created.

In you custom filter package, create a python file with the name of your future
filter and the extension ``.py``.  In this example, we'll call it
``add_constant_field.py``, because our filter will simply add a field with a
constant value to all the bibtex entries.

The file ``add_constant_field.py`` might look like this::

    # add_constant_field.py:
    
    from pybtex.database import Entry, Person

    import logging
    logger = logging.getLogger(__name__)
    
    def bib_filter_entry(entry, field_name='note', value='Hello world'):
        """
        Author: Philippe Faist (C) 2019 GPL 3+

        Description: Add a fixed field to each entry

        This filter adds to each entry an additional field named `field_name`
        set to the constant value `value`.

        Arguments:

          * field_name : the field name to insert (or replace) in all
                         bibtex entries
          * value :      the value to set the given field_name to, in
                         all bibtex entries
        """
    
        # write debug messages, which are seen in verbose mode
        logger.debug("Taking care of entry %s", entry.key)

        # set the field field_name to the given value:
        entry.fields[field_name] = value
    

There are two possible ways a filter can act on a bibliography database.  Either
it can filter all entries individually, where each fix for each entry does not
depend on any other entry; or the filter can act on the database as a whole.
For instance, a filter that fixes URLs or creates author initials would act
entry-by-entry, whereas a duplicates detector would act on the database as a
whole.

In the above example, we act on each entry individually, because we defined a
function called ``filter_bib_entry()``.  This function must take a first
argument called ``entry``.  This will be the entry to possibly modify.  Any
additional arguments to the function are automatically scanned and set according
to options of the form ``-sKey=Value`` and ``-dKey`` in the bibolamazi file.
You can see this by clicking on the "? info" button to open you own filter's
help page (in the bibolamazi application), or by running
``bibolamazi --filterpackage=/path/to/mypackage --help add_constant_field`` (in
the bibolamazi command-line tool).

In the above example, we modify the entry's fields to add a field with the given
field name and field value.  For instance, we could use this filter as it is in
a bibolamazi file with the directives::

  package: /path/to/mypackage

  filter: add_constant_field -sFieldName=annote
                             -sValue='automatic annotation added by my filter'

with the effect of adding the field ``annote = {automatic annotation added by my
filter}`` to all bibtex entries.

The function `bib_filter_entry()` may also take an argument called
``bibolamazifile`` to access properties of the bibolamazifile.  The argument
``bibolamazifile`` would then be a
:py:class:`bibolamazi.core.bibolamazifile.BibolamaziFile` instance.

The ``entry`` argument is an object of type ``pybtex.database.Entry``.  See more
in the `pybtex documentation
<https://docs.pybtex.org/api/parsing.html#pybtex.database.Entry>`_.

An inconvenience of defining the ``bib_filter_entry()`` as above in the "simple
filter" definition method is that you can't pre-process the user's options once
before filtering all entries.  Because this function will be called many times,
it might be necessary in certain cases to perform some task once only, compute
some value or get some data, and then filter all entries using this data.  For
this, you should change to a filter-class based filter module, as described
:ref:`in the next section <devel-filter>`.

If your filter is supposed to act on the whole bibliography database in one go,
then you should define the function ``bib_filter_bibolamazifile()`` instead of
``bib_filter_entry()``. For instance, we could define a filter
``remove_books.py`` as follows::

    # remove_books.py:
    
    from pybtex.database import Entry, Person

    import logging
    logger = logging.getLogger(__name__)

    def bib_filter_bibolamazifile(bibolamazifile):
        r"""
        Author: Philippe Faist, (C) 2019, GPL 3+

        Description: Remove all entries that are of type 'book'

        I have no idea why you'd want to do this, but it provides a nice example
        of how to write a filter that acts on the full bib database.
        """

        bibdata = bibolamazifile.bibliographyData()

        keys_for_removal = []

        for key, entry in bibdata.entries.items():
            if entry.type == 'book':
                # mark this key for removal from database
                keys_for_removal.append(key)

        # remove entries only after we've done iterating the database
        for key in keys_for_removal:
            del bibdata.entries[key]


In this example, we iterate over the full bibliography database and remove all
entries that are of the type ``book``.

The argument ``bibolamazifile`` is a
:py:class:`bibolamazi.core.bibolamazifile.BibolamaziFile` instance.

You should proceed by trial and error, and you can get inspired by the existing
built-in filters, see
`https://github.com/phfaist/bibolamazi/tree/master/bibolamazi/filters
<https://github.com/phfaist/bibolamazi/tree/master/bibolamazi/filters>`_.

Continue reading :ref:`devel-filter` for more in-depth information about how
bibolamazi filters work.  Really, the "easy" filter definitions presented here
are a convenient shorthand for defining a full filter class as described in the
next section.
