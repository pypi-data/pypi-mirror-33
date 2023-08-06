#!/usr/bin/env python
import os
import shutil
import sys
from setuptools import setup, find_packages


readme = open('README.md').read()

VERSION = '0.0.1'

requirements = [
    'numpy',
    'shapely'
]

setup(
    # Metadata
    name='wutil',
    version=VERSION,
    author='Red Pandas Team',
    author_email='param3456@gmail.com',
    description='Various utils',
    long_description=readme,
    license='BSD',

    # Package info
    packages=find_packages(exclude=('test',)),

    zip_safe=True,
    install_requires=requirements,
)
