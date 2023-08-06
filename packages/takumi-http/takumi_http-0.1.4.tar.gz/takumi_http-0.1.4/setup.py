#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages

# Find version
here = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(here, 'takumi_http', '__version__.py'), 'r') as f:
    exec(f.read(), about)


setup(
    name='takumi_http',
    version=about['__version__'],
    description='Http to thrift protocol conversion',
    long_description=open("README.rst").read(),
    author="Eleme Lab",
    author_email="imaralla@icloud.com",
    packages=find_packages(),
    package_data={'': ['LICENSE', 'README.rst']},
    url='https://github.com/elemepi/takumi-http',
    install_requires=[
        'takumi',
        'takumi-config',
        'takumi-thrift',
        'thriftpy',
        'itsdangerous',
    ],
)
