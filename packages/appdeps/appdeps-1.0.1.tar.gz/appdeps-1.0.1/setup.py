#!/usr/bin/env python
from setuptools import setup

setup(
    name='appdeps',
    version='1.0.1',
    url='https://github.com/gwu-libraries/appdeps',
    author='Justin Littman',
    author_email='justinlittman@gmail.com',
    scripts=['appdeps.py', ],
    description="Simple commandline tool to check and/or wait for application dependencies.",
    platforms=['POSIX'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 5 - Production/Stable',
    ],
)
