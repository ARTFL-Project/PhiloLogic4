Installing PhiloLogic on RedHat (and CentOS)
============================================

* Install gdbm

  `sudo yum install gdbm gbdm-devel`


* Run install script

  `./install.sh`

* Configure Apache
  * Make sure your prefered webspace allows full override for htaccess files: `AllowOverride All`
  * Make sure the correct permissions are set on the folder dedicated to PhiloLogic databases, 
    i.e. write access for the user/group that will be building databases.
