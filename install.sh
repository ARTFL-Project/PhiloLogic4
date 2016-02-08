#!/bin/sh

CORE_INSTALL="\n## INSTALLING PHILOLOGIC C CORE ##"
echo "$CORE_INSTALL"
cd libphilo/
make
sudo make install
PYTHON_INSTALL="\n## INSTALLING PYTHON LIBRARY ##"
echo "$PYTHON_INSTALL"
cd ../python;
sudo pip install .
sudo mkdir -p /etc/philologic/
if [ ! -f /etc/philologic/philologic4.cfg ]
    then
        sudo rm /etc/philologic/philologic4.cfg
        db_url="# Set the filesytem path to the root web directory for your PhiloLogic install.
        database_root = None
        # /var/www/html/philologic/ is conventional for linux,
        # /Library/WebServer/Documents/philologic for Mac OS.\n"
        echo "$db_url" | sudo tee /etc/philologic/philologic4.cfg > /dev/null
        url_root="# Set the URL path to the same root directory for your philologic install.
        url_root = None
        # http://localhost/philologic/ is appropriate if you don't have a DNS hostname.\n"
        echo "$url_root" | sudo tee -a /etc/philologic/philologic4.cfg > /dev/null
        web_app_dir="## This should be set to the location of the PhiloLogic4 directory
        web_app_dir = None
        # The load process will fail if you haven't set up the web_app_dir at the correct location.\n"
        echo "$web_app_dir" | sudo tee -a /etc/philologic/philologic4.cfg > /dev/null
else
    echo "\n## WARNING ##"
    echo "/etc/philologic/philologic4.cfg already exists"
    echo "Please delete and rerun the install script to avoid incompatibilities\n"
fi
