#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

config = {
    'name': 'mitsPy',
    'author': 'Avraham David Gelbfish',
    'author_email': 'adg@adgelb.fish',
    'url': '',
    'description': '',
    'long_description': open('README.rst', 'r').read(),
    'license': 'MIT',
    'version': '0.1.7',
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 2 - Pre-Alpha",
    ],
    'packages': find_packages(),
}

if __name__ == '__main__':
    setup(**config, install_requires=['xmltodict', 'aiohttp'])
