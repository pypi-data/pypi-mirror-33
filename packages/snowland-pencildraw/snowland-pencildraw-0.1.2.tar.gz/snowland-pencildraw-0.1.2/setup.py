#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/4 0004 下午 10:37
# @Author  : A.Star
# @Site    :
# @contact : astar@snowland.ltd
# @File    : setup.py
# @Software: PyCharm 

from setuptools import setup, find_packages
from slapy import __version__
setup(
    name='snowland-pencildraw',
    version=__version__,
    description=(
        'pencil draw'
    ),
    long_description=open('README.rst').read(),
    author='A.Star',
    author_email='astar@snowland.ltd',
    maintainer='A.Star',
    maintainer_email='astar@snowland.ltd',
    license='BSD License',
    packages=find_packages(),
    platforms=["all"],
    url='https://gitee.com/hoops/PencilDrawing_python3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
    ],
    install_requires=[
        'scikit-image==0.14.0',
        'numpy>=1.0.0',
        'scipy>=0.14.0',
        'matplotlib>=2.0.0'
    ]
)