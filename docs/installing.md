Installation
============

Installing PhiloLogic consists of four steps:

1) Install the C and Python libraries system-wide
2) Set up a directory in your web server to serve databases from
3) Configure a loader script 
4) Load your texts into a new database instance

Downloading
-----------

Getting a copy of PhiloLogic4 can be achieved two different ways.
One is by cloning GitHub's repository via `git`_::

    cd $HOME
    git clone https://github.com/ARTFL-Project/PhiloLogic4

Another would be to directly download an archive from GitHub's ``master``
branch::

    cd $HOME
    wget --output-document=PhiloLogic4.tar.gz https://github.com/ARTFL-Project/PhiloLogic4/archive/master.tar.gz
    tar -xzf PhiloLogic4.tar.gz
    mv PhiloLogic4-master PhiloLogic4

If you are going to be the only PhiloLogic user on your machine, you probably want to set up 
a repository in your home directory.  If your setting it up for shared use, you should make sure
the repository is accessible by whoever is going to load databases on your system.  However,
shared use is not advisable if you will be commiting code to github.

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
``search4`` and ``pack4``, which are then copied into the 
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
