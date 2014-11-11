
Introduction to Bibolamazi
==========================

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

Additionally, the graphical user interface requires PyQt4_. If you're on a linux
distribution, it's most probably in your distribution packages. Note you only need PyQt4
to run the graphical user interface: the command-line version will happily run without.

Note that these requirements are NOT necessary if you use a `precompiled binary
release`_. The requirements (and following instructions) apply to downloading and running
bibolamazi from source, which for example is required if you want to use the command-line
version.

* First, clone this repository on your computer, or download it as
  a ZIP file and uncompress it somewhere (cloning is preferred, as it makes updating much
  easier with ``git pull``)::

    > cd somewhere/where/Ill-keep-bibolamazi/
    ...> git clone --recursive https://github.com/phfaist/bibolamazi

  Then, link the executable(s) to somewhere in your path::

    > cd ~/bin/
    bin> ln -s /path/to/unpacked/bibolamazi/bibolamazi .
    bin> ln -s /path/to/unpacked/bibolamazi/bibolamazi_gui .

  or, for a system-wide install::

     > cd /usr/local/bin/
     > sudo ln -s /path/to/unpacked/bibolamazi/bibolamazi .
     > sudo ln -s /path/to/unpacked/bibolamazi/bibolamazi_gui .


* To compile a bibolamazi bibtex file, you should run ``bibolamazi`` in general as::

     > bibolamazi bibolamazibibtexfile.bibolamazi.bib

* To quickly get started with a new bibolamazi file, the following command will create the
  given file and produce a usable template which you can edit::

     > bibolamazi --new newfile.bibolamazi.bib

* For an example to study, look at the file ``test/test0.bibolamazi.bib`` in the source code.
  To compile it, run::

     > bibolamazi test/test0.bibolamazi.bib
           
* For a help message with a list of possible options, run::

     > bibolamazi --help

  To get a list of all available filters along with their description, run::

     > bibolamazi --list-filters

  To get information about a specific filter, simply use the command::

     > bibolamazi --help <filter>


.. _PyQt4: http://www.riverbankcomputing.com/software/pyqt/download
.. _precompiled binary release: https://github.com/phfaist/bibolamazi/releases
