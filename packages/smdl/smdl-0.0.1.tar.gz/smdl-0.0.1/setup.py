"""
File Name   : setup.py
Created on  : 2018/06/22
Author      : spxcds
"""
#-*- coding: utf-8 -*-

import setuptools
with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='smdl',
    version='0.0.1',
    description='A ML & DL lib',
    url='http://githbu.com/spxcds/sdml',
    author='spxcds',
    author_email='spxcds@gmail.com',
    license='MIT',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    zip_safe=False)
