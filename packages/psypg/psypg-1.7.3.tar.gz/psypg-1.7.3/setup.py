#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='psypg',
    version='1.7.3',
    description='Simple Python wrapper for Psycopg2',
    author='Gary Chambers',
    author_email='gwc@gwcmail.com',
    url='https://gitlab.com/amos_moses/psypg',
    packages=['psypg'],
    install_requires=['psycopg2-binary']
)
