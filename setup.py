#!/usr/bin/env python
from setuptools import setup
from fredapi import __version__

# requires = ['pandas >= 0.13', 'python-dateutil']
requires = ['pandas', 'python-dateutil']

# README = open('README.rst').read()
# CHANGELOG = open('docs/changelog.rst').read()
LONG_DESCRIPTION = open('DESCRIPTION.rst').read()

setup(
    name="fredapi",
    version=__version__,
    url='https://github.com/mortada/fredapi',
    author='Mortada Mehyar',
    # author_email='',
    description="Python API for Federal Reserve Economic Data (FRED) from St. Louis Fed",
    long_description=LONG_DESCRIPTION,
    packages=['fredapi'],
    platforms=["Any"],
    install_requires=requires,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Operating System :: OS Independent',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
