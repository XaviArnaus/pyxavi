#!/usr/bin/env python

from distutils.core import setup

setup(
    name='Python Bundle',
    version='0.0.6',
    description='Simple Python utilities for small apps',
    author='Xavier Arnaus',
    author_email='xavi@arnaus.net',
    url='https://github.com/XaviArnaus/python-bundle',
    packages=['bundle'],
    install_requires=[
       'bs4',
   ],
)