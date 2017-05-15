## Installing PhiloLogic4 on Ubuntu ##

* The following dependencies need to be installed:
  * libxml2-dev
  * libxslt-dev
  * python-pip
  * zlib1g-dev
  * apache2
  * libgdbm-dev
  * python3-pip

  Run the following command:

  `sudo apt-get install libxml2-dev libxslt-dev python-pip zlib1g-dev apache2 libgdbm-dev python3-pip`
  
* Run install script inside the PhiloLogic4 directory

  `./install.sh`

* Set-up Apache:
  * enable mod_rewrite: `sudo a2enmod rewrite`
  * enable mod_cgi: `sudo a2enmod cgi`
