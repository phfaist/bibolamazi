
Using Bibolamazi in Command-Line
================================

First Steps With Bibolamazi Command-Line
----------------------------------------

Once you've installed bibolamazi as described in :ref:`bibolamazi_installing_cmdl`, you may
start using it! Here are a couple of commands to get you started playing around. But it's
important to understand how Bibolamazi works: for that, read the following sections
of this manual carefully.

- To compile a bibolamazi bibtex file, you should run ``bibolamazi`` in general as::

     > bibolamazi myfile.bibolamazi.bib

- To quickly get started with a new bibolamazi file, the following command will create the
  given file and produce a usable template which you can edit::

     > bibolamazi --new newfile.bibolamazi.bib

- For an example to study, look at the various test files provided in the source
  code.  To compile them, run::

     > bibolamazi test0.bibolamazi.bib
     
- For a help message with a list of possible options, run::

     > bibolamazi --help

  To get a list of all available filters along with their description, run::

     > bibolamazi --list-filters

  To get information about a specific filter, simply use the command::

     > bibolamazi --help <filter>



Bibolamazi Operating Mode
-------------------------

Bibolamazi works by reading a bibtex file (say ``main.bibolamazi.bib``) with a special
bibolamazi configuration section at the top. These describe on one hand *sources*, and on
the other hand *filters*. Bibolamazi first reads all the entries in the given sources (say
``source1.bib`` and ``source2.bib``), and then applies the given filters to them.  Then, the
main bibtex file (in our example ``main.bibolamazi.bib``) is updated, such that:

* Any content that was already present in the main bibtex file *before* the
  configuration section is restored unchanged;

* The configuration section is restored as it was;

* All the filtered entries (obtained from, e.g., ``source1.bib`` and ``source2.bib``) are
  then dumped in the rest of the file, overwriting the rest of ``main.bibolamazi.bib`` (which
  logically contained output of a previous run of bibolamazi).

The bibolamazi file ``main.bibolamazi.bib`` is then a valid BibTeX file to include into your
LaTeX document, so you would include the bibliography in your document with a LaTeX command
similar to::

    \bibliography{main.bibolamazi}



The Bibolamazi Configuration Section
------------------------------------

The main bibtex file should contain a block of the following form::

    %%%-BIB-OLA-MAZI-BEGIN-%%%
    %
    %   ... bibolamazi configuration section ...
    %
    %%%-BIB-OLA-MAZI-END-%%%

The configuration section is started by the string `%%%-BIB-OLA-MAZI-BEGIN-%%%` on its own line,
and is terminated by the string `%%%-BIB-OLA-MAZI-END-%%%`, also on its own line. The lines between
these two markers are the body of the configuration section, and are where you should specify
sources and filters. Leading percent signs on these inner lines are ignored. Comments can be specified
in the configuration body with two additional percent signs, e.g.::

    % %% This is a comment


Content of the Configuration Section
------------------------------------

The content of the configuration section is the same as described in
:ref:`bibolamazi-configuration-section`. Of course, you'll probably want to prefix all
lines by an additional '%' to make sure it gets interpreted as a bibtex comment (see
example below).


Example Full Bibolamazi File
----------------------------


