#!/usr/bin/env python
from setuptools import setup

import netaxept

setup(
    name='django-netaxept-gateway',
    version=netaxept.__version__,
    description='Integrate django with the netaxept payment service provider',
    long_description='',
    author='Nicholas Wolff',
    author_email='nwolff@gmail.com',
    url=netaxept.__URL__,
    download_url='https://pypi.python.org/pypi/django-datatrans-gateway',
    install_requires=[
        'Django>=2.0',
        'structlog',
        'suds2',
        'requests',
    ],
    packages=[
        'netaxept',
        'netaxept.migrations',
        'netaxept.views',
    ],
    package_data={'netaxept': [
        'templates/admin/netaxept/*.html',
        'templates/netaxept/example/*.html',
    ]},
    licence=netaxept.__license__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
