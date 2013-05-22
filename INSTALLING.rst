Installation
============

As described in main :doc:`README`, installing `PhiloLogic` follows
each of its parts installations.


Installing library system-wide
------------------------------

Installing `libphilo` system-wide requires administrator privileges.
It processes in two classical steps:

1. first compiling the library into binaries,
2. then installing the fresh built material into system,

with shell commands:

.. code-block:: sh

    $ cd libphilo
    libphilo$ make
    libphilo$ sudo make install

The binaries resulting of compilation process are ``libphilo/search4``
and ``libphilo/db/pack4``. They are then copied into the execution directory,
usually ``/bin``.

.. seealso:: :doc:`libphilo/README` for further details,
    including needed dependencies.

.. note:: Installing library in a `virtualenv`

    It may be possible to install library in a `virtualenv`_,
    by setting ``exec_prefix`` parameter at installation,
    and pointing it to the desired `virtualenv`'s path:

    .. code-block:: sh

        # create a fresh virtualenv
        $ virtualenv --no-site-packages /path/to/philologic/venv
        # go to libphilo source directory
        $ cd libphilo
        # install libphilo in virtualenv
        libphilo$ make install exec_prefix=/path/to/philologic/venv


Installing library's `Python` binding system-wide
-------------------------------------------------

Once `libphilo` is installed, we need to install its `Python` bindings.
Once again, this step requires administrator privileges.
Installing bindings is reached by calling ``setup.py``:

.. code-block:: sh

    $ cd python
    python$ sudo python setup.py install

.. note:: Installing bindings in a `virtualenv`

    It may be possible to install `Python`'s bindings in a `virtualenv`_,
    by setting ``python`` binary to `virtualenv`'s one:

    .. code-block:: sh

        # provided a given virtualenv at /path/to/philologic/venv
        $ cd python
        python$ /path/to/philologic/venv/bin/python setup.py install

    or activating choosen `virtualenv` before installing bindings:

    .. code-block:: sh

        # provided a given virtualenv at /path/to/philologic/venv
        $ source /path/to/philologic/venv/bin/activate
        (venv) $ cd python
        (venv) python$ python setup.py install


Installing web application
--------------------------

Installing the web application consists on
copying ``www`` directory content in desired web app. location subdirectory.
As the application could use many databases, it's common to install it
in its own subdirectory, at same level than all databases.
The loader used for database initialization needs that the web app. files
are located in ``_system_dir/_install_dir``, such that the whole tree will
be similar to this:

.. code-block:: text

    --- [web directory]
      \--- [philologic]
         \--- database1
         \--- database2
         \--- _system_dir
            \--- _install_dir

where content of ``_install_dir`` subdirectory is identical to `PhiloLogic`
``www`` source directory. For a web directory located at ``/var/www/html``,
this could be achieved by:

.. code-block:: sh

    $ sudo mkdir -p /var/www/html/philologic/_system_dir/_install_dir
    $ sudo cp -r /path/to/philologic4/sources/www/* /var/www/html/philologic/_system_dir/_install_dir/

.. seealso:: :doc:`www/README` for further details,
    including needed dependencies.


Initializing web application with a given database
--------------------------------------------------

Once web app. is copied in its ``_system_dir/_install_dir`` directory,
the last step consists on initializing it with a database.
This is the role of ``scripts/loader.py`` module,
whose call takes two main arguments:

1. the name of the database to create, which will be the subdirectory
   into ``philologic`` directory,
2. the path(s) to the `TEI-XML` file(s) with which fulfill database content.

But first, we need to configure this ``loader.py`` module, by editing
some of its internals in a fresh new copy:

.. code-block:: sh

    $ cd /var/www/html/philologic
    /var/www/html/philologic$ cp /path/to/philologic4/sources/scripts/loader.py ./_system_dir/

The main variables to edit in this module are located at lines 30-45
of this ``loader.py`` module:

.. literalinclude:: scripts/loader.py
    :language: python
    :lines: 30-39,44-45

Following previous example, we must set :data:`database_root`
to ``'/var/www/html/philologic/'`` -- with an ending slash! --,
and :data:`url_root` set to e.g. ``'http://localhost/philologic'``.

Then, we can call ``loader.py``. For example, to create a database
called ``database1``, with content from two `TEI-XML` files
(``corpus1.xml`` and ``corpuse2.xml``):

.. code-block:: sh

    /var/www/html/philologic$ cd _system_dir
    /var/www/html/philologic/_system_dir$ python loader.py database1 /path/to/corpus1.xml /path/to/corpus2.xml

This will compute databases indexes needed by `PhiloLogic` for this
specific corpus.

.. seealso:: doc:`apache` for further details about setting up `Apache`
    web server.


.. _virtualenv: http://www.virtualenv.org/
