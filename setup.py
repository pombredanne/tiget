#!/usr/bin/env python
from setuptools import setup

version = __import__('tiget').get_version()

setup(
    name='tiget',
    version=version,
    author='Martin Natano',
    author_email='natano@natano.net',
    description='ticketing system with git backend',
    long_description='',
    license='ISC',
    keywords='TODO',
    packages=['tiget', 'tiget.cmds'],
    scripts=['scripts/tiget'],
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'License :: OSI Approved :: ISC License (ISCL)',
    ],
)
