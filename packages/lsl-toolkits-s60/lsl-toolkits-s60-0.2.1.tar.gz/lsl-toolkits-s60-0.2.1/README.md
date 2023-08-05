LSL Toolkit for S60 Data
========================

DESCRIPTION
-----------
This package provides the S60 data reader and simulator found in
in LSL versions up to the 0.4.x branch.

REQUIREMENTS
------------
  * python >= 2.6 and python < 3.0
  * numpy >= 1.2

BUILDING
--------
The S60 package is installed as a regular Python package using distutils.  
Unzip and untar the source distribution. Setup the python interpreter you 
wish to use for running the package applications and switch to the root of 
the source distribution tree.

To build the S60 package, run:
    
    python setup.py build
    
TESTING
-------
To test the as-build S60 package, run:
    
    python setup.py test

INSTALLATION
------------
Install S60 by running:
    
    python setup.py install [--prefix=<prefix>|--user]

If the '--prefix' option is not provided, then the installation 
tree root directory is the same as for the python interpreter used 
to run `setup.py`.  For instance, if the python interpreter is in 
'/usr/local/bin/python', then <prefix> will be set to '/usr/local'.
Otherwise, the explicit <prefix> value is taken from the command line
option.  The package will install files in the following locations:
  * <prefix>/bin
  * <prefix>/lib/python2.6/site-packages
  * <prefix>/share/doc
  * <prefix>/share/install

If an alternate <prefix> value is provided, you should set the PATH
environment to include directory '<prefix>/bin' and the PYTHONPATH
environment to include directory '<prefix>/bin' and the PYTHONPATH
environment to include directory '<prefix>/lib/python2.6/site-packages'.

If the '--user' option is provided, then then installation tree root 
directory will be in the current user's home directory.

DOCUMENTATION
-------------
See the module's internal documentation.

RELEASE NOTES
-------------
See the CHANGELOG for a detailed list of changes and notes.
