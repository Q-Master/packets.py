#!/usr/bin/env python
# setup.py
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

"""Install script for packets.py"""

# Copyright (C) 2019-2023:
# Vladimir Berezenko : qmaster 2thousand at gmail com

# This software is licensed under the terms of the MIT license.

import os
import sys

from setuptools import setup

if sys.version_info.major < 3:
    print('This code is intended to use with python 3 only')
    sys.exit(1)

__here__ = os.path.abspath(os.path.dirname(__file__))

NAME = 'packets'
PACKAGES = ['packets', 'packets.processors']
DESCRIPTION = 'Packets system for serialization/deserialization.'
URL = 'https://github.com/Q-Master/packets.py'

REQUIRES = """
    ujson
"""

VERSION = '0.6.4'


LONG_DESCRIPTION = """***packets*** - pure Python declarative packes system for serializing/deserializing
===

`packets` is my own view of declarative description of serializable/deserializable objects.

The main idea of this project is to give easiness of managing serializable objects in declarative way
without any need to implement type checking, defaults, serializing and deserializing of objects.

"""

CLASSIFIERS = [
    # Details at http://pypi.python.org/pypi?:action=list_classifiers
    'Development Status :: 5',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Programming Language :: Python :: 3.11',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries',
    'Topic :: Software Development :: Libraries :: Python Modules',
]

AUTHOR = 'Vladimir Berezenko'

AUTHOR_EMAIL = 'qmaster2000@gmail.com'

KEYWORDS = "serialization, deserialization, dictionary, application, developer, validation".split(', ')

project = dict(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    url=URL,
    packages=PACKAGES,
    install_requires=[i.strip() for i in REQUIRES.splitlines() if i.strip()],
    python_requires='>=3.0, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.*',
    classifiers=CLASSIFIERS,
    keywords=KEYWORDS,
    license='MIT',
)

if __name__ == '__main__':
    setup(**project)