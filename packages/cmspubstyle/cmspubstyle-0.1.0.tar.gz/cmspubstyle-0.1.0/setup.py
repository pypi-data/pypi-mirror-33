#!/usr/bin/env python


import setuptools
from cmspubstyle.__init__ import __version__


setuptools.setup(name='cmspubstyle',
                 version=__version__,
                 description='Check CMS publications against PubComm rules',
                 author='Robin Aggleton',
                 url='https://github.com/raggleton/cmspubstyle',
                 packages=setuptools.find_packages(),
                 scripts=['cmspubstyle/pubcheck.py'],
                 classifiers=(
                     "License :: OSI Approved :: MIT License ",
                     "Programming Language :: Python :: 2.7",
                     "Programming Language :: Python :: 3.5",
                     "Programming Language :: Python :: 3.6",
                     "Topic :: Scientific/Engineering :: Physics",
                     "Topic :: Text Processing"
                 )
                 )
