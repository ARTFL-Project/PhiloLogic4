Installing PhiloLogic on Mac OSX
================================

Note: these instructions were only tested on Mac OSX Yosemite.

##### Install Homebrew for easy installation of dependencies: see <a href="http://brew.sh/">here</a> #####


##### Install gdbm #####

`brew install gdbm`


##### Install pip #####

`sudo easy_install pip`


##### Install mako and LXML #####

`sudo pip install mako`

`sudo pip install lxml`


##### Download PhiloLogic from [here](releases/) and unpack the tarball #####

`tar -xf PhiloLogic4.xyz.tar.gz`

`cd PhiloLogic4/`


##### Compile and install the search core #####

`cd lib``

`make`

`sudo make install`


##### Install Python bindings #####

`cd ..`

`sudo python setup.py install`


##### Configure Apache Web Server #####

`sudo vim /etc/apache2/httpd.conf``

uncomment: `LoadModule cgi_module libexec/apache2/mod_cgi.so`

In `<Directory "/Library/WebServer/Documents”>`, change `AllowOverride None` to `ÀllowOverride All`


##### Create a PhiloLogic4 directory in the webspace and give proper permissions #####

`sudo mkdir /Library/WebServer/Documents/philologic4/`

Run one of the two following commands according to your prefered configuration:

`sudo chmod -R username /Library/WebServer/Documents/philologic4/`

OR

`sudo chgrp -R group /Library/WebServer/Documents/philologic4/`

Then run:

`sudo chmod 775 /Library/WebServer/Documents/philologic4/`


##### Start Apache Server #####

`sudo apachectl start`
