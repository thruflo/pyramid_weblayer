#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os.path import dirname, join as join_path
from setuptools import setup, find_packages

def _read(file_name):
    sock = open(file_name)
    text = sock.read()
    sock.close()
    return text



setup(
    name = 'pyramid_weblayer',
    version = '0.14.5',
    description = 'Common / reusable utilities for a Pyramid web application.',
    author = 'James Arthur',
    author_email = 'username: thruflo, domain: gmail.com',
    url = 'http://github.com/thruflo/pyramid_weblayer',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Framework :: Pylons',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    license = _read('UNLICENSE').split('\n')[0],
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    include_package_data = True,
    zip_safe = False,
    install_requires=[
        'html2text',
        'markdown2',
        'pyga',
        'pyramid',
        'pyramid_basemodel',
        'pyramid_hsts',
        'pyramid_layout',
        'transaction',
        'zope.interface'
    ],
    tests_require = [
        'coverage',
        'nose',
        'mock',
        'WebTest>=1.3.1',
    ]
)
