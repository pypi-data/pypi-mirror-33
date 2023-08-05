#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name='pydnsfeature',
    version="0.1.0",
    author="huyifeng",
    author_email="solopointer@qq.com",
    description="Get the dns feature for machine learning",
    long_description=open("README.md").read(),
    license="MIT",
    keywords = ["dns", "feature", "machine learning"],
    url="https://github.com/solopointer/pydnsfeature",
    packages=['pydnsfeature'],
    include_package_data = True,
    install_requires=['pytld', 'dnspython'],
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

