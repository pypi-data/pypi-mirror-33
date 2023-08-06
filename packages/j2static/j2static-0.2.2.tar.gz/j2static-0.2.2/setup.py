#!/usr/bin/env python3
##
# Based on the setuptools example
##

from setuptools import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='j2static',
    version='0.2.2',
    description='static templating engine',
    long_description=long_description,
    author='FOSS Galaxy',
    author_email='software@fossgalaxy.com',
    url='https://www.fossgalaxy.com',
    install_requires=[
        'jinja2',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3'
    ],
    test_suite='tests',
    packages=['j2static', 'j2static.tools' ],
    package_dir={'j2static': 'j2static'},
    entry_points={
        'console_scripts': [
            'j2static=j2static.cli:main',
            'j2merge=j2static.cli_merge:main'
        ],
    },
)
