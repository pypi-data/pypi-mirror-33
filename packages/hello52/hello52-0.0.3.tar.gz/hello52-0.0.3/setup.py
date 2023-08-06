#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = "zhangyouliang"

PROJ_NAME = 'hello52'
PACKAGE_NAME = 'hello52'

PROJ_METADATA = '%s.json' % PROJ_NAME

import os,json,imp
here = os.path.abspath(os.path.dirname(__file__))

proj_info = json.loads(open(os.path.join(here,PROJ_METADATA),encoding='utf-8').read())

try:
    README = open(os.path.join(here, 'README.rst'), encoding='utf-8').read()
except:
    README = ""

VERSION = imp.load_source('version',os.path.join(here,'src/%s/version.py' % PACKAGE_NAME)).__version__

from setuptools import setup,find_packages

setup(
    # name
    name = proj_info['name'],
    # version
    version = VERSION,

    author = proj_info['author'],
    author_email = proj_info['author_email'],
    url = proj_info['url'],
    license = proj_info['license'],

    long_description = README,

    description = proj_info['description'],
    keywords = proj_info['keywords'],

    # packages
    packages = find_packages('src'),
    package_dir = {'' : 'src'},

    test_suite = 'tests',

    platforms = 'any',
    zip_safe = True,
    #  启用清单文件 MANIFEST.in
    include_package_data = True,
    # 排除某些文件
    # exclude_package_date={'hello52':['.gitignore']},

    classifiers = proj_info['classifiers'],

    entry_points = {'console_scripts': proj_info['console_scripts']},


)


