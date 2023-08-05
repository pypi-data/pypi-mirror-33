#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import argparse
from mkpi.mkpi import create_project

def main():
    parser = argparse.ArgumentParser(description='Make Python Project Setuptools Template.')
    parser.add_argument('--name', required=True, help='specify project\'s name')
    args = parser.parse_args()
    create_project(args)
