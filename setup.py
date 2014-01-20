#!/usr/bin/env python3
from setuptools import setup, find_packages

# work around error in atexit when running ./setup.py test
# see http://www.eby-sarna.com/pipermail/peak/2010-May/003357.html
import multiprocessing


setup(
    name='tiget',
    version=__import__('tiget').__version__,
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
    packages=find_packages(),
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Topic :: Utilities',
        'Topic :: System :: Shells',
        'Topic :: Software Development :: Bug Tracking',
        'Topic :: Software Development :: Quality Assurance',
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'console_scripts': [
            'tiget = tiget.main:main',
            'tiget-setup = tiget.setup:main',
        ],
        'nose.plugins.0.10': [
            'tiget_nose_config = tiget.nose_config:NoseConfig',
        ],
        'tiget.plugins': [
            'core = tiget.core',
            'importer = tiget.importer',
            'scrum = tiget.scrum',
        ],
    },
    install_requires=['git-orm', 'ansicolors'],
    tests_require=['nose', 'mock'],
    test_suite='nose.collector',
)
