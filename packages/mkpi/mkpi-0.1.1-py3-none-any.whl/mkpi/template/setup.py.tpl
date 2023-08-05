#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import setuptools

with open('README.md', 'r', encoding='UTF-8') as df:
    long_description = df.read()
    
setuptools.setup(
    name = "{project}",
    version = "{version}",
    author = "{author}",
    author_email = "{email}",
    description = "{description}",
    long_description = "{long_description}",
    long_description_content_type = "{content_type}",
    url = "{url}",
    packages = setuptools.find_packages(),
    install_requires = ["{requires}"],
    entry_points = {},
    classifiers = (
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT Licens",
        "Operating System :: OS Independent",
    )
)