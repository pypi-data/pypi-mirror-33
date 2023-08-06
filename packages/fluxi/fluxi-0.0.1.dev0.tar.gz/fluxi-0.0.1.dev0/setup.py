#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#
# Copyright (C) 2018, Maximilian Köhl <mail@koehlma.de>

from setuptools import setup

# TODO: choose an appropriate license
# LICENSE = 'License :: OSI Approved :: GNU Affero General Public License v3'


setup(
    name='fluxi',
    version='0.0.1.dev0',
    description='Fluxi',
    long_description='Fluxi, the stream-based programming framework for humans!.',
    
    author='Maximilian Köhl',
    author_email='mail@koehlma.de',
    url='https://www.koehlma.de/fluxi',

    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-cov'],
    
    packages=['fluxi'],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        # LICENSE,  # TODO: choose an appropriate license
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ]
)
