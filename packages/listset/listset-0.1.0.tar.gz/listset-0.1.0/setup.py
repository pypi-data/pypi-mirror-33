#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='listset',
    version='0.1.0',
    description='remove duplicates from lists',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jmsv/listset',
    author='James Vickery',
    author_email='dev@jamesvickery.net',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=2.6, !=3.0.*, !=3.1.*, <4',
    keywords='list set duplicates listset',
    packages=['listset'],
    project_urls={
        'Source': 'https://github.com/jmsv/listset',
        'Bug Reports': 'https://github.com/jmsv/listset/issues',
    },
)
