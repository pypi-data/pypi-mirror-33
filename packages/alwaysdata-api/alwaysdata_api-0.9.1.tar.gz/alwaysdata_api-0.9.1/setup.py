#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""`alwaysdata_api` provides a dead simple Python interface to the
Alwaysdata API (at https://api.alwaysdata.com/).

    >>> from alwaysdata_api import Config, Domain, Record
    >>> auth = ('MY_API_KEY account=MY_ACCOUNT', '')
    >>> config = Config(auth)
    >>> # List all domains.
    >>> domains = Domain.list(config=config)
    >>> domains
    >>> # Find nameserver records in the DNS.
    >>> domain = domains[0]
    >>> records = Record.list(domain=domain.id, type='NS', config=config)
    >>> records
    >>> # Print the WHOIS information.
    >>> print(domain.whois())

`Config` is a namedtuple with the authentication credentials and server
root URL. By default, it reads the API key and account name from the
environment variables `ALWAYSDATA_API_KEY` and `ALWAYSDATA_ACCOUNT`
respectively. If these are set, all auth and config can be dropped from
the above example.
"""
from setuptools import setup

LONG_DESCRIPTION = __doc__

INSTALL_REQUIRES = ['setuptools', 'requests>=2.1.0']


setup(
    name='alwaysdata_api',
    version='0.9.1',
    author='Paul Koppen',
    author_email='alwaysdata-api@paulkoppen.com',
    description='A dead simple Python interface to the Alwaysdata API.',
    license='MIT License',
    keywords='api domain subdomain management web',
    url='https://gitlab.com/wpk-/alwaysdata-api',
    packages=['alwaysdata_api'],
    long_description=LONG_DESCRIPTION,
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
)
