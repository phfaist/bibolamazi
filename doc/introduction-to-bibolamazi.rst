
Introduction to Bibolamazi
==========================

Bibolamazi lets you prepare consistent and uniform BibTeX files for your LaTeX
documents. It lets you prepare your BibTeX entries as you would like them to be---adding
missing or dropping irrelevant information, capitalizing names or turning them into
initials, converting unicode characters to latex escapes, etc.


Example Usage Scenario
----------------------

A typical scenario of Bibolamazi usage might be:

- You use a bibliography manager, such as Mendeley_, to store all your references. You
  have maybe configured e.g. Mendeley_ to keep a BibTeX file
  ``Documents/bib/MyLibrary.bib`` in sync with your library;

- You're working, say on a document ``mydoc.tex``, which cites entries from ``MyLibrary.bib``;

- You like to keep URLs in your entries in your Mendeley library, because it lets you open
  the journal page easily, but you don't want the URLs to be displayed in the bibliography
  of your document ``mydoc.tex``. But you've gone through all the bibliography styles, and
  really, the one you prefer unfortunatly does display those URLs.

- You don't want to edit the file ``MyLibrary.bib``, because it would just be overwritten
  again the next time you open Mendeley. The low-tech solution (what people generally do!) 
  would then be to export the required citations from Mendeley to a new bibtex file, or
  copy ``MyLibrary.bib`` to a new file, and edit that file manually.

- To avoid having to perform this tedious task manually, you can use Bibolamazi to prepare
  the BibTeX file as you would like it to be. For this specific task, for example, you
  would perform the following steps:

  - Create a bibolamazi file, say, ``mydoc.bibolamazi.bib``;

  - Specify as a source your original ``MyLibrary.bib``::

      src: ~/Documents/bib/MyLibrary.bib

  - Give the following filter command::

      filter: url -dStrip

    which instructs to strip all urls (check out the documentation of the `url` filter in
    the `Help & Reference Browser`)

  - Run bibolamazi.

  - Use this file as your bibtex bibliography, i.e. in your LaTeX document, use::

      \bibliography{mydoc.bibolamazi}

  Note that you can then run Bibolamazi as many times as you like, to update your file,
  should there have been changes to your original ``MyLibrary.bib``, for example.


.. _Mendeley: http://mendeley.com/


Teaser: Features
----------------

The most prominent features of Bibolamazi include:

- A `duplicates` filter allows you to efficiently collaborate on LaTeX documents: in your
  shared LaTeX document, each collaborator may cite entries in his own bibliography
  database (each a source in the bibolamazi file). Then, if instructed to do so,
  bibolamazi will detect when two entries are duplicates of each other, merge their
  information, and produce LaTeX definitions such that the entries become aliases of one
  another. Then both entry keys will refer to the same entry in the bibliography.

  **Catch**: there is one catch to this, though, which we can do nothing about: if two
  entries in two different database share the same key, but refer to different
  entries. This may happen, for example, if you have automatic citation keys of the form
  ``AuthorYYYY``, and if the author published several papers that same year.
  
- A powerful `arxiv` filter, which can normalize the way entries refer to the arXiv.org
  online preprint repository. It can distinguish between published and unpublished
  entries, and its output is highly customizable.

- A general-purpose `fixes` filter provides general fixes that are usually welcome in a
  BibTeX files. For example, revtex doesn't like Mendeley's way of exporting swedish 'Å',
  for example in ``Åberg``, as ``\AA berg``, and introduces a space between the 'Å' and
  the 'berg'. This filter allows you to fix this.

- Many more! Check out the filter list in the `Help & Reference Browser` window of
  Bibolamazi!

