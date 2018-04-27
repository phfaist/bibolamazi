#
# Simple example of a custom filter package
#


from pybtex.database import Entry, Person


def bib_filter_bibolamazifile(bibolamazifile, author='One; Two; Three, Jr.',
                              title='A nice title', year=2001):
    """
    This filter adds to each entry (which is not a book) an additional field
    named `fieldname` set to the constant value `value`.

      * author :

          Specify the author list, separated by semicolons (e.g., "Maria Doe;
          John Doe")

      * title :

          The title of the book.

      * year (int) :

          The year the book was published.

    """

    # set the field fieldname to the given value in all entries except books (for example)

    bibolamazifile.bibliographyData().entries['mybook'] = Entry(
        type_='book',
        persons=dict(author=[Person(a.strip()) for a in author.split(";")]),
        fields={'title': title, 'year': str(year)}
    )
