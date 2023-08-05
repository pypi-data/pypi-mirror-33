#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import os

from setuptools import setup, find_packages

try:
    with open('README.txt') as f:
        readme = f.read()
except IOError:
    readme = ''

def _requires_from_file(filename):
    return open(filename).read().splitlines()

# version
here = os.path.dirname(os.path.abspath(__file__))
version = next((line.split('=')[1].strip().replace("'", '')
                for line in open(os.path.join(here,
                                              'learning/',
                                              '__init__.py'))
                if line.startswith('__version__ = ')),
               '0.0.dev0')

setup(
    name="learning",
    version=version,
    url='https://github.com/kwacgit/myRecommendationSystem',
    author='Kazuya Nishi',
    author_email='nishi.k.mllab.nit@gmail.com',
    maintainer='Kazuya Nishi',
    maintainer_email='nishi.k.mllab.nit@gmail.com',
    description='For data-intern',
    long_description=readme,
    packages=find_packages(),
    install_requires=_requires_from_file('requirements.txt'),
    license="MIT",
    classifiers=[
        'License :: OSI Approved :: MIT License',
    ],
)