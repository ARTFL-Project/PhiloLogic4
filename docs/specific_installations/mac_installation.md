---
title: Installing PhiloLogic on Mac OSX
---

Note: these instructions were only tested on Mac OSX Yosemite.


* Install Homebrew for easy installation of dependencies: see <a href="http://brew.sh/">here</a>


* Install gdbm

 `brew install gdbm`

* Make sure your default Python is `/usr/bin/python`

  Run `which python` to check

  If you are using a different python, make sure you install the following python module to the system python.


* Install pip

 `sudo easy_install pip`

 
* Install Xcode if not already installed
 
  `xcode-select --install`


* Download latest stable PhiloLogic release from [here](../../../../releases/) and unpack the tarball

 `tar -xf PhiloLogic4.xyz.tar.gz`

 `cd PhiloLogic4/`


* Run the install script

 `./install.sh``


* Configure Apache Web Server
 * Open Apache config file:
  `sudo vim /etc/apache2/httpd.conf`

 * Make sure mod_cgi is loaded (remove the leading `#` if present in front of the following line):
 
   `LoadModule cgi_module libexec/apache2/mod_cgi.so`
    
 * Make sure the mod_rewrite module is loaded (remove the leading `#` if present in front of the following line):
   `LoadModule rewrite_module libexec/apache2/mod_rewrite.so`

 * In `<Directory "/Library/WebServer/Documents”>`, change `AllowOverride None` to `ÀllowOverride All`


* Create a PhiloLogic4 directory in the webspace and give proper permissions
 * Create database directory:
   `sudo mkdir /Library/WebServer/Documents/philologic4/`

 * Run one of the two following commands according to your prefered configuration:

   `sudo chown -R username /Library/WebServer/Documents/philologic4/`

    OR

    `sudo chgrp -R group /Library/WebServer/Documents/philologic4/`

 * Then run:

   `sudo chmod 775 /Library/WebServer/Documents/philologic4/`


* Start Apache Server

 `sudo apachectl start`
