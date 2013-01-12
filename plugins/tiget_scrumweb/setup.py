#!/usr/bin/env python3
from setuptools import setup


setup(
    name='tiget-scrumweb',
    version='0.1a0',
    author='Martin Natano',
    author_email='natano@natano.net',
    description='web frontend for tiget',
    url='http://github.com/natano/tiget/',
    long_description='',
    license='ISC',
    keywords=['Web'],
    packages=['tiget_scrumweb'],
    package_data={
        'tiget_scrumweb': ['templates/*.tpl']
    },
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.2',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application'
        'Development Status :: 3 - Alpha',
    ],
    entry_points={
        'tiget.plugins': [
            'scrumweb = tiget_scrumweb',
        ],
    },
    requires=['tiget', 'bottle', 'cryptacular', 'beaker'],
    install_requires=['distribute'],
)
