Configuring PhiloLogic's Web Application
========================================

#### Layout of a PhiloLogic Web Application Instance ####

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

