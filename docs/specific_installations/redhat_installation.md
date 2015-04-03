Installing PhiloLogic on RedHat (and CentOS)
============================================

* Install gdbm

  `sudo yum install gdbm gbdm-devel`

* Install lxml

  `sudo yum install lxml`
  
* [Download PhiloLogic](releases/)

* Compile and install C Core

  `cd lib`
  
  `make`
  
  `sudo make install`

* Install Python bindings

  `cd python`
  
  `sudo python setup.py install`

* Configure Apache
  * Make sure your prefered webspace allows full override for htaccess files: `AllowOverride All`
  * Make sure the correct permissions are set on the folder dedicated to PhiloLogic databases, 
    i.e. write access for the user/group that will be building databases.
