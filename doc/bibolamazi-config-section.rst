

.. _bibolamazi-configuration-section:

Bibolamazi's configuration section
==================================


If you open the Bibolamazi application and open your bibolamazi file (or create
a new one), you'll immediately be prompted to edit its configuration section.

Syntax
------

The configuration section should contain instructions of the form::

    keyword: <instruction>

Possible instructions are sources, with the ``src:`` keyword, or filters, with
the ``filter:`` keyword. All source instructions must preceed any filters.

You may also include comments in the configuration section. Any line starting
with two percent signs ``%%`` will be ignored by bibolamazi::

    %% This line is a comment and will be ignored by bibolamazi.

Comments must be on a line of their own.


Specifying sources
------------------

Sources are where your 'original' bibtex entries are stored, the ones you would
like to process. This is typically a bibtex file which a reference manager such
as Mendeley keeps in sync.

Sources are specified with the ``src:`` keyword. As an example::

    src: mysource.bib

You should specify one or more files from which entries should be read. If more
than one file is given, only the FIRST file that exists is read. This is useful
for example if on different computers your bibtex source is in different
places::

    src: /home/philippe/bibtexfiles/mylibrary.bib /Users/philippe/bibtexfiles/mylibrary.bib

You may also specify HTTP or FTP URLs. If your filename or URL contains spaces,
enclose the name in double quotes: ``"My Bibtex Library.bib"``.

To specify several sources that should be read independently, simply use
multiple ``src:`` commands::

    src: file1.bib [alternativefile1.bib ...]
    src: file2.bib [alternativefile2.bib ...]
    [...]

This would collect all the entries from the first existing file of each ``src:``
command.

Specifying filters
------------------

Once all the entries are collected from the various sources, you may now apply
filters to them.

A filter is applied using the ``filter:`` command::

    filter: filtername [options and arguments]

Filters usually accept options and arguments in a shell-like fashion, but this
may vary in principle from filter to filter. For example, one may use the
`arxiv` filter to strip away all arXiv preprint information from all published
entries, and normalize unpublished entries to refer to the arxiv in a uniform
fashion::

    filter: arxiv --mode=strip --unpublished-mode=eprint

In the Bibolamazi application, when editing filter options you can click on the
"? info" button to get information about that filter.

If you are using the command-line bibolamazi program, a full list of options can
be obtained with::

    > bibolamazi --help <filtername>

and a list of available filters can be obtained by running::

    > bibolamazi --list-filters

**Note:** Filters are organized into *filter packages* (see below). A filter is
searched in each filter package until a match is found. To force the lookup of a
filter in a specific package, you may prefix the package name to the filter,
e.g.::

    filter: myfilterpackage:myfiltername --option1=val1  ...


Example/Template Configuration Section
--------------------------------------

::

    %% BIBOLAMAZI configuration section.
    %% Additional two leading percent signs indicate comments in the configuration.
    
    %% **** SOURCES ****
    
    %% The _first_ accessible file in _each_ source list will be read and filtered.
    
    src:   <source file 1> [ <alternate source file 1> ... ]
    src:   <source file 2> [ ... ]
    
    %% Add additional sources here. Alternative files are useful, e.g., if the same
    %% file must be accessed with different paths on different machines.
    
    %% **** FILTERS ****
    
    %% Specify filters here. Specify as many filters as you want, each with a `filter:'
    %% directive. See also `bibolamazi --list-filters' and `bibolamazi --help <filter>'.
    
    filter: filter_name  <filter options>
    
    %% Example:
    filter: arxiv -sMode=strip -sUnpublishedMode=eprint
    
    %% Finally, if your file is in a VCS, sort all entries by citation key so that you don't
    %% get huge file differences for each commit each time bibolamazi is run:
    filter: orderentries
    
    

Available Filters
-----------------

You can get a full list of available filters if you open the bibolamazi help &
reference browser window (from the main application startup window). You can
click on the various filters displayed to view their documentation on how to use
them.


Filter Packages
---------------

Filters are organized into *filter packages*. All built-in filters are in the
package named `bibolamazi.filters`. If you want to write your own filters, or
use someone else's own filters, then you can install further filter packages.

A *filter package* is a Python package, i.e. a directory containing a
``__init__.py`` file, which contains python modules that implement the
bibolamazi filter API. (The ``__init__.py`` file is usually empty.)

If you develop your own filters, it is recommended to group them in a filter
package, and not for example fiddle with the built-in filter package. Put your
filters in a directory called, say, `myfilters`, and place an additional empty
file in it called `__init__.py`. This will create a python package named
`myfilters` with your filters as submodules.

You can include filter packages from within a bibolamazi file by using the
syntax::

  package: path/to/filter/pkgname

The path should point to a directory which is a valid python package, i.e.,
which contains a ``__init__.py`` file.

You may also register filter packages at specific locations in a way which
applies to all bibolamazi files.  Open the settings dialog, and click "Add
filter package ..."; choose the directory corresponding to your filter package
(e.g. `myfilters`). Now you can refer in your bibolamazi file to the filters
within your filter package with the syntax ``myfilters:filtername`` or simply
``filtername`` (as long as the filter name does not clash with another filter of
the same name in a different filter package).
