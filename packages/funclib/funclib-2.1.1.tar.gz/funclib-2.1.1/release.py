#!/usr/bin/env python
# -*- coding:utf-8 -*-
from src.funclib import FuncLib as fn
import os
import platform
import time

def del_temp_files():
    print('\nDeleting temp files !!! ...\n')
    tmp_files = ['build', 'dist', 'funclib.egg-info']
    if platform.system() == "Windows":
        for f in tmp_files:
            if os.path.exists(f):
                if os.path.isfile(f):
                    os.system('del ' + f)
                else:
                    os.system('rd /s /q ' + f)
    else:
        for f in tmp_files:
            os.system('rm -rf ' + f)
    time.sleep(1)
    print('\nDelete temp files Success!')

def md_2_rst():
    print('\nRename README.md to README.rst !!! ...\n')
    if platform.system() == "Windows" and os.path.exists('README.md'):
        os.system('ren README.md README.rst')
    else:
        os.system('mv README.md README.rst')
    time.sleep(1)
    print('\nRename README.md to README.rst Success!')

def build_dist(): 
    print('\nBuilding Dist !!! ...\n')
    os.system('python setup.py sdist build')
    time.sleep(1)
    print('\nBuild Dist Success!')

def release_funclib():
    print('\nRelease !!! ...\n')
    status_code = os.system('twine upload dist/*')
    if status_code != 0:
        raise Exception('Release Error, Please make sure you have installed the "twine" module already!')
    time.sleep(1)
    print('\nRelease Success!')

def rst_2_md():
    print('\nRename README.rst to README.md !!! ...\n')
    if platform.system() == "Windows":
        os.system('ren README.rst README.md')
    else:
        os.system('mv README.rst README.md')
    time.sleep(1)
    print('\nRename README.rst to README.md Success!\n')

if __name__ == '__main__':
    fn.clear()
    fn.log('Release Starting !!! ...')
    del_temp_files()
    md_2_rst()
    build_dist()
    release_funclib()
    rst_2_md()
    fn.log('Congratulations, Release totaly Success!')
