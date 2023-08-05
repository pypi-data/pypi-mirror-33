# -*- coding: utf-8 -*-

import glob

from setuptools import setup, Extension, Distribution, find_packages

try:
	import numpy
except ImportError:
	pass

setup(
    name                 = "lsl-toolkits-s60",
    version              = "0.2.1",
    description          = "LSL Toolkit for S60 data", 
    long_description     = "LWA Software Library reader for S60 data", 
    url                  = "https://fornax.phys.unm.edu/lwa/trac/", 
    author               = "Jayce Dowell",
    author_email         = "jdowell@unm.edu",
    license              = 'GPL',
    classifiers          = ['Development Status :: 7 - Inactive',
                            'Intended Audience :: Developers',
                            'Intended Audience :: Science/Research',
                            'License :: OSI Approved :: GNU General Public License (GPL)',
                            'Topic :: Scientific/Engineering :: Astronomy',
                            'Programming Language :: Python :: 2',
                            'Programming Language :: Python :: 2.6',
                            'Programming Language :: Python :: 2.7',
                            'Operating System :: MacOS :: MacOS X',
                            'Operating System :: POSIX :: Linux'],
    packages             = find_packages(exclude="tests"), 
    namespace_packages   = ['lsl_toolkits',],
    scripts              = glob.glob('scripts/*.py'), 
    python_requires      = '>=2.6, <3', 
    setup_requires       = ['numpy>=1.2'], 
    install_requires     = ['numpy>=1.2'],
    include_package_data = True,  
    zip_safe             = False,  
    test_suite           = "tests.test_s60.s60_tests"
)
