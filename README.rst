.. image:: https://beeware.org/project/projects/tools/duvet/duvet.png
    :width: 72px
    :target: https://beeware.org/duvet

Duvet
=====

.. image:: https://img.shields.io/pypi/pyversions/duvet.svg
    :target: https://pypi.python.org/pypi/duvet

.. image:: https://img.shields.io/pypi/v/duvet.svg
    :target: https://pypi.python.org/pypi/duvet

.. image:: https://img.shields.io/pypi/status/duvet.svg
    :target: https://pypi.python.org/pypi/duvet

.. image:: https://img.shields.io/pypi/l/duvet.svg
    :target: https://github.com/pybee/duvet/blob/main/LICENSE

.. image:: https://github.com/beeware/duvet/workflows/CI/badge.svg?branch=main
   :target: https://github.com/beeware/duvet/actions
   :alt: Build Status

.. image:: https://img.shields.io/discord/836455665257021440?label=Discord%20Chat&logo=discord&style=plastic
   :target: https://beeware.org/bee/chat/
   :alt: Discord server

Duvet is a GUI tool for visualizing code coverage results produced by
`coverage.py`_.

Why the name Duvet? Because a duvet doesn't just provide coverage - it keeps you
warm and cozy.

.. _coverage.py: http://nedbatchelder.com/code/coverage/

Quickstart
----------

In your virtualenv, install Duvet, generate some coverage data, and then run ``duvet``::

    $ pip install duvet
    $ coverage run myscript.py arg1 arg2
    $ duvet

This will pop up a GUI window, displaying all source code in your current working
directory. Any source file mentioned in the coverage data will be highlighted in the
source file tree, with a color indicating how good the coverage is (red for bad
coverage, green for perfect coverage). If you select a filename in the tree, the
contents of that file will be displayed, with the missed lines highlighted.

Problems under Ubuntu
~~~~~~~~~~~~~~~~~~~~~

Ubuntu's packaging of Python omits the ``idlelib`` library from it's
base packge. If you're using Python 2.7 on Ubuntu 13.04, you can install
``idlelib`` by running::

    $ sudo apt-get install idle-python2.7

For other versions of Python and Ubuntu, you'll need to adjust this as
appropriate.

Problems under Windows
~~~~~~~~~~~~~~~~~~~~~~

If you're running Duvet in a virtualenv, you'll need to set an
environment variable so that Duvet can find the TCL graphics library::

    $ set TCL_LIBRARY=c:\Python27\tcl\tcl8.5

You'll need to adjust the exact path to reflect your local Python install.
You may find it helpful to put this line in the ``activate.bat`` script
for your virtual environment so that it is automatically set whenever the
virtualenv is activated.

Documentation
-------------

Documentation for Duvet can be found on `Read The Docs`_.

Community
---------

Duvet is part of the `BeeWare suite`_. You can talk to the community through:

* `@pybeeware on Twitter`_

* `Discord <https://beeware.org/bee/chat/>`__

We foster a welcoming and respectful community as described in our
`BeeWare Community Code of Conduct`_.

Contributing
------------

If you experience problems with Duvet, `log them on GitHub`_. If you
want to contribute code, please `fork the code`_ and `submit a pull request`_.

.. _BeeWare suite: https://beeware.org
.. _Read The Docs: https://duvet.readthedocs.io
.. _@pybeeware on Twitter: https://twitter.com/pybeeware
.. _BeeWare Community Code of Conduct: https://beeware.org/community/behavior/
.. _log them on Github: https://github.com/beeware/duvet/issues
.. _fork the code: https://github.com/beeware/duvet
.. _submit a pull request: https://github.com/beeware/duvet/pulls
