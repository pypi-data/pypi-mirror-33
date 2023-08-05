#!/usr/bin/env python
from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name='pygibberish',
    version="0.0.9",
    author="huyifeng",
    author_email="solopointer@qq.com",
    description="Gibberish train/test",
    long_description=open("README.md").read(),
    license="MIT",
    keywords = ("gibberish"),
    url="https://github.com/solopointer/pygibberish",
    packages=['pygibberish'],
    #package_data = {'train_data': ['pygibberish/en_big.txt']},
    #data_files = [('train_data', ['pygibberish/train_data/en_big.txt'])],
    include_package_data = True,
    install_requires=[],
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

