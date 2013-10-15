Installation
============

As described in main ``README`` document, installing `PhiloLogic` follows
each of its parts installations.


Installing library system-wide
------------------------------

Installing ``libphilo`` system-wide requires administrator privileges.
It processes in two classical steps:

1. first compiling the library into binaries,
2. then installing the fresh built material into system,

with shell commands::

    cd libphilo
    make
    sudo make install

The binaries resulting of compilation process are ``libphilo/search4``
and ``libphilo/db/pack4``. They are then copied into the execution directory,
usually ``/bin``.

.. note::

    See ``libphilo/README`` document for further details,
    including needed dependencies.


Installing library's `Python` binding system-wide
-------------------------------------------------

Once ``libphilo`` is installed, we need to install its `Python` bindings.
Once again, this step requires administrator privileges.
Installing bindings is reached by calling ``setup.py``::

    cd python
    sudo python setup.py install


Installing web application
--------------------------

Installing the web application consists on
copying ``www`` directory content in desired web app. location subdirectory.
As the application could use many databases, it's common to install it
in its own subdirectory, at same level as all databases.
The loader used for database initialization needs that the web app. files
are located in ``_system_dir/_install_dir``, such that the whole tree will
be similar to this::

    --- [web directory]
      \--- [philologic]
         \--- database1
         \--- database2
         \--- _system_dir
            \--- _install_dir

where content of ``_install_dir`` subdirectory is identical to `PhiloLogic`
``www`` source directory. For a web directory located at ``/var/www/html``,
this could be achieved by::

    sudo mkdir -p /var/www/html/philologic/_system_dir/_install_dir
    sudo cp -r /path/to/philologic4/sources/www/* /var/www/html/philologic/_system_dir/_install_dir/

.. note::

    See ``www/README`` document for further details,
    including needed dependencies.


Initializing web application with a given database
--------------------------------------------------

Once web app. is copied in its ``_system_dir/_install_dir`` directory,
the last step consists on initializing it with a database.
This is the role of ``scripts/loader.py`` module,
whose call takes two main arguments:

1. the name of the database to create, which will be the subdirectory
   into ``philologic`` directory,
2. the path to the `TEI-XML` file(s) from which fulfill database content.

But first, we need to configure this ``loader.py`` module, by editing
some of its internals in a fresh new copy::

    cd /var/www/html/philologic
    cp /path/to/philologic/sources/scripts/loader.py ./_system_dir/

The main variables to edit in this module are located at lines 25-44, as
``database_root``, ``url_root`` and others::

    database_root = None
    url_root = None
    template_dir = database_root + '_system_dir/_install_dir'

Following previous example, we must set ``database_root`` variable
to ``'/var/www/html/philologic/'`` -- with an ending slash! --,
and ``url_root`` set to e.g. ``'http://localhost/philologic'``::

    # variables are set to None by default,
    # and *must* be set to values according to *your* current installation,
    # for example:
    database_root = '/var/www/html/philologic/'
    url_root = 'http://localhost/philologic'

Then, we can call ``loader.py``:

    cd _system_dir
    python loader.py database1 /path/to/corpus1.xml /path/to/corpus2.xml

This will compute databases indexes needed by `PhiloLogic` for this
specific corpus.

.. note::

    See ``apache`` document for further details about setting up `Apache`
    web server.

