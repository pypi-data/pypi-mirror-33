#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name='pydomaintextfeature',
    version="0.1.0",
    author="huyifeng",
    author_email="solopointer@qq.com",
    description="Generate text feature of domain for machine learn",
    long_description=open("README.md").read(),
    license="MIT",
    keywords = ("pydomaintextfeature"),
    url="https://github.com/solopointer/pydomaintextfeature",
    packages=['pydomaintextfeature'],
    include_package_data = True,
    install_requires=['pyngramgen'],
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

