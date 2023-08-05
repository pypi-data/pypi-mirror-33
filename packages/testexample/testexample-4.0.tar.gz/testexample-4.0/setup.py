#!/usr/bin/env python

from distutils.core import setup


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='testexample',
    version='4.0',
    description='${library_description}',
    packages=['testexample'],
    install_requires=required
)
