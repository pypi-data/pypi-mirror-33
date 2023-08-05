#!/usr/bin/env python3
#-*- coding: utf-8 -*-

'''
@author Linwei.Wang
@email wenix@live.cn
@date 2018/06/19
'''

import os
import os.path as op
import shutil

def create_project(args):
    project_name = args.name
    if project_name:
        cwd = os.getcwd()
        try:
            os.mkdir(op.join(cwd, project_name))
        except OSError as err:
            print('%s directory has existed!' % project_name)
        basedir = op.dirname(op.abspath(__file__)),
        files = os.listdir(op.join(basedir[0], 'template'))
        for f in files:
            dst = f
            if f.endswith('.tpl'):
               dst = f[:-4]
            shutil.copy(op.join(basedir[0], 'template', f),
                        op.join(cwd, project_name, dst))
        print('%s has been created' % project_name)
