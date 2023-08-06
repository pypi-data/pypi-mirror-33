#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import codecs
import os
import sys
import re

try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')
_init_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "pyfly", "__init__.py")
with open(_init_file, 'rb') as f:
    version = str(_version_re.search(
        f.read().decode('utf-8')).group(1)).replace('"', "")

NAME = "pyfly"
"""
名字，一般放你包的名字即可
"""

PACKAGES = find_packages()


DESCRIPTION = "load testing framework"


LONG_DESCRIPTION = "pyfly is a python utility for doing easy, distributed load testing of a web site"


KEYWORDS = "load test"


AUTHOR = "Yang Lei"
"""
谁是这个包的作者，写谁的名字吧
我是MitchellChu，自然这里写的是MitchellChu
"""

AUTHOR_EMAIL = "yl.seu@qq.com"


URL = "https://github.com/seuman/pyfly.git"


VERSION = version

LICENSE = "MIT"

INSTALL_REQUIRES = ["gevent>=1.2.2", "flask>=0.10.1", "requests>=2.9.1", 
                    "msgpack-python>=0.4.2", "pyzmq>=16.0.2", "dash==0.21.0",
                    "dash-renderer==0.11.3", "dash-html-components==0.9.0", 
                    "dash-core-components==0.21.1", "plotly>=2.5.1" ]

setup(
    name = NAME,
    version = VERSION,
    description = DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3',
    keywords = KEYWORDS,
    author = AUTHOR,
    author_email = AUTHOR_EMAIL,
    url = URL,
    license = LICENSE,
    packages = PACKAGES,
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    zip_safe=True,
)