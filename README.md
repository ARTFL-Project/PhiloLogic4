PhiloLogic4
===========

PhiloLogic is an XML database/search engine/web app that is designed 
for the particular difficulties of TEI XML.  For a more theoretical 
description, you can refer to `our research publications <http://http://jtei.revues.org/817>`_ or `our blog <http://artfl.blogspot.com>`_.


Documentation
=============
* [**Installation**](docs/installation.md)
* [**Database Loading**](docs/database_loading.md)

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

