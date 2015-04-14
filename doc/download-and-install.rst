
Downloading and Installing Bibolamazi
-------------------------------------

Bibolamazi comes in two flavors:

- an Application that runs on Mac OS X, Linux and Windows (this is what most users
  probably want)

- a command-line tool (for more advanced and automated usage)


The Bibolamazi Application
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're unsure which flavor to get, this is the one you're looking for. It's
straightfoward to download, there is no installation required, and the application is easy
to use.

Download the latest release from our releases page:

**Download Release:** https://github.com/phfaist/bibolamazi/releases

These binaries don't need any installation, you can just download them, place them
wherever you want, and run them.

You may now start using Bibolamazi normally. To read more on bibolamazi, skip to
:ref:`using-bibolamazi`.


Installing the Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bibolamazi runs with Python 2.7 (this is there by default on most linux and Mac systems).

Additionally, the graphical user interface requires PyQt4_. If you're on a linux
distribution, it's most probably in your distribution packages. Note you only need PyQt4
to run the graphical user interface: the command-line version will happily run without.

- First, clone this repository on your computer (don't download the prepackaged
  ZIP/Tarball proposed by github, because there will be missing submodules)::

    > cd somewhere/where/Ill-keep-bibolamazi/
    ...> git clone --recursive https://github.com/phfaist/bibolamazi

  Note the ``--recursive`` switch which will also retrieve all required submodules.

  Then, link the executable(s) to somewhere in your path::

    > cd ~/bin/
    bin> ln -s /path/to/unpacked/bibolamazi/bibolamazi .
    bin> ln -s /path/to/unpacked/bibolamazi/bibolamazi_gui .

  or, for a system-wide install::

     > cd /usr/local/bin/
     > sudo ln -s /path/to/unpacked/bibolamazi/bibolamazi .
     > sudo ln -s /path/to/unpacked/bibolamazi/bibolamazi_gui .


- To compile a bibolamazi bibtex file, you should run ``bibolamazi`` in general as::

     > bibolamazi bibolamazibibtexfile.bibolamazi.bib

- To quickly get started with a new bibolamazi file, the following command will create the
  given file and produce a usable template which you can edit::

     > bibolamazi --new newfile.bibolamazi.bib

- For an example to study, look at the file ``test/test0.bibolamazi.bib`` in the source code.
  To compile it, run::

     > bibolamazi test/test0.bibolamazi.bib
           
- For a help message with a list of possible options, run::

     > bibolamazi --help

  To get a list of all available filters along with their description, run::

     > bibolamazi --list-filters

  To get information about a specific filter, simply use the command::

     > bibolamazi --help <filter>


.. _PyQt4: http://www.riverbankcomputing.com/software/pyqt/download
.. _precompiled binary release: https://github.com/phfaist/bibolamazi/releases
