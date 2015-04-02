PhiloLogic4
===========

PhiloLogic is an XML database/search engine/web app that is designed 
for the particular difficulties of TEI XML.  For a more theoretical 
description, you can refer to `our research publications <http://http://jtei.revues.org/817>`_ or `our blog <http://artfl.blogspot.com>`_.


Documentation
=============
* [**Installation**](docs/installation.md)

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


Setting up PhiloLogic Web Application
---------------------------------------------

Each new PhiloLogic database you load, containing one or more TEI-XML files, will be served
by a its own dedicated copy of PhiloLogic web application.
By convention, this database and web app reside together in a directory
accessible via an HTTP server configured to run Python CGI scripts.

In Mac OS X systems, you will probably want to create a directory at
``/Library/WebServer/Documents/philologic`` to serve up PhiloLogic databases
with the URL prefix: ``http://<your_server's_name>/philologic/``; for Linux systems, 
the proper directory may vary, but ``/var/www/philologic/`` or ``/var/www/html/philologic/``

Configuring your web server is outside of the scope of this document; but the web install
does come with a preconfigured .htaccess file that allows you to run the Web App.
Therefore, you need to make sure your server is configured to allow htaccess files.
if in doubt, ask a friendly sysadmin..  

Customize ``load_script.py``
^^^^^^^^^^^^^^^^^^^^^^^

Tthe ``load_script.py`` is the most important script for generating database and
web application from web application *template* and `TEI-XML` corpus files,
but before using it, you **must customize** it for your system, and possibly
for your data. 

Given a set of this `TEI-XML` files, located for e.g. at ``~/mycorpus/xml`` directory, 
we could put a copy of ``~/PhiloLogic4/scripts/load_script.py`` in ``~/mycorpus``::

    cp ~/PhiloLogic4/scripts/load_script.py ~/mycorpus/

It could be possible to also tweak the web application template to better
fullfill your data specification or branding needs, but for this
example, we assume you'll simply started with bare ``~/PhiloLogic4/www``'s one.

The main *required* variables of ``load_script.py`` to be set are located
around lines 25-44, and are ``database_root``, ``url_root``
and ``template_dir``. Following the previous section, we must set
``database_root`` variable to ``'/var/www/html/mydatabase/'``
``url_root`` set to``'http://localhost/mydatabase/'``. 
Finally, since we're using the basic web application template in `
`~/PhiloLogic4/www``, we should point ``template_dir`` there.

So the three lines to edit are as follows::

    database_root = '/var/www/html/mydatabase/'
    url_root = 'http://localhost/mydatabase/'
    template_dir = '~/PhiloLogic4/www/'


Loading
^^^^^^^

Once all files are in place and ``load_script.py`` script is customized, it's time
for PhiloLogic to actually index your text files, by running the script
on TEI-XML files::

    python ~/mycorpus/load_script.py [database name] [path to TEI-XML files]

This script takes the following required arguments:

1.  the name of the database to create, which will be the subdirectory
    into ``/var/www/html`` directory, i.e. ``mydatabase``,
2.  the paths to each of `TEI-XML` files from which fulfill database content,
    i.e. ``~/mycorpus/xml/*.xml``.

The full list of arguments ``load_script.py`` accepts is set in its body
around lines 15-25, and will be displayed  when running ``loader.py`` without
a database name::

    python ~/mycorpus/load_script.py

The script also accepts optional arguments, among others most common are
``--workers`` and ``--debug``:

``-w WORKERS`` / ``--workers=WORKERS``:
    This option set the number of workers the ``loader.py`` will use.
    It is mostly usefull for multi-cores hardware.

``-d`` / ``--debug``
    Set both ``load_script.py`` and web application in debug mode.

.. note::

    See ``LOADING.rst`` document for details about loading.

So our command line for loading would be::

    cd /var/www/html
    python ~/mycorpus/load_script.py mydatabase ~/mycorpus/xml/*.xml

The above command should have populated the ``/var/www/html/mydatabase``
directory with both web application and data files.

Layout of a PhiloLogic Web Application Instance
-----------------------------------------------

This database directory now contains *both* `PhiloLogic` web application, at the root,
with the indexes and other data structures, in a ``data`` subdirectory.
At the end of generation, this directory will look like this tree::

    --- /var/www/html
        \--- mydatabase
            \--- app
                \--- assets
                \--- components
                \--- shared
                \--- index.html
                \--- PhiloLogicMain.js
            \--- data
            \--- functions
            \--- reports
            \--- scripts
            \--- .htaccess
            \--- dispatcher.py

----

.. Links:

.. _git: http://git-scm.com/
.. _gdbm: http://www.gnu.org.ua/software/gdbm/
.. _pip: http://www.pip-installer.org/
.. _Apache httpd: http://httpd.apache.org/
.. _lxml: http://lxml.de/
