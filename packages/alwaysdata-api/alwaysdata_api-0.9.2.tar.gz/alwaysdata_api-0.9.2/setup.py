#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`alwaysdata_api` provides a dead simple Python interface to the
Alwaysdata API (at https://api.alwaysdata.com/).

See the README.md for details.
"""
from os.path import dirname, join as joinpath
from setuptools import setup


def read(fname):
    with open(joinpath(dirname(__file__), fname)) as f:
        return f.read()


LONG_DESCRIPTION = read('README.md')

INSTALL_REQUIRES = ['setuptools', 'requests>=2.1.0']


setup(
    name='alwaysdata_api',
    version='0.9.2',
    author='Paul Koppen',
    author_email='alwaysdata-api@paulkoppen.com',
    description='A dead simple Python interface to the Alwaysdata API.',
    license='MIT License',
    keywords='api domain subdomain management web',
    url='https://gitlab.com/wpk-/alwaysdata-api',
    packages=['alwaysdata_api'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
    install_requires=INSTALL_REQUIRES,
    zip_safe=True,
)
