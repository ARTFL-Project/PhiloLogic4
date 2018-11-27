Installation
============

Installing PhiloLogic consists of two steps:

1. Install the C and Python libraries system-wide
2. Set up a directory in your web server to serve databases from

You can find more detailed installation instructions for specific OSes here:
* [Mac OSX] (specific_installations/mac_installation.md) (no longer maintained)
* [RedHat (and CentOS)](specific_installations/redhat_installation.md)
* [Ubuntu](specific_installations/ubuntu_installation.md)

### Downloading ###

IMPORTANT: Do not install from the master branch on github: this is a the development branch and in no way garanteed to be stable

You can find a copy of the latest version of PhiloLogic5 [here](../../../releases/).

For the rest of this document, we will assume the PhiloLogic source code is installed in
your home directory at ~/PhiloLogic5/

### Prerequisites ###

* Python 3.5 and up
* GCC
* Make
* [gdbm](http://www.gnu.org.ua/software/gdbm/)
* LZ4

### Installing ###

Installing PhiloLogic's libraries requires administrator privileges.
The C library depends on `gdbm`_, which *must* be installed first, to compile correctly.

Just run the install.sh in the top level directory to install the C Core, Python dependencies, and the Python PhiloLogic library:

``./install.sh``

### <a name="global-config"></a>Global Configuration ###

The installer creates a file in `/etc/philologic/philologic5.cfg` which contains several important global variables:

* `database_root` defines the filesytem path to the root web directory for your PhiloLogic install such as `/var/www/html/philologic`. Make sure your user or group has full write permissions to that directory.
* `url_root` defines the URL path to the same root directory for your philologic install, such as http://localhost/philologic/
* `web_app_dir` defines the location of the PhiloLogic4 www directory. By default, the installer will copy the contents of the PhiloLogic www directory (which contains the web app) to /etc/philologic/web_app/.

### Setting up PhiloLogic Web Application ###

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
