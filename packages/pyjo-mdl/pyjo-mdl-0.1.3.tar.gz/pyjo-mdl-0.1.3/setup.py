#!/usr/bin/env python
from setuptools import setup, find_packages
import re

with open('pyjo_mdl/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE).group(1)
if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name='pyjo-mdl',
    version=version,
    description='Model Definition Language for Pyjo',
    url='https://github.com/xelhark/pyjo-mdl',
    long_description=open('README.md').read(),
    author='Gabriele Platania',
    author_email='gabriele.platania@gmail.com',
    packages=find_packages(),  # ['pyjo_mdl'],
    package_data={'': ['LICENSE']},
    install_requires=[
        'pyjo'
    ],
)
