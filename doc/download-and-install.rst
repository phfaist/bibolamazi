
Downloading and Installing Bibolamazi
-------------------------------------

Bibolamazi comes in two flavors:

- an Application that runs on Mac OS X, Linux and Windows (this is what most users
  probably want)

- a command-line tool (for more advanced and automated usage)

There are precompiled ready-for-use binaries for the Application (see below,
:ref:`bibolamazi_application`). Alternatively, both flavors may be installed using
``pip``/``setuptools`` or from source (see :ref:`bibolamazi_installing_cmdl`).

.. _bibolamazi_application:

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
:ref:`using-bibolamazi-app`.


.. _bibolamazi_installing_cmdl:

Installing the Command-Line Interface
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bibolamazi runs with Python 3 (this is there by default on most linux and Mac systems).

Additionally, the graphical user interface requires PyQt4_. If you're on a linux
distribution, it's most probably in your distribution packages. Note you only need PyQt4
to run the graphical user interface: the command-line version will happily run without.

**The easy way: via PIP**

The recommended way to install Bibolamazi command line and gui interfaces is via ``pip``::

  pip install bibolamazi        # for the command-line interface
  pip install bibolamazigui     # if you want the GUI interface

After that, you'll find the ``bibolamazi`` (respectively ``bibolamazi_gui``) executables
in your PATH::

  > bibolamazi --help           # command-line interface
  (...)
  > bibolamazi_gui              # to launch the GUI
  (...)
  

**The less easy way: From Source**

You may, alternatively, download and compile the packages from source.

- First, clone this repository on your computer (don't download the prepackaged
  ZIP/Tarball proposed by github, because there will be missing submodules)::

    > cd somewhere/where/Ill-keep-bibolamazi/
    ...> git clone --recursive https://github.com/phfaist/bibolamazi

  Note the ``--recursive`` switch which will also retrieve all required submodules.

- Then, run the setup script to install the package and script (see `Installing Python
  Modules <https://docs.python.org/2/install/>`_)::

    > python setup.py install

  After that, you should find the ``bibolamazi`` executable in your PATH automatically::

    > bibolamazi --help

- If you want to install the GUI Application, you need to do that seperately. Go into the
  ``gui/`` directory of the source code, and run the python setup script there::

    > cd gui/
    gui> python setup.py install

  After that, you should find the ``bibolamazi_gui`` executable in your PATH
  automatically::

    > bibolamazi_gui


.. _PyQt4: http://www.riverbankcomputing.com/software/pyqt/download
.. _precompiled binary release: https://github.com/phfaist/bibolamazi/releases
