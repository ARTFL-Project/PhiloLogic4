---
title: Installing PhiloLogic4 on Ubuntu
---

-   The following dependencies need to be installed:

    -   libxml2-dev
    -   libxslt-dev
    -   zlib1g-dev
    -   apache2
    -   libgdbm-dev
    -   python3-pip
    -   libgdbm-dev
    -   liblz4-tool
    -   brotli

    Run the following command:

    `sudo apt-get install libxml2-dev libxslt-dev zlib1g-dev apache2 libgdbm-dev python3-pip liblz4-tool brotli`

-   Run install script inside the PhiloLogic4 directory

    `./install.sh`

-   Set-up Apache:
    -   enable mod_rewrite: `sudo a2enmod rewrite`
    -   enable mod_cgi: `sudo a2enmod cgi`
    -   enable brotli: `sudo a2enmod brotli`
