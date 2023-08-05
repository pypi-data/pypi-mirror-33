#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : insertsort.py
# @Created : 2018/2/6 
# @Software: PyCharm Community Edition
import random, profile

def insertSort(lists):
    # 插入排序
    count = len(lists)
    for i in range(1, count):
        key = lists[i]
        j = i - 1
        while j >= 0:
            if lists[j] > key:
                lists[j + 1] = lists[j]
                lists[j] = key
            j -= 1
    return lists

if __name__ == '__main__':
    array = [random.randint(1,10000) for i in range(10000)]
    profile.run('insertSort(array)')