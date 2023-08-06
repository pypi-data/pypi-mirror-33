#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '0.1.1'

setup(
    name='choukette',
    version=__version__,
    description='Badges creator',
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/choukette/choukette',
    scripts=['scripts/choukette'],
    install_requires=['future'],
    packages=find_packages(exclude=['tests*']),
)
