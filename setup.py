#!/usr/bin/env python
from setuptools import setup, find_packages

version = __import__('tiget').__version__


setup(
    name='tiget',
    version=version,
    author='Martin Natano',
    author_email='natano@natano.net',
    description='ticketing system with git backend',
    url='http://github.com/natano/tiget/',
    long_description='',
    license='ISC',
    keywords=[
        'Interactive', 'Interpreter', 'Shell', 'Git', 'Distributed',
        'Ticketing', 'Tracker',
    ],
    packages=find_packages(exclude=['tests']),
    package_data={
        'tiget': ['config/tigetrc'],
    },
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities',
        'Topic :: System :: Shells',
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'console_scripts': [
            'tiget = tiget.main:main',
            'tiget-setup-repository = tiget.setup_repository:main',
        ],
        'tiget.plugins': [
            'core = tiget.core',
            'importer = tiget.importer',
            'simple-workflow = tiget.simple_workflow',
        ],
    },
    requires=['pygit2', 'ansicolors'],
    test_suite='tests',
)
