#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import print_function
from setuptools import setup, find_packages
from funclib.config.config import *
import sys

setup(
    name="funclib",
    version=version,
    author="CN-Tower",
    author_email="247114045@qq.com",
    description="A data processing methods lib of python",
    long_description=open("README.rst").read(),
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url="https://github.com/CN-Tower/FuncLib",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
)
