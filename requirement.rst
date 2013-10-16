Requirement
===========

`PhiloLogic4` currently needs additional softwares do be available
on your system:

+-----------------------+-----------------------+-------------------------+
| 3rd party             | versions              | `PhiloLogic4` component |
+=======================+=======================+=========================+
| operating system      | Linux/Unix, Mac OS X  |                         |
+-----------------------+-----------------------+-------------------------+
| `gdbm`_               |                       | ``libphilo``            |
+-----------------------+-----------------------+-------------------------+
| `Python` interpreter  | 2.6, 2.7              | ``philologic`` module   |
+-----------------------+-----------------------+-------------------------+
| `lxml`_               |                       | ``philologic`` module   |
+-----------------------+-----------------------+-------------------------+
| `Mako`_               |                       | web application         |
+-----------------------+-----------------------+-------------------------+
| `Apache httpd`_       |                       | web application         |
+-----------------------+-----------------------+-------------------------+


Also, *installation* of both dependancies and component could require
other softwares:

+-----------------------------------+-------------------+
| component                         | installer         |
+===================================+===================+
| ``libphilo``                      | `GNU Make`_       |
+-----------------------------------+-------------------+
| ``philologic`` `Python` module    | `pip`_ [1]_       |
+-----------------------------------+-------------------+
| `lxml`_                           | `pip`_ [1]_, [2]_ |
+-----------------------------------+-------------------+
| `Mako`_                           | `pip`_ [1]_, [2]_ |
+-----------------------------------+-------------------+


----

.. Footnotes:

.. [1]
    Using `pip`_ to install a `Python` package allows its future
    deinstallation. Depending on your operating system and Python environement,
    `pip`_ could already be installed or not, and available as a distribution
    package. See `pip`_ documentation in last resort.
.. [2]
    If 3rd party `Python` package, such as `Mako`_ or `lxml`_ is available
    as a package for your current distribution, it could be to old for running
    `PhiloLogic4`. A common way to get last recent version of it is
    installing this package via `pip`  [1]_, e.g.::

        pip install lxml Mako

.. Links:

.. _gdbm: http://www.gnu.org.ua/software/gdbm/
.. _lxml: http://lxml.de/
.. _Mako: http://makotemplates.org/
.. _GNU Make: http://www.gnu.org/software/make/
.. _pip: http://pip-installer.org/
.. _Apache httpd: http://httpd.apache.org/

