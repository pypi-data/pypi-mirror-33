#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
@author Linwei.Wang
@email wenix@live.cn
@date 2018/06/19
'''

import os
import shutil
import argparse

def create_project(args):
    project_name = args.name
    if project_name:
        try:
            os.mkdir(project_name)
        except OSError as err:
            print('%s directory has existed!' % project_name)
        files = os.listdir('template')
        for f in files:
            dst = f
            if f.endswith('.tpl'):
               dst = f[:-4]
            shutil.copy(os.path.join('template', f),
                        os.path.join(project_name, dst))
        print('%s has been created' % project_name)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Make Python Project Setuptools Template.')
    parser.add_argument('--name', required=True, help='specify project\'s name')
    args = parser.parse_args()
    create_project(args)
