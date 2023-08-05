#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'KennyZ'
# @Site    : http://www.zhouwenkai.com
# @Email   : naizut@163.com
# @File    : radixsort.py
# @Created : 2018/6/8 
# @Software: PyCharm Community Edition

import random
import profile

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

if __name__ == '__main__':
    array = [random.randint(1, 10000) for i in range(10000)]
    profile.run('radixSort(array,3)')