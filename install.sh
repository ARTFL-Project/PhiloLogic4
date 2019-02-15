#!/bin/sh

CORE_INSTALL="\n## INSTALLING PHILOLOGIC C CORE ##"
echo "$CORE_INSTALL"
cd libphilo/
make clean
make
if [[ $OSTYPE == 'darwin'* ]];
then
  sudo /usr/bin/install -c search5 /usr/local/bin/
  sudo /usr/bin/install -c db/pack5 /usr/local/bin/
else
  sudo /usr/bin/install -c search5 /bin/
  sudo /usr/bin/install -c db/pack5 /bin/
fi

cd ..;
PYTHON_INSTALL="\n## INSTALLING PYTHON LIBRARY ##"
echo "$PYTHON_INSTALL"
cd python;
sudo -H pip3 install --upgrade .
sudo mkdir -p /etc/philologic/

cd ..;
sudo mkdir -p /var/lib/philologic5/web_app/
sudo rm -rf /var/lib/philologic5/web_app/*
sudo cp -R www/* /var/lib/philologic5/web_app/
sudo cp www/.htaccess  /var/lib/philologic5/web_app/

# WEB_LOADER_CONFIG="\nAlias /philoload5 /var/lib/philologic5/web_loader
# <Directory /var/lib/philologic5/web_loader>
# Order allow,deny
# Allow from all
# AllowOverride All
# Require all granted
# </Directory>"
# echo "Copying web loader to /var/lib/philologic5/web_loader"
# echo "If you wish to enable that functionality,"
# echo "you will need to paste the following in your Apache config:"
# echo "$WEB_LOADER_CONFIG"
# sudo rm -rf /var/lib/philologic5/web_loader
# sudo cp -R extras/web_loader /var/lib/philologic5/web_loader
# sudo cp -R www/app/assets/css/split/style.css /var/lib/philologic5/web_loader/
# sudo cp -R www/app/assets/css/split/default_theme.css /var/lib/philologic5/web_loader/

if [ ! -f /etc/philologic/philologic5.cfg ]
    then
        db_url="# Set the filesytem path to the root web directory for your PhiloLogic install.
        database_root = None
        # /var/www/html/philologic/ is conventional for linux,
        # /Library/WebServer/Documents/philologic for Mac OS.\n"
        echo "$db_url" | sed "s/^ *//g" | sudo tee /etc/philologic/philologic5.cfg > /dev/null
        url_root="# Set the URL path to the same root directory for your philologic install.
        url_root = None
        # http://localhost/philologic/ is appropriate if you don't have a DNS hostname.\n"
        echo "$url_root" | sed "s/^ *//g" | sudo tee -a /etc/philologic/philologic5.cfg > /dev/null
        web_app_dir="## This should be set to the location of the PhiloLogic5 www directory
        web_app_dir = '/var/lib/philologic5/web_app/'"
        echo "$web_app_dir" | sed "s/^ *//g" | sudo tee -a /etc/philologic/philologic5.cfg > /dev/null
        theme="# Point to a default theme to use for all your PhiloLogic5 loads.\n
        theme = '/var/lib/philologic5/web_app/app/assets/css/split/default_theme.css'"
        echo "$theme" | sed "s/^ *//g" | sudo tee -a /etc/philologic/philologic5.cfg > /dev/null
else
    echo "\n## WARNING ##"
    echo "/etc/philologic/philologic5.cfg already exists"
    echo "Please delete and rerun the install script to avoid incompatibilities\n"
fi
