Installation
============

Installing PhiloLogic consists of two steps:

1. Install the C and Python libraries system-wide
2. Set up a directory in your web server to serve databases from

Downloading
-----------

You can find a copy of the latest version of PhiloLogic4 from <a href="https://github.com/ARTFL-Project/PhiloLogic4/releases/tag/v4.0-rc.1">here</a>.

For the rest of this document, we will assume the PhiloLogic source code is installed in 
your home directory at ~/PhiloLogic4/

Prerequisites
------------
* Python
* GCC
* Make
* `gdbm`_
* `lxml`_

Installing the C library
------------------------------

Installing PhiloLogic's libraries requires administrator privileges.
This C library depends on `gdbm`_, which *must* be installed first, to compile correctly.
Installation is standard for a Makefile-style distribution.

    cd ~/PhiloLogic4/libphilo
    make
    sudo make install

In addition to the library, the Makefile also generates two binary executables,
``corpus_search`` and ``pack4``, which are then copied into the 
binary execution directory, usually ``/bin``.

Installing the `Python` ``philologic`` module system-wide
------------------------------------------------------

Once ``libphilo`` is installed, we need to install its `Python` bindings
and library: ``philologic``. Once again, this step requires administrator
privileges. You probably want to install its prerequiste, ``lxml`` , first.

You can install the libraries either with Python's distutils:

    cd ~/PhiloLogic4/python
    sudo python setup.py install

or via the pip command::

    cd ~/PhiloLogic4/python
    sudo pip install .
