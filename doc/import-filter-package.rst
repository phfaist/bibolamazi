.. _import-filter-package:

Importing a filter package
==========================

Filter packages are imported by providing a filter specification at one of
several places in the bibolamazi app or command-line tool.

Where to import the package
---------------------------

You have different ways to import a filter package to make the corresponding
filters available for use in your bibolamazi file:

  * Use a `package:` directive in your bibolamazi file.  Along with your sources
    and filters, specify something like::

      package: <filter-package-specification>

    To import the corresponding filter package.  See below for possible values
    of *<filter-package-specification>*.

  * (In the bibolamazi application only:) Open the settings dialog (from the
    main window).  Then click on the button "Add filter package" to specify your
    local filter package.  You should specify the directory that defines the
    python package, i.e., the directory that contains the ``__init__.py`` file.

  * You may globally enable and import a filter package by setting the
    environment variable `BIBOLAMAZI_FILTER_PATH`.  This variable may be set to
    a list of filter packages, 

  Open the settings dialog, and click "Add
filter package ..."; choose the directory corresponding to your filter package
(e.g. `myfilters`). Now you can refer in your bibolamazi file to the filters
within your filter package with the syntax ``myfilters:filtername`` or simply
``filtername`` (as long as the filter name does not clash with another filter of
the same name in a different filter package).





See 

TODO: DOC .................. SINCE 4.2: Can specify URLs of the form
github:user/repo & bibolamazi automatically downloads the filter
package. .............. To set up authentication in app: see settings. In
command-line, use --github-auth, see --help. .............
