#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '0.1.0'

setup(
    name='konfiture',
    version=__version__,
    license='GPL3',
    description='Smart markdown grammar and spelling checker',
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/konfiture/konfiture',
    scripts=['scripts/konfiture'],
    install_requires=['mistune', 'termcolor'],
    packages=find_packages(exclude=['tests*']),
)
