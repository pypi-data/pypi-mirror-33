#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : quicksort.py
# @Created : 2018/2/4 
# @Software: PyCharm Community Edition
import random, profile
def quickSort(L, low, high):
    i = low
    j = high
    if i >= j :
        return L
    key = L[i]
    while i<j:
        while i < j and L[j] >= key:
            j -= 1
        L[i]=L[j]
        while i < j and L[i] <= key:
            i+=1
        L[j]=L[i]
    L[i] = key
    quickSort(L, low, i-1)
    quickSort(L, j+1, high)
    return L

if __name__ == '__main__':
    array = [random.randint(1,10000) for i in range(10000)]
    profile.run('quickSort(array, 0, len(array)-1)')