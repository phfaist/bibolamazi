.. _import-filter-package:

Importing a filter package
==========================

Filter packages are imported by providing a filter specification at one of
several places in the bibolamazi app or command-line tool.


How to import a package
-----------------------

You have different ways to import a filter package to make the corresponding
filters available for use in your bibolamazi file:

  * Use a `package:` directive in your bibolamazi file.  Along with your sources
    and filters, specify something like::

      package: <filter-package-specification>

    To import the corresponding filter package.  See below for possible values
    of *<filter-package-specification>*.

  * (In the bibolamazi application only:) Open the settings dialog (from the
    main window).  Then select the local filter packages tab, and click on the
    button "Add filter package" to specify your local filter package.  You
    should specify the directory that defines the python package, i.e., the
    directory that contains the ``__init__.py`` file.

  * You may globally enable and import a filter package by setting the
    environment variable `BIBOLAMAZI_FILTER_PATH`.  This variable may be set to
    a list of filter packages separated by ``:`` on Unix/Mac systems and by
    ``;`` on Windows systems (as for the ``PATH`` environment variable).

  * (In the `bibolamazi` command-line tool only:) Use the option
    ``--filter-package=<filter-package-specification>``


After importing a filter package, you can then use all the filters defined in
that package in your bibolamazi file.  You can also refer to a filter in a
specific package, in case two filters from different packages have the same
name, with the syntax ``mypackage:filtername``.  For instance::

  filter: mypackage:filtername -dOption1 -sOption2=default ...


Filter Package Specification
----------------------------

A filter specification, indicated by *<filter-package-specification>* above, is
a string of one of the following forms:

  * ``/path/to/some/package`` — if a path is given, this must be a folder that
    defines a Python package (ie., which contains an ``__init__.py`` file).
    This package is the filter package.

  * ``packagename=/some/path/`` or ``packagename=`` — using this syntax, you
    specify a python package name and the path that needs to be added to the
    `PYTHONPATH` in order to load that package.  For instance, if you have a
    Python package located at ``/home/me/python/packages/pkga`` (which contains
    an ``__init__.py`` file), you would specify
    ``pkga=/home/me/python/packages``.

  * ``github:<user or org>/<repo>[/<branch>]`` — specify a filter package as a
    remote github repository.  The branch name is optional, and you can use a
    tag name or commit ID instead of a branch name.  Examples::

      package: github:phfaist/mybibolamazifilters

      package: github:phfaist/mybibolamazifilters/mybranch

      package: github:phfaist/mybibolamazifilters/4c84fd92ec9189ebf28ebd30916d3c9c9e53a8fb

    When a github repository is specified, the repository must either be the
    contents of the filter package (it contains a ``__init__.py`` file directly
    in the root directory of the repository), or it must contain a folder of the
    same name as the repo (possibly with hyphens converted to underscores) which
    is assumed to be the python filter package.

.. versionadded:: 4.2
                  Remote github repositories can be specified and automatically
                  accessed since Bibolamazi 4.2


Security Considerations for Remote Packages
-------------------------------------------

Downloading remote filter packages presents a security risk, because filters are
python scripts that can execute arbitrary code.  For this reason, a warning is
displayed to the user the first time you access a remote repository. You should
acknowledge this risk and remember to be careful.

You're asked once only, and the setting is then stored in the configuration
file.  You can modify the configuration file directly if you would like to
change this setting.  The configuration file resides in a system-dependent
location which is typically `~/.config/bibolamazi/` on Unix-like systems,
`C:\\Users\\<username>\\AppData\\Local\\bibolamazi\\` on Windows, and
`~/Library/Application Support/bibolamazi/` on Macs; we use the `appdirs Python
package <https://pypi.org/project/appdirs/>`_ to determine this.


.. _filter-package-github-auth:

Github Authentication for Private Repositories
----------------------------------------------

It's a good idea to set up github authentication if you use github remote
packages, as you have two main advantages:

  * you can access your private repositories;

  * the github API server has higher rate limits and you will be much less
    likely to reach their query limits.

Bibolamazi uses personal access tokens to authenticate to github.  You simply
create a dedicated personal access token for bibolamazi by visiting
`https://github.com/settings/tokens <https://github.com/settings/tokens>`_ and
specify the resulting token to bibolamazi.  The token can be revoked at any
later time and bibolamazi never sees your password.

In the bibolamazi application, go to `Settings` → `Remote filter packages tab`,
and turn on `Use authentication`.  This will prompt you with specific settings
to carry out to generate your personal access token and provide it to
bibolamazi.

In the command-line application, run ``bibolamazi --github-auth``.  This will
enter interactive setup mode where instructions are provided on how to generate
the access token and provide it to bibolamazi.  To un-set any previously set
authentication data, use ``bibolamazi --github-auth=-``.

.. versionadded:: 4.2
                  Remote github repositories can be specified and automatically
                  accessed since Bibolamazi 4.2

