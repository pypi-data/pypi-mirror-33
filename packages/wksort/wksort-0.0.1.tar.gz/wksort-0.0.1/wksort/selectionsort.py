#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : selectionsort.py
# @Created : 2018/2/3 
# @Software: PyCharm Community Edition
import random
import profile

def selectionSort(nums):
    """
    :param nums: list
    :return: list
    """
    for i in range(len(nums)-1):
        minindex = i
        for j in range(i,len(nums)):
            if nums[j]<nums[minindex]:
                minindex = j
        nums[minindex],nums[i]=nums[i],nums[minindex]
    return nums

if __name__ == '__main__':
    array = [random.randint(1,10000) for i in range(10000)]
    profile.run('selectionSort(array)')