#! /usr/bin/env python
"""Toolbox for streaming data."""
from __future__ import absolute_import

import codecs
import os

from setuptools import find_packages, setup

# get __version__ from _version.py
ver_file = os.path.join('weles', '_version.py')
with open(ver_file) as f:
    exec(f.read())

DISTNAME = 'weles'
DESCRIPTION = 'Supplementary scikit-learn package with methods developed in W4K2.'
MAINTAINER = 'P. Ksieniewicz'
MAINTAINER_EMAIL = 'pawel.ksieniewicz@pwr.edu.pl'
URL = 'https://github.com/w4k2/weles'
LICENSE = 'MIT'
DOWNLOAD_URL = 'https://github.com/w4k2/weles'
VERSION = __version__
INSTALL_REQUIRES = ['numpy', 'scipy', 'scikit-learn','future']


setup(name=DISTNAME,
      maintainer=MAINTAINER,
      maintainer_email=MAINTAINER_EMAIL,
      description=DESCRIPTION,
      license=LICENSE,
      url=URL,
      version=VERSION,
      download_url=DOWNLOAD_URL,
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES)
