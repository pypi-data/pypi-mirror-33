#!/usr/bin/env python

"""Distribution Utilities for crypto-cookie package
"""
__author__ = "@philipkershaw"
__date__ = "09/07/15"
__copyright__ = "(C) 2015 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
from setuptools import setup, find_packages
import os

THIS_DIR = os.path.dirname(__file__)
DESCRIPTION = 'Package to encrypt and sign cookies'

try:
    LONG_DESCR = open(os.path.join(THIS_DIR, 'README.rst')).read()
except IOError:
    LONG_DESCR = ""

setup(
    name =                  'crypto-cookie',
    version =               '0.3.1',
    description =           DESCRIPTION,
    long_description =      LONG_DESCR,
    author =                'Philip Kershaw',
    author_email =          'Philip.Kershaw@stfc.ac.uk',
    maintainer =            'Philip Kershaw',
    maintainer_email =      'Philip.Kershaw@stfc.ac.uk',
    url =                   'https://github.com/cedadev/crypto-cookie',
    license =               'BSD - See LICENCE file for details',
    classifiers=(
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ),
    install_requires =      ['cryptography'],
    packages =              find_packages(),
    entry_points =          None,
    test_suite =            'crypto_cookie.test',
    zip_safe =              False
)
