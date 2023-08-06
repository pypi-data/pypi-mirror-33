#!/usr/bin/env python
# coding: utf8

from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

setup(
    name='move-carrots',
    license='MIT',
    version='0.0.1a',
    packages=find_packages(exclude=['tests*']),
    description='Simple helper for reproducible (research) experiments.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['pyyaml'],
    url='https://gitlab.com/Pinle/move-carrots',
    author='Pinle',
    author_email='',
    py_modules=['mcar'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
