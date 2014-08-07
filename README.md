![bibolamazi](https://github.com/phfaist/bibolamazi/raw/master/bibolamazi.png)

Collect bibliographic entries from BibTeX files and apply rules or filters to them

Command-Line vs Graphical User Interface
----------------------------------------

There are two flavors of bibolamazi: the command-line version, and the nice windowed
graphical interface.

Most users might prefer the straightforward-to-install, ready-and-easy-to-use
graphical interface, in which case you should download the latest stable binary
release from:

**Download Release:** https://github.com/phfaist/bibolamazi/releases

These binaries don't need any installation, you can just download them, place them
wherever you want, and run them.

The rest of this document is concerned mostly about downloading, installing and using
bibolamazi from source. This option is only necessary if you want to use the
command-line interface.


Installing and Getting Started
------------------------------

Note: bibolamazi requires Python 2.7 being installed (which is there by default on most
linux and Mac systems).

Additionally, the graphical user interface requires
[PyQt4](http://www.riverbankcomputing.com/software/pyqt/download). If you're on a linux
distribution, it's most probably in your distribution packages. Note you only need PyQt4
to run the graphical user interface: the command-line version will happily run without.

* To install bibolamazi, simply clone this repository on your computer, or download it as
  a ZIP file and uncompress it somewhere (cloning is preferred, as it makes updating much
  easier with `git pull`).

           > cd somewhere/where/Ill-keep-bibolamazi/
           ...> git clone --recursive https://github.com/phfaist/bibolamazi

  Then, link the executable(s) to somewhere in your path:

           > cd ~/bin/
           bin> ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi .
           bin> ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi_gui .

  or, for a system-wide install,

           > cd /usr/local/bin/
           > sudo ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi .
           > sudo ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi_gui .


* To compile a bibolamazi bibtex file, you should run `bibolamazi` in general as

           > bibolamazi bibolamazibibtexfile.bib

* To quickly get started with a new bibolamazi file, the following command will create the
  given file and produce a usable template which you can edit:

           > bibolamazi --new newfile.bib

* For an example to study, look at the file `test/output.bib` in the source code. To compile
  it, run

           > bibolamazi test/output.bib
           
* For a help message with a list of possible options, run

           > bibolamazi --help

  To get a list of all available filters along with their description, run

           > bibolamazi --list-filters

  To get information about a specific filter, simply use the command

           > bibolamazi --help <filter>


Using Bibolamazi
----------------

### Bibolamazi Operating Mode

Bibolamazi works by reading a bibtex file (say `main.bib`) with a special bibolamazi
configuration section at the top. These describe on one hand *sources*, and on the
other hand *filters*. Bibolamazi first reads all the entries in the given sources
(say `source1.bib` and `source2.bib`), and then applies the given filters to them.
Then, the main bibtex file (in our example `main.bib`) is updated, such that:

* Any content that was already present in the main bibtex file *before* the
  configuration section is restored unchanged;

* The configuration section is restored as it was;

* All the filtered entries (obtained from, e.g., `source1.bib` and `source2.bib`) are
  then dumped in the rest of the file, overwriting the rest of `main.bib` (which
  logically contained output of a previous run of bibolamazi).


### The Bibolamazi Configuration Section

The main bibtex file should contain a block of the following form:

    %%%-BIB-OLA-MAZI-BEGIN-%%%
    %
    %   ... bibolamazi configuration section ...
    %
    %%%-BIB-OLA-MAZI-END-%%%

The configuration section is started by the string `%%%-BIB-OLA-MAZI-BEGIN-%%%` on its own line,
and is terminated by the string `%%%-BIB-OLA-MAZI-END-%%%`, also on its own line. The lines between
these two markers are the body of the configuration section, and are where you should specify
sources and filters. Leading percent signs on these inner lines are ignored. Comments can be specified
in the configuration body with two additional percent signs, e.g.

    % %% This is a comment


### Specifying sources

Sources are specified with the `src:` keyword. As an example:

    % src: mysource.bib

You should specify one or more files from which entries should be read. If more than one file is
given, only the FIRST file that exists is read. This is useful for example, if on different
computers your bibtex is elsewhere:

    % src: /home/philippe/bibtexfiles/mylibrary.bib /Users/philippe/bibtexfiles/mylibrary.bib

You may also specify HTTP or FTP URLs. If your filename or URL contains spaces, enclose the name
in double quotes: `"My Bibtex Library.bib"`.

To specify several sources that should be read independently, simply use multiple `src:` commands.

    % src: file1.bib [alternativefile1.bib ...]
    % src: file2.bib [alternativefile2.bib ...]
    % [...]

This would collect all the entries from the first existing file of each `src` command.

### Specifying filters

Once all the entries are collected from the various sources, you may now apply filters to them.

A filter is applied using the `filter` command.

    % filter: filtername [options and arguments]

Filters usually accept options and arguments in a shell-like fashion, but this may vary in
principle from filter to filter. For example, one may use the `arxiv` filter to strip away all
arXiv preprint information from all published entries, and normalize unpublished entries to
refer to the arxiv in a uniform fashion:

    % filter: arxiv --mode=strip --unpublished-mode=eprint

A full list of options can be obtained with

    > bibolamazi --help arxiv

and more generally, for any filter,

    > bibolamazi --help <filtername>

A list of available filters can be obtained by running

    > bibolamazi --list-filters

**Note:** Filters are organized into *filter packages* (see below). A filter is searched
in each filter package until a match is found. To force the lookup of a filter in a
specific package, you may prefix the package name to the filter, e.g.:

    % filter: myfilterpackage:myfiltername --option1=val1  ...


Example Bibolamazi File
-----------------------

Here is a minimal example of a bibolamazi bibtex file.

    
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

    

Available filters
-----------------

A complete list of available filters, along with a short description, is obtained by

    > bibolamazi --list-filters

Run that command to get an up-to-date list. At the time of writing, the list of
filters is:

    > bibolamazi --list-filters

    List of available filters:
    --------------------------
    
    Package `filters':
    
      arxiv         ArXiv clean-up filter: normalizes the way each biblographic
                    entry refers to arXiv IDs.
      citearxiv     Filter that fills BibTeX files with relevant entries to cite
                    with \cite{1211.1037}
      citekey       Set the citation key of entries in a standard format
      duplicates    Filter that detects duplicate entries and produces rules to make
                    one entry an alias of the other.
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


Filter Packages
---------------

Filters are organized into *filter packages*. All built-in filters are in the package
named `filters`. If you want to write your own filters, or use someone else's own filters,
then you can install further filter packages.

A *filter package* is a Python package, i.e. a directory containing a `__init__.py` file,
which contains python modules that implement the bibolamazi filter API.

The command-line bibolamazi by default only knows the built-in fitler package `filters`. 
You may however specify additional packages either by command-line options or with an
environment variable.

You can specify additional filter packages with the command-line option
`--filter-package`.

    > bibolamazi myfile.bib --filter-package 'package1=/path/to/filter/pack'

The argument to `--filter-package` is of the form
'packagename=/path/to/the/filter/package'. Note that the path is which path must be added
to python's `sys.path` in order to import the `filterpackagename` package itself, i.e. the
last item of the path must not be the package directory.

This option may be repeated several times to import different filter packages. The order
is relevant; the packages specified last will be searched for first.

You may also set the environment variable `BIBOLAMAZI_FILTER_PATH`. The format is
`filterpack1=/path/to/somewhere:filterpack2=/path/to/otherplace:...`, i.e. a list of
filter package specifications separated by ':' (Linux/Mac) or ';' (Windows). Each filter
package specification has the same format as the command-line option argument. In the
environment variable, the first given filter packages are searched first.

Note in the graphical user interface, you can specify filter packages in the settings
dialog.


Developing Custom filters
-------------------------

Writing filters is straightforward. Look inside the filters/ directory at the existing
filters, e.g. `arxiv.py`, `duplicates.py` or `url.py`. They should be simple to understand.

A filter can either act on individual entries (e.g. the `arxiv.py` filter), or on the
whole database (e.g. `duplicates.py`).

For your organization, it is recommended to develop your filter(s) in a custom filter
package which you keep a repository e.g. on github.com, so that the filter package can be
easily installed on the different locations you would like to run bibolamazi from.

Feel free to contribute filters, it will only make bibolamazi more useful!


Credits and Copyright
---------------------

Copyright (c) 2014 Philippe Faist

Bibolamazi is developed and maintained by Philippe Faist. It is distributed under the
[GNU General Public License (GPL)](http://www.gnu.org/copyleft/gpl.html), Version 3 or higher.

### Third-Party Code

This project also contains the following 3rd party code.

[**PybTeX**](http://pybtex.sourceforge.net/) provides a python library for parsing and writing
BibTeX files.

    Copyright (c) 2006, 2007, 2008, 2009, 2010, 2011 Andrey Golovizin

Full copyright notice is availble in this repo in the file `3rdparty/pybtex/COPYING`.

[**Arxiv2Bib**](http://nathangrigg.github.io/arxiv2bib/) is a tool for querying the
[arxiv.org](http://arxiv.org/) API for preprint details and for parsing its results.

    Copyright (c) 2012, Nathan Grigg

Full copyright notice is available in this repo in the first lines of the file
`3rdparty/arxiv2bib/arxiv2bib.py`.



Contact
-------

Please contact me for any bug reports, or if you want to contribute.

    @: (philippe) dot (faist) [at] (bluewin) dot (ch)


