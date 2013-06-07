#!/usr/bin/env python
# -*- coding: utf-8 -
#
# This file is part of socketpool.
# See the NOTICE for more information.


import os
from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Software Development :: Libraries']


# read long description
with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    long_description = f.read()

DATA_FILES = [
        ('socketpool', ["LICENSE", "MANIFEST.in", "NOTICE", "README.rst",
                        "THANKS", "UNLICENSE"])
        ]


setup(name='socketpool',
      version='0.5.3',
      description = 'Python socket pool',
      long_description = long_description,
      classifiers = CLASSIFIERS,
      license = 'BSD',
      url = 'http://github.com/benoitc/socketpool',
      packages=find_packages(),
      data_files = DATA_FILES)
