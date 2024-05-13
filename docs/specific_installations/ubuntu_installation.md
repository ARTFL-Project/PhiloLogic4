---
title: Installing PhiloLogic4 on Ubuntu
---

-   The following dependencies need to be installed:

    -   libxml2-dev
    -   libxslt-dev
    -   zlib1g-dev
    -   apache2
    -   libgdbm-dev
    -   libgdbm-dev
    -   liblz4-tool
    -   brotli
    -   ripgrep

    Run the following command:

    `sudo apt-get install libxml2-dev libxslt-dev zlib1g-dev apache2 libgdbm-dev liblz4-tool brotli ripgrep`

- Install pip3 (not the version from Ubuntu repos since it breaks pyproject.toml builds). First delete the python3-setuptools Ubuntu package if present: `sudo apt purge python3-setuptools`, then run:
    `wget https://bootstrap.pypa.io/get-pip.py && python3 get-pip.py`

-   Run install script inside the PhiloLogic4 directory

    `./install.sh`

-   Set-up Apache:
    -   enable mod_rewrite: `sudo a2enmod rewrite`
    -   enable mod_cgi: `sudo a2enmod cgi`
    -   enable brotli: `sudo a2enmod brotli`
    -   Make sure to set `AllowOverride` to `all` for the directory containined your philologic databases in your Apache config
