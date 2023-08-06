#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""Python package for the geonames.org postcode databases

geonames_postcode is a Python package to make geonames.org postcode
databases accessible in Python. It provides a command line tool to
fetch, preprocess, and store the data in a Python file per country.
In the result very fast (in-memory) queries by postcodes and names are
available using just a few MB per country. Some helper functions are
part of the package to solve common tasks like getting distances and
finding postcodes nearby."""

from setuptools import setup

description, long_description = __doc__.split("\n\n", 1)

from geonames_postcode import version

setup(
    name='geonames_postcode',
    version=version,
    description=description,
    long_description=long_description,
    author='André Wobst',
    author_email='project.geonames_postcode@wobsta.de',
    url='https://github.com/wobsta/geonames_postcode',
    packages=['geonames_postcode', 'geonames_postcode/data'],
    package_data={
        'geonames_postcode': ['fetch.ini',
                              'data/template']
    },
    entry_points = {
        'console_scripts': ['geonames_postcode_fetch=geonames_postcode.fetch:main'],
    },
    license='GPLv2+',
    platforms='OS independent',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3'],
    zip_safe=False
)
