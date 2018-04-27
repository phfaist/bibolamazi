
.. _devel-filter-easy:

Writing a Simple Filter
=======================

There are two ways of writing filters.  The first one, presented here, is the
quick-and-easy way, where you basically only have to define a function.  The
more elaborate way gives you additional control about more stuff you can do, but
requires a little more coding, and will be covered in the section
:ref:`devel-filter`.

To create your custom filters, first create a subdirectory with a short name
without spaces, accents or any punctuation, such as ``myfilters`` (basically
only letters and underscores are allowed). Then place in there an empty python
file called ``__init__.py`` (two double-underscores before and after the word
`init` in lowercase).  Then create in the same subdirectory a python file with
the name of your filter.  In this example, we'll call it
``add_constant_field.py``, because our filter will simply add a field with a
constant value to all the bibtex entries.

The file ``add_constant_field.py`` might look like this::

    # add_constant_field.py:
    
    import logging
    logger = logging.getLogger(__name__)
    
    def bib_filter_entry(entry, field_name='note', value='Hello world'):
        """
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
    

More doc needed ................

- the `bib_filter_entry` function may also take an argument called
  'bibolamazifile' to access properties of the bibolamazifile.



Also::

    def bib_filter_bibolamazifile(bibolamazifile, ...):

       ...

to filter the full bibliography. ...........
