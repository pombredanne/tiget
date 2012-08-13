#!/usr/bin/env python
from setuptools import setup

setup(
    name='tiget',
    version='0.1',
    author='Martin Natano',
    author_email='natano@natano.net',
    description='ticketing system with git backend',
    long_description='',
    license='ISC',
    keywords='TODO',
    packages=['tiget'],
    scripts=['scripts/tiget'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: ISC License (ISCL)',
    ],
)
