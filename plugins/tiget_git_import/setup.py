#!/usr/bin/env python
from setuptools import setup

version = __import__('tiget_git_import').__version__


setup(
    name='tiget-git-import',
    version=version,
    author='Martin Natano',
    author_email='natano@natano.net',
    description='import hooks for tiget to load modules from git',
    url='http://github.com/natano/tiget/',
    long_description='',
    license='ISC',
    keywords=['Import', 'Hooks', 'PEP302'],
    packages=['tiget_git_import'],
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
            'git-import = tiget_git_import',
        ],
    },
    requires=['tiget'],
)
