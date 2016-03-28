#!/bin/sh

CORE_INSTALL="\n## INSTALLING PHILOLOGIC C CORE ##"
echo "$CORE_INSTALL"
cd libphilo/
make
sudo make install

cd ..;
echo "Installing Python dependencies"
sudo -H pip install -r requirements.txt

PYTHON_INSTALL="\n## INSTALLING PYTHON LIBRARY ##"
echo "$PYTHON_INSTALL"
cd python;
sudo -H pip install --upgrade .
sudo mkdir -p /etc/philologic/

cd ..;
sudo mkdir -p /var/lib/philologic4/web_app/
sudo rm -rf /var/lib/philologic4/web_app/*
sudo cp -R www/* /var/lib/philologic4/web_app/
sudo cp www/.htaccess  /var/lib/philologic4/web_app/

# WEB_LOADER_CONFIG="\nAlias /philoload /var/lib/philologic4/web_loader
# <Directory /var/lib/philologic4/web_loader>
# Order allow,deny
# Allow from all
# AllowOverride All
# Require all granted
# </Directory>"
# echo "Copying web loader to /var/lib/philologic4/web_loader"
# echo "If you wish to enable that functionality,"
# echo "you will need to paste the following in your Apache config:"
# echo "$WEB_LOADER_CONFIG"
# sudo rm -rf /var/lib/philologic4/web_loader
# sudo cp -R extras/web_loader /var/lib/philologic4/web_loader
# sudo cp -R www/app/assets/css/split/style.css /var/lib/philologic4/web_loader/
# sudo cp -R www/app/assets/css/split/default_theme.css /var/lib/philologic4/web_loader/

sudo rm /usr/bin/philoload4
sudo cp extras/philoload4.py /usr/bin/philoload4

if [ ! -f /etc/philologic/philologic4.cfg ]
    then
        db_url="# Set the filesytem path to the root web directory for your PhiloLogic install.
        database_root = None
        # /var/www/html/philologic/ is conventional for linux,
        # /Library/WebServer/Documents/philologic for Mac OS.\n"
        echo "$db_url" | sed "s/^ *//g" | sudo tee /etc/philologic/philologic4.cfg > /dev/null
        url_root="# Set the URL path to the same root directory for your philologic install.
        url_root = None
        # http://localhost/philologic/ is appropriate if you don't have a DNS hostname.\n"
        echo "$url_root" | sed "s/^ *//g" | sudo tee -a /etc/philologic/philologic4.cfg > /dev/null
        web_app_dir="## This should be set to the location of the PhiloLogic4 www directory
        web_app_dir = '/var/lib/philologic4/web_app/'"
        echo "$web_app_dir" | sed "s/^ *//g" | sudo tee -a /etc/philologic/philologic4.cfg > /dev/null
else
    echo "\n## WARNING ##"
    echo "/etc/philologic/philologic4.cfg already exists"
    echo "Please delete and rerun the install script to avoid incompatibilities\n"
fi
