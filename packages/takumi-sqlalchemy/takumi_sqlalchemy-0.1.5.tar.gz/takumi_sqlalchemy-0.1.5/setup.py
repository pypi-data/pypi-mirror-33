#! /usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='takumi_sqlalchemy',
    version='0.1.5',
    description='Sqlalchemy utilities for Takumi',
    long_description=open("README.rst").read(),
    author="Eleme Lab",
    author_email="imaralla@icloud.com",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemepi/takumi-sqlalchemy',
    install_requires=[
        'takumi',
        'takumi-config',
        'sqlalchemy',
    ],
)
