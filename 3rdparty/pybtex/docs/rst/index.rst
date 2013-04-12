=======
Pybtex!
=======

.. download-links::


Pybtex is a drop-in replacement for BibTeX written in Python.
You can start using it right now by simply typing ``pybtex`` where you would have typed ``bibtex``.

Please note that the correct spelling is just *Pybtex*, without any camel-casing,
which we considered too annoying to type.

We also suggest reading `the Friendly Manual <manual.txt>`_, although it is
still incomplete.

Oh! Is it really BibTeX-compatible?
===================================

Yes, it really is, most of the time.

BibTeX styles work fine with Pybtex,
although there are still some minor issues.
Nevertheless, we are going to achieve 100% compatibility before releasing
version 1.0.

If something does not work for you, just `let us know
<http://sourceforge.net/tracker/?func=add&group_id=151578&atid=781406>`_.


But why should I use it instead of BibTeX?
==========================================

You probably should not if you ask. But still, Pybtex has Unicode inside.
It supports BibTeXML and YAML. It can write HTML and plain text.
It is extensible and fun to hack. It comes with a free database conversion utility.
And designing new bibliography styles is no more a pain with Pybtex'
brand new `pythonic style API <style_api.txt>`_.

You can see the `feature overview <features.txt>`_ for more details.

Hmm nice. Wrap it up, I'll take it! Where is the download link?
===============================================================
.. _download:

The tarballs thay are available from the `PyPI page
<http://pypi.python.org/pypi/pybtex>`_.  That said, the most stable and
feature complete and well documented version of Pybtex is known to be the
`Bazaar trunk <https://code.launchpad.net/~ero-sennin/pybtex/trunk>`_.

To get the very latest Pybtex from the trunk:

.. sourcecode:: bash

    bzr branch lp:pybtex
    cd pybtex
    python setup.py develop

And do not forget to run the tests (need `nose
<http://somethingaboutorange.com/mrl/projects/nose/>`_):

.. sourcecode:: bash

    python setup.py nosetests

Pybtex can be also installed with Easy Install:

.. sourcecode:: bash

    easy_install pybtex

But you won't get any documentation this way.

If something goes wrong, please `file a bug report
<http://sourceforge.net/tracker/?func=add&group_id=151578&atid=781406>`_.

Have fun!
