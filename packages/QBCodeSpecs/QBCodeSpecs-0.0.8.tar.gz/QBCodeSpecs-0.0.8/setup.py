#!/usr/bin/env python
#-*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: paulineli
# Mail: 109926082@qq.com
# Created Time:  2018-06-14 18:14:34 AM
#############################################


from setuptools import setup, find_packages

setup(
    name = "QBCodeSpecs",
    version = "0.0.8",
    keywords = ["pip", "code", "specs"],
    description = "QBCodeSpecs",
    long_description = "QBCodeSpecs sdk for python",
    license = "MIT Licence",

    url = "https://browser.qq.com/ipad/pc.html",
    author = "paulineli",
    author_email = "109926082@qq.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = ["click"],
    entry_points = {
        'console_scripts': [
            'QBCodeSpecs = QBCodeSpecs.driver.ObjCCheckMain:enter'
        ]
    }
)
