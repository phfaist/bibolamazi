=======================
The Style API of Pybtex
=======================

Well, to tell the truth, the style API is still undergoing heavy development
and is far from being finished yet.

Here is what it looks like.

Rich text
=========

Pybtex was designed to be able to output bibliographies in multiple formats.
It means that bibliograhy formatting functions can't just return things like
``\emph{editor}`` or ``<i>journal</i>``. We have a simple language for
producing formatted text:

.. sourcecode:: pycon

    >>> from pybtex.richtext import Text, Tag
    >>> from pybtex.backends import latex, html
    >>> text = Text('This is an example of a ', Tag('emph', 'rich'), ' text.')
    >>> print text.render(html.Backend())
    This is an example of a <em>rich</em> text.
    >>> print text.render(latex.Backend())
    This is an example of a \emph{rich} text.


Template language
=================

BibTeX uses has a simple stack oriented language for defining bibliography
styles. This is what is inside of ``.bst`` files.  For a Pythonic bibliography
processor it is natural to use Python for writing styles. A Pybtex style file
is basically a Python module containing a class named ``Formatter``. This
class has methods like ``format_article``, ``format_book``, etc. They accept a
bibliography entry (an instance of ``pybtex.database.Entry`` class) and return a
formatted entry (an instance of ``pybtex.richtes.Text``).

.. sourcecode:: python

    from pybtex.style.formatting import BaseStyle
    from pybtex.richtext import Text, Tag

    class MyStyle(BaseStyle):
        def format_article(self, entry):
            return Text('Article ', Tag('em', entry.fields['title']))

To make things easier we designed a simple template language:

.. sourcecode:: python

    from pybtex.style.formatting import BaseStyle, toplevel
    from pybtex.style.template import field, join, optional

    class MyStyle(BaseStyle):
        def format_article(self, entry):
            if entry.fields['volume']:
                volume_and_pages = join [field('volume'), optional [':', pages]]
            else:
                volume_and_pages = words ['pages', optional [pages]]
            template = toplevel [
                self.format_names('author'),
                sentence [field('title')],
                sentence [
                    tag('emph') [field('journal')], volume_and_pages, date],
            ]
            return template.format_data(entry)

Is that all?
============

More documentation will be written when our style API
gets some form. Use the source for now.
