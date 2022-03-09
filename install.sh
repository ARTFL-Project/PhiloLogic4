#!/bin/sh

CORE_INSTALL="\n## INSTALLING PHILOLOGIC C CORE ##"
echo "$CORE_INSTALL"
cd libphilo/
make clean
make
if [[ $OSTYPE == 'darwin'* ]];
then
  sudo /usr/bin/install -c db/corpus_search /usr/local/bin/
  sudo /usr/bin/install -c db/pack4 /usr/local/bin/
else
  sudo /usr/bin/install -c db/corpus_search /bin/
  sudo /usr/bin/install -c db/pack4 /bin/
fi

cd ..;
PYTHON_INSTALL="\n## INSTALLING PYTHON LIBRARY ##"
echo "$PYTHON_INSTALL"
cd python;
sudo -H pip3 install --upgrade .
sudo mkdir -p /etc/philologic/

cd ..;
sudo mkdir -p /var/lib/philologic4/web_app/
sudo rm -rf /var/lib/philologic4/web_app/*
if [ -d www/app/node_modules ]
    then
        sudo rm -rf www/app/node_modules
fi
sudo cp -R www/* /var/lib/philologic4/web_app/
sudo cp www/.htaccess  /var/lib/philologic4/web_app/

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
