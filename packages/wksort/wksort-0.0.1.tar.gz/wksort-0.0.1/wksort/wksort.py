#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : wksort.py
# @Created : 2018/6/19 
# @Software: PyCharm Community Edition

def bubbleSort(nums):
    """
    :param nums:list
    :return: list
    """

    for i in range(len(nums)-1):
        for j in range(len(nums)-1-i):
            if nums[j] > nums[j+1]:
                nums[j] ,nums[j+1] = nums[j+1] ,nums[j]
    return nums

def heapSort(lists):
    def adjust_heap(lists, i, size):
        lchild = 2 * i + 1
        rchild = 2 * i + 2
        max = i
        if i < size / 2:
            if lchild < size and lists[lchild] > lists[max]:
                max = lchild
            if rchild < size and lists[rchild] > lists[max]:
                max = rchild
            if max != i:
                lists[max], lists[i] = lists[i], lists[max]
                adjust_heap(lists, max, size)

    def build_heap(lists, size):
        for i in range(0, (size // 2))[::-1]:
            adjust_heap(lists, i, size)

    size = len(lists)
    build_heap(lists, size)
    for i in range(0, size)[::-1]:
        lists[0], lists[i] = lists[i], lists[0]
        adjust_heap(lists, 0, i)

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


def mergeSort(lists):
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

    if len(lists) <= 1:
        return lists
    middle = len(lists) // 2
    left = mergeSort(lists[:middle])
    right = mergeSort(lists[middle:])
    return merge(left, right)

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

def radixSort(list,d):
    for k in range(d):#d轮排序
        s=[[] for i in range(10)]#因为每一位数字都是0~9，故建立10个桶
        '''对于数组中的元素，首先按照最低有效数字进行
           排序，然后由低位向高位进行。'''
        for i in list:
            '''对于3个元素的数组[977, 87, 960]，第一轮排序首先按照个位数字相同的
               放在一个桶s[7]=[977],s[7]=[977,87],s[0]=[960]
               执行后list=[960,977,87].第二轮按照十位数，s[6]=[960],s[7]=[977]
               s[8]=[87],执行后list=[960,977,87].第三轮按照百位，s[9]=[960]
               s[9]=[960,977],s[0]=87,执行后list=[87,960,977],结束。'''
            s[i//(10**k)%10].append(i) #977/10=97(小数舍去),87/100=0
        list=[j for i in s for j in i]
    return list

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

def names():
    dicts = {"冒泡排序":"sort.bubbleSort(list)","堆排序":"sort.heapSort(list)", "插入排序":"sort.insertSort(list)",
             "归并排序":"sort.mergeSort(list)","快速排序":"sort.quickSort(list, low, high)",
             "基数排序":"sort.radixSort(list, looptimes)", "选择排序":"sort.selectionSort(list)"}
    for key,value in dicts.items():
        print('{key}:{value}'.format(key=key, value=value))
