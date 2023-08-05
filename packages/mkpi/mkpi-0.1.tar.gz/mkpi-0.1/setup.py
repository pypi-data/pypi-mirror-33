#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import setuptools

with open('README.md', 'r', encoding='UTF-8') as df:
    long_description = df.read()

setuptools.setup(
    name = "mkpi",
    version = "0.1",
    author = "Linwei Wang",
    author_email = "wenix@live.cn",
    description = "make python project setuptools template",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/wanix1988/python-setup-boilerplate",
    packages = setuptools.find_packages(),
    install_requires = [],
    entry_points = {
        'console_scripts': [
            'mkpi=mkpi:main'
        ]
    },
    classifiers = (
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
