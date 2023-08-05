# -*- coding: utf-8 -*-

import glob

from setuptools import setup, Extension, Distribution, find_packages

try:
	import numpy
except ImportError:
	pass

deps = glob.glob('lsl_toolkits/OldDRSpec/*.c')

extensions = [Extension('lsl_toolkits.OldDRSpec._oldfast', ['lsl_toolkits/OldDRSpec/oldfast.c'], include_dirs=[numpy.get_include()], extra_compile_args=['-DNPY_NO_DEPRECATED_API=NPY_1_7_API_VERSION', '-funroll-loops']),]

setup(
    name                 = "lsl-toolkits-olddrspec",
    version              = "0.2.2",
    description          = "LSL Toolkit for Older LWA DR Spectrometer Data", 
    long_description     = "LWA Software Library reader for older-format DR Spectrometer data (LSL 0.5.x branch)",
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
    ext_modules          = extensions,
    scripts              = glob.glob('scripts/*.py'), 
    python_requires      = '>=2.6, <3', 
    setup_requires       = ['numpy>=1.7'], 
    install_requires     = ['numpy>=1.7', 'lsl>=0.6'],
    include_package_data = True,  
    zip_safe             = False,
    test_suite           = "tests.test_drspec.drspec_tests"
)
