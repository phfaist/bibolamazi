![bibolamazi](https://github.com/phfaist/bibolamazi/raw/master/bibolamazi.png)

Collect bibliographic entries from BibTeX files and apply rules or filters to them


Installing and Getting Started
------------------------------

NOTE: bibolamazi requires Python 2.7 being installed.

* To install bibolamazi, simply clone this repository on your computer, or download it as
  a ZIP file and uncompress it somewhere. Then, link the executable to somewhere in your
  path:

           > cd /home/username/bin/
           bin> ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi bibolamazi

  or, for a system-wide install,

           > cd /usr/bin/
           > sudo ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi bibolamazi


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


Example Bibolamazi File
-----------------------

Here is a minimal example of a bibolamazi bibtex file.

    
    data here will not be overwritten. Place here any additional entries, comments or
    whatever you want to be left as is.
    
    %%%-BIB-OLA-MAZI-BEGIN-%%%
    % %% BIBOLAMAZI configuration section.
    % %% Additional two leading percent signs indicate comments in the configuration.
    % 
    % %% **** SOURCES ****
    % 
    % %% Specify your bib sources here. These files will not be touched by bibolamazi. If several paths
    % %% are given in one line, the first path that exists and is readable will be taken. HTTP/FTP URLs
    % %% can also be specified, and the file being pointed to will be downloaded and used as source.
    % %% Nonexisting sources will be ignored.
    %
    % src: "/Users/philippe/path/to/MyLibrary.bib" /home/pfaist/path/to/MyLibrary.bib
    % src: anothersource.bib
    % %% add additional sources here
    %
    % %% **** FILTERS ****
    %
    % %% Specify which filters to apply here. Filters are applied in the order they are given. Options
    % %% are provided in a command-line type syntax. For help about options to a filter, run
    % %% "bibolamazi --help <thefilter>", e.g. "bibolamazi --help arxiv". For a list of available filters
    % %% with their description, run "bibolamazi --list-filters".
    % 
    % filter: arxiv -sMode=strip -sUnpublishedMode=unpublished-note
    % %% or, for example: filter: arxiv --mode=eprint
    % filter: nameinitials
    % filter: duplicates dupfile.tex
    % filter: url -dStrip=False -dStripAllIfDoiOrArxiv=False
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
    
      arxiv         ArXiv clean-up filter: normalizes the way each biblographic
                    entry refers to arXiv IDs.
      duplicates    Filter that detects duplicate entries and produces rules to make
                    one entry an alias of the other.
      url           Remove or add URLs from entries according to given rules, e.g.
                    whether DOI or ArXiv ID are present
      nameinitials  Name Initials filter: Turn full first names into only initials
                    for all entries.
      fixes         Fixes filter: perform some various known fixes for bibtex
                    entries
      orderentries  Order bibliographic entries in bibtex file
    
    --------------------------
    
    Use  bibolamazi --help <filter>  for more information about each filter and
    its options.
    


Writing new filters
-------------------

Writing filters is straightforward. Look inside the filters/ directory at the existing
filters, e.g. `arxiv.py`, `duplicates.py` or `url.py`. They should be simple to understand.

A filter can either act on individual entries (e.g. the `arxiv.py` filter), or on the
whole database (e.g. `duplicates.py`).

Feel free to contribute filters, it will only make bibolamazi more useful!


Contact
-------

Please contact me for any bug reports, or if you want to contribute.

    @: (philippe) dot (faist) [at] (bluewin) dot (ch)


