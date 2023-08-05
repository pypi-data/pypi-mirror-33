#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name='pydomaingibfeature',
    version="0.1.2",
    author="huyifeng",
    author_email="solopointer@qq.com",
    description="Generator gibberish feature for machine learning",
    long_description=open("README.md").read(),
    license="MIT",
    keywords = ("pydomaingibfeature"),
    url="https://github.com/solopointer/pydomaingibfeature",
    packages=['pydomaingibfeature'],
    include_package_data = True,
    install_requires=['pygibberish'],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Indexing",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
)