Here is a minimal example of a bibolamazi bibtex file::

    
    .. Additionnal stuff here will not be managed by bibolamazi. It will also not be
    .. overwritten. You can e.g. temporarily add additional references here if you
    .. don't have bibolamazi installed.
    
    
    %%%-BIB-OLA-MAZI-BEGIN-%%%
    %
    % %% BIBOLAMAZI configuration section.
    % %% Additional two leading percent signs indicate comments in the configuration.
    %
    % %% **** SOURCES ****
    %
    % %% The _first_ accessible file in _each_ source list will be read and filtered.
    %
    % src:   <source file 1> [ <alternate source file 1> ... ]
    % src:   <source file 2> [ ... ]
    %
    % %% Add additional sources here. Alternative files are useful, e.g., if the same
    % %% file must be accessed with different paths on different machines.
    %
    % %% **** FILTERS ****
    %
    % %% Specify filters here. Specify as many filters as you want, each with a `filter:'
    % %% directive. See also `bibolamazi --list-filters' and `bibolamazi --help <filter>'.
    %
    % filter: filter_name  <filter options>
    %
    % %% Example:
    % filter: arxiv -sMode=strip -sUnpublishedMode=eprint
    %
    % %% Finally, if your file is in a VCS, sort all entries by citation key so that you don't
    % %% get huge file differences for each commit each time bibolamazi is run:
    % filter: orderentries
    %
    %%%-BIB-OLA-MAZI-END-%%%
    %
    %
    % ALL CHANGES BEYOND THIS POINT WILL BE LOST NEXT TIME BIBOLAMAZI IS RUN.
    %
    
    ... bibolamazi filtered entries ...



Querying Available Filters and Filter Documentation
---------------------------------------------------

A complete list of available filters, along with a short description, is obtained by::

  > bibolamazi --list-filters

Run that command to get an up-to-date list. At the time of writing, the list of
filters is::

  > bibolamazi --list-filters

  List of available filters:
  --------------------------
  
  Package `bibolamazi.filters':
  
    arxiv         ArXiv clean-up filter: normalizes the way each biblographic
                  entry refers to arXiv IDs.
    citearxiv     Filter that fills BibTeX files with relevant entries to cite
                  with \cite{1211.1037}
    citeinspirehep Filter that fills BibTeX files with relevant entries to cite
                  with e.g.  \cite{inspire:PhysRev.47.777--EPR+paper}
    citekey       Set the citation key of entries in a standard format
    duplicates    Produces LaTeX rules to make duplicate entries aliases of one
                  another.
    echo          Echo a custom message in the bibolamazi log
    fixes         Fixes filter: perform some various known fixes for bibtex
                  entries
    nameinitials  Name Initials filter: Turn full first names into only initials
                  for all entries.
    only_used     Filter that keeps only BibTeX entries which are referenced in
                  the LaTeX document
    orderentries  Order bibliographic entries in bibtex file
    url           Remove or add URLs from entries according to given rules, e.g.
                  whether DOI or ArXiv ID are present
  
  --------------------------
  
  Filter packages are listed in the order they are searched.
  
  Use  bibolamazi --help <filter>  for more information about a specific filter
  and its options.

.. note::
   The ``--list-filters`` option must be given after any ``--filterpackage`` options.


Specifying Filter Packages
--------------------------

The command-line bibolamazi by default only knows the built-in fitler package
``bibolamazi.filters``. You may however specify additional packages either by
command-line options or with an environment variable.

You can specify additional filter packages with the command-line option
``--filter-package``::

  > bibolamazi myfile.bibolamazi.bib --filter-package 'package1=/path/to/filter/pack'

or using the alternative syntax::

  > bibolamazi myfile.bibolamazi.bib --filter-package '/path/to/filter/pack/package1'

The argument to ``--filter-package`` is of the form
'packagename=/path/to/the/filter/package' or '/path/to/filter/package'. Note
that in the first syntax, the path is which path must be added to python's
``sys.path`` in order to import the ``filterpackagename`` package itself,
i.e. the last item of the path must not be the package directory; in the second
syntax, the path should point to the python package directory itself, i.e., the
directory which contains the ``__init__.py`` file.

This option may be repeated several times to import different filter
packages. The order is relevant; the packages specified last will be searched
for first.

You may also set the environment variable ``BIBOLAMAZI_FILTER_PATH``. The format
is a list of filter package specifications separated by ':' (Linux/Mac) or ';'
(Windows). Each filter package specification has the same format as the
command-line option argument (i.e., a key-value pair
``pkgname=/path/for/import``, or ``/path/to/filter/pkgname``).  In the
environment variable, the first given filter packages are searched first.
