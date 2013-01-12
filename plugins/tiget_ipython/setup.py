#!/usr/bin/env python3
from setuptools import setup


setup(
    name='tiget-ipython',
    version='0.1a0',
    author='Martin Natano',
    author_email='natano@natano.net',
    description='ipython plugin for tiget',
    url='http://github.com/natano/tiget/',
    long_description='',
    license='ISC',
    keywords=['Interactive', 'Interpreter', 'Shell'],
    py_modules=['tiget_ipython'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
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
    install_requires=['distribute'],
)
