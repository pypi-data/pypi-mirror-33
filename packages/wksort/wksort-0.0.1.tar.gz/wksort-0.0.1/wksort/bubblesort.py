#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : bubblesort.py
# @Created : 2018/2/3 
# @Software: PyCharm Community Edition
import random
import profile

def bubbleSort(nums):
    """
    :param nums:list
    :return: list
    """
    print("start!")
    for i in range(len(nums)-1):
        for j in range(len(nums)-1-i):
            if nums[j] > nums[j+1]:
                nums[j] ,nums[j+1] = nums[j+1] ,nums[j]
    return nums

if __name__ == '__main__':
    array = [random.randint(1,10000) for i in range(10000)]
    profile.run('bubbleSort(array)')
    profile.run('heapSort(array)')