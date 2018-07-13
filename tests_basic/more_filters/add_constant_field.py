#
# Simple example of a custom filter package
#



def bib_filter_entry(entry, bibolamazifile, fieldname='processed_by', value='bibolamazi-program',
                     make_value_caps=False):
    """
    This filter adds to each entry (which is not a book) an additional field
    named `fieldname` set to the constant value `value`.

    Author: Philippe Faist

    Some more doc text goes here.

    Description: Add a fixed key=value pair to all
    non-book entries

    Arguments:

      * fieldname:   the field name to insert (or replace) in all
                     bibtex entries
      * value:       the value to set the given field_name to, in
                     all bibtex entries
      * make_value_caps: turn the value into upper-case letters
    """

    # set the field fieldname to the given value in all entries except books (for example)

    if entry.type != 'book':
        if make_value_caps:
            value = value.upper()
        entry.fields[fieldname] = value

