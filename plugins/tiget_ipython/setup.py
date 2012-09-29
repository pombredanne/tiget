#!/usr/bin/env python
from setuptools import setup

version = __import__('tiget_ipython').__version__


setup(
    name='tiget-ipython',
    version=version,
    author='Martin Natano',
    author_email='natano@natano.net',
    description='ipython plugin for tiget',
    url='http://github.com/natano/tiget/',
    long_description='',
    license='ISC',
    keywords=['Interactive', 'Interpreter', 'Shell'],
    packages=['tiget_ipython'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Utilities',
        'Topic :: System :: Shells',
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'tiget.plugins': [
            'ipython = tiget_ipython',
        ],
    },
    requires=['tiget', 'ipython'],
)
