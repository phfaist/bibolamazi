bibolamazi
==========

![bibolamazi logo](https://github.com/phfaist/bibolamazi/raw/master/bibolamazi.png)

Collect bibliographic entries from BibTeX files and apply rules or filters to them


Installing and Getting Started
------------------------------

NOTE: bibolamazi requires Python 2.7 being installed.

* To install bibolamazi, simply clone this repository on your computer, or download it as
  a ZIP file and uncompress it somewhere.

* The main script is "bibolamazi.py". Run

           > bibolamazi.py --help

  for a help message.

* To get started with an example, run

           > bibolamazi.py test/output.bib

* To have bibolamazi accessible in your $PATH, simply create a symbolic link in a directory which
  is in your $PATH:

           > cd /home/username/bin/
           bin> ln -s /path/to/where/you/unpacked/bibolamazi/bibolamazi.py bibolamazi
 
  such that you can run
  
          > bibolamazi
 
  whereever you are.


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


