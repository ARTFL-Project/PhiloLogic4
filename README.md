PhiloLogic4
===========

PhiloLogic is an XML database/search engine/web app that is designed 
for the particular difficulties of TEI XML.  For a more theoretical 
description, you can refer to `our research publications <http://http://jtei.revues.org/817>`_ or `our blog <http://artfl.blogspot.com>`_.


Documentation
=============
* [**Installation**](docs/installation.md)


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
