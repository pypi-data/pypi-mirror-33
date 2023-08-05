#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : setup.py
# @Created : 2018/6/19 
# @Software: PyCharm Community Edition

from setuptools import setup, find_packages

setup(
    name='wksort',
    version='0.0.1',
    author="Wenkai Zhou",
    author_email="naizut@163.com",
    description=("This is a lib of realizing sort methods"),
    license="MIT",
    keywords='',
    packages = find_packages(),
    url="https://github.com/naizut/wksort",

    install_requires = [],
    zip_safe=False,
    # classifiers = [
    #     'Development Status :: Original - Version,'
    #     'License :: OSI Approved :: MIT License',
    #     'Programming Language :: Python :: 3.6',
    # ],
)