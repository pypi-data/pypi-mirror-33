# -*- coding: utf-8 -*-
# @Author  : 河北雪域网络科技有限公司 A.Star
# @contact: astar@snowland.ltd
# @site: 
# @file: __init__.py
# @time: 2018-07-12
# @Software: PyCharm

import pickle as pk
from skimage.io import imread
try:
    with open('pencils/pencil0.pkl', 'rb') as fin:
        pencil0 = pk.load(fin)
except:
    with open('pencils/pencil0.pkl', 'wb') as fin:
        pencil0 = imread('pencils/pencil0.jpg', as_gray=True)
        pk.dump(pencil0, fin)

try:
    with open('pencils/pencil1.pkl', 'rb') as fin:
        pencil1 = pk.load(fin)
except:
    with open('pencils/pencil1.pkl', 'wb') as fin:
        pencil1 = imread('pencils/pencil1.jpg', as_gray=True)
        pk.dump(pencil1, fin)

try:
    with open('pencils/pencil2.pkl', 'rb') as fin:
        pencil2 = pk.load(fin)
except:
    with open('pencils/pencil2.pkl', 'wb') as fin:
        pencil2 = imread('pencils/pencil2.png', as_gray=True)
        pk.dump(pencil2, fin)

try:
    with open('pencils/pencil3.pkl', 'rb') as fin:
        pencil3 = pk.load(fin)
except:
    with open('pencils/pencil3.pkl', 'wb') as fin:
        pencil3 = imread('pencils/pencil3.jpg', as_gray=True)
        pk.dump(pencil3, fin)

try:
    with open('pencils/pencil4.pkl', 'rb') as fin:
        pencil4 = pk.load(fin)
except:
    with open('pencils/pencil4.pkl', 'wb') as fin:
        pencil4 = imread('pencils/pencil4.jpg', as_gray=True)
        pk.dump(pencil4, fin)
