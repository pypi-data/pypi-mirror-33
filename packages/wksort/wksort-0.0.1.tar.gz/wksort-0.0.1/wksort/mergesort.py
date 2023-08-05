#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : mergesort.py
# @Created : 2018/6/8 
# @Software: PyCharm Community Edition
import random
import profile

def merge(a, b):
    c = []
    h = j = 0
    while j < len(a) and h < len(b):
        if a[j] < b[h]:
            c.append(a[j])
            j += 1
        else:
            c.append(b[h])
            h += 1
    if j == len(a):
        for i in b[h:]:
            c.append(i)
    else:
        for i in a[j:]:
            c.append(i)
    return c

def mergeSort(lists):
    if len(lists) <= 1:
        return lists
    middle = len(lists)//2
    left = mergeSort(lists[:middle])
    right = mergeSort(lists[middle:])
    return merge(left, right)

if __name__ == '__main__':
    array = [random.randint(1, 10000) for i in range(10000)]
    profile.run('mergeSort(array)')