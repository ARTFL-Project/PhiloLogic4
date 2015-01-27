PhiloLogic4
===========

PhiloLogic is an XML database/search engine/web app that is desigined for the particular difficulties of TEI XML.  For a more theoretical description, you can refer to `our research publications <http://http://jtei.revues.org/817>`_ or `our blog <http://artfl.blogspot.com>`_.

Installation
============

Installing PhiloLogic consists of three steps:

1) Install the C and Python libraries system-wide
2) Set up a directory in your web server to deploy databases
3) Configure a loader script 


Downloading
-----------

Getting a copy of `PhiloLogic4` can be achieved two different ways.
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
the repository is accessible by whoever is going to load databases on your system.  

For the rest of this document, we will assume the PhiloLogic source code is installed in 
your home directory at ~/PhiloLogic4/

Prerequisites
------------
Python
GCC
Make
`gdbm`_
libxml
`LXML`_
`Mako`_

Installing the C library
------------------------------

Installing PhiloLogic's libraries requires administrator privileges.
This C library, depends on `gdbm`_, which *must* be installed first, to compile correctly.
Installation is standard for a Makefile-style distribution.

    cd ~/PhiloLogic4/libphilo
    make
    sudo make install

The binaries resulting of compilation process are
``~/PhiloLogic4/libphilo/search4`` and ``~/PhiloLogic4/libphilo/db/pack4``.
They are then copied into the execution directory, usually ``/bin``.

.. note::

    See ``libphilo/README`` document for further details.


Installing `Python` ``philologic`` library system-wide
------------------------------------------------------

Once ``libphilo`` is installed, we need to install its `Python` bindings
and library: ``philologic``. Once again, this step requires administrator
privileges. You probably want to install it's prerequistes, 'lxml'_ and 'mako'_, first.

Installation could be reached through its
``~/PhiloLogic4/python/setup.py`` package setup::

    cd ~/PhiloLogic4/python
    sudo python setup.py install

or via the pip command::

    cd ~/PhiloLogic4/python
    sudo pip install .


Setting up PhiloLogic Web Services
---------------------------------------------

A new database, filled with one or more `TEI-XML` corpus file, will be served
by a its own dedicated version of `PhiloLogic` web application.
By convention, this database and web app reside together in a directory
accessible via an HTTP server configure to run Python CGI scripts.

In Mac OS X systems, you will probably want to create a directory at
``/Library/WebServer/Documents/philologic`` to serve up PhiloLogic databases
with the URL prefix: ``http://<your_server's_name>/philologic/``; for Linux systems, 
the proper directory may vary, but ``/var/www/philologic/`` or ``/var/www/html/philologic/``

Configuring your web server is outside of the scope of this document;
if in doubt, ask your sysadmin, or ask Google.  


.. note::

    See ``www/README`` document for further details,
    including needed dependencies.


Dependencies
^^^^^^^^^^^^

`PhiloLogic4` web application obviously requires both ``libphilo`` and
``philologic`` libraries to be installed (see above), but it also
depends on `Mako`_ templating engine [1]_. If `Mako`_ is not provided by
your operating system package, or provided version is too old,
we advice to install a fresh one via `pip`_ [2]_::

    sudo pip install Mako

Running the ``loader.py`` depends itself on `lxml`_, and previous remark for
`Mako` also applies here::

    sudo pip install lxml


Customize ``load_script.py``
^^^^^^^^^^^^^^^^^^^^^^^

So the ``load_script.py`` is the central piece of software generating database and
web application from web application *template* and `TEI-XML` corpus files,
and you **must customize** it. Given a set of this `TEI-XML` files,
located for e.g. at ``~/mycorpus/xml`` directory, we could put a copy
of ``~/PhiloLogic4/scripts/load_script.py`` in ``~/mycorpus``::

    cp ~/PhiloLogic4/scripts/load_script.py ~/mycorpus/

It could be possible to also tweak the web application template to better
fullfill your corpora specificities or needs, but for the sake of current
example, we assume you'll simply started with bare ``~/PhiloLogic4/www``'s one.

The main *required* variables of ``load_script.py`` to be set are located
around lines 25-44, and are ``database_root``, ``url_root``
and ``template_dir``. Following previous example, we must set
``database_root`` variable to ``'/var/www/html/mydatabase/'``
-- with an ending slash! --, and ``url_root`` set to e.g.
``'http://localhost/mydatabase'``. Also, as we use ``~/PhiloLogic4/www``
sources as bare web application template, we must tweaked ``template_dir``
as follows::

    # variables are set to None by default,
    # and *must* be set to values according to *your* current installation,
    # for example:
    database_root = '/var/www/html/mydatabase/'
    url_root = 'http://localhost/mydatabase'
    template_dir = '~/PhiloLogic4/www'


Loading
^^^^^^^

Once all files are in place and ``load_script.py`` script customized, it's time
for `PhiloLogic` to generates all stuff it needs, by executing script
on `TEI-XML` files::

    python ~/mycorpus/load_script.py [database name] [path to TEI-XML files]

This script required the following arguments:

1.  the name of the database to create, which will be the subdirectory
    into ``/var/www/html`` directory, i.e. ``mydatabase``,
2.  the paths to each of `TEI-XML` files from which fulfill database content,
    i.e. ``~/mycorpus/xml/*.xml``.

The full list of arguments ``load_script.py`` accepts is set in its body
around 15-25 lines, and showable when running ``loader.py`` without
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
directory with both web application and data files::

    ls -l /var/www/html/mydatabase

Layout of a PhiloLogic Web Application Instance
-----------------------------------------------

This database directory now contains *both* `PhiloLogic` web application, at the root,
with the indexes and other data structures, in a ``data`` subdirectory.
At the end of generation, this directory will look like this tree::

    --- /var/www/html
      \--- mydatabase
        \--- css
        \--- data
        \--- functions
        \--- js
        \--- reports
        \--- scripts
        \--- templates
        \--- .htaccess
        \--- dispatcher.py

----

.. Footnotes:

.. [1]
    See ``requirement.rst`` document of a synthetical list of all dependencies.
.. [2]
    Installing a `Python` package via `pip`_ allows an easy deinstallation.
    It's also an easy way to get the last version of a package,
    or a specific one.

.. Links:

.. _git: http://git-scm.com/
.. _gdbm: http://www.gnu.org.ua/software/gdbm/
.. _pip: http://www.pip-installer.org/
.. _Apache httpd: http://httpd.apache.org/
.. _Mako: http://makotemplates.org/
.. _lxml: http://lxml.de/
