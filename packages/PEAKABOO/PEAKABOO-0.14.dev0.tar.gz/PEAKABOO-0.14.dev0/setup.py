#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 26 15:47:58 2018

@author: demiliu
"""

import os
from setuptools import setup, find_packages
PACKAGES = find_packages()

# Get version and release info, which is all stored in peakaboo/version.py
ver_file = 'peakaboo/version.py'
with open(ver_file) as f:
    exec(f.read())

opts = dict(name=NAME,
            maintainer=MAINTAINER,
            maintainer_email=MAINTAINER_EMAIL,
            description=DESCRIPTION,
            long_description=LONG_DESCRIPTION,
            url=URL,
            download_url=DOWNLOAD_URL,
            license=LICENSE,
            classifiers=CLASSIFIERS,
            author=AUTHOR,
            author_email=AUTHOR_EMAIL,
            platforms=PLATFORMS,
            version=VERSION,
            packages=PACKAGES,
            package_data=PACKAGE_DATA,
            include_package_data=True,            
            install_requires=REQUIRES,
            requires=REQUIRES)


if __name__ == '__main__':
    setup(**opts)