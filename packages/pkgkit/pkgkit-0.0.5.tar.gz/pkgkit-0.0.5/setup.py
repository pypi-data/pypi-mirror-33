# -*- coding: utf-8 -*-
"""
Created on 2018-07-10 22:04:21
Last Modified on 2018-07-10 22:04:21

Setup file of "pkgkit"

@Author: Ying Huang
"""
from setuptools import setup, find_packages


with open("./Readme.md", "r") as f:
    long_description = f.read()


setup(
    name="pkgkit",
    version="0.0.5",
    author="Ying Huang",
    author_email="hhhyyy1992117@qq.com",
    description="A pakage toolkit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yingHH/easyShell",
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux'
    ],
)
