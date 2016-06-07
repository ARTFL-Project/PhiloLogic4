* The following dependencies need to be installed:
  * libxml2-dev
  * libxslt-dev
  * python-pip
  * zlib1g-dev
  * apache2

  Run the following command:

  `sudo apt-get install libxml2-dev libxslt-dev python-pip zlib1g-dev apache2`

* Set-up Apache:
  * enable mod_rewrite: `sudo a2enmod rewrite`
  * enable mod_cgi: `sudo a2enmod cgi`
