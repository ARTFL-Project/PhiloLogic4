Installing PhiloLogic on Mac OSX
================================

Note: these instructions were only tested on Mac OSX Yosemite.

* Install Homebrew for easy installation of dependencies: see <a href="http://brew.sh/">here</a>

* Install gdbm:

`brew install gdbm`

* Install pip:

`sudo easy_install pip`

* Install mako and LXML

`sudo pip install mako`

`sudo pip install lxml`

- Download Philo4: click on download zip
In the future, go in releases. 

- Install search core:
in lib/
make
sudo make install

- Install Python bindings:
in python/
sudo python setup.py install

- Configure Apache:
sudo vim /etc/apache2/httpd.conf
* uncomment: LoadModule cgi_module libexec/apache2/mod_cgi.so
* In <Directory "/Library/WebServer/Documents”>, change AllowOverride None to All

- Create philo4 directory and give proper permissions
sudo mkdir /Library/WebServer/Documents/philologic4/
sudo chmod -R username /Library/WebServer/Documents/philologic4/
OR
sudo chgrp -R group /Library/WebServer/Documents/philologic4/
sudo chmod 775 /Library/WebServer/Documents/philologic4/

- Start apache
sudo apachectl start
