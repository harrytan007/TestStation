#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of test_station.

"""脚本工具包
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]
import random
import time

from test_station.logging.logger import log
from test_station.err import EXCEPTION
from test_station.resource import Resource
import tcmp


class Utils(Resource):
    """工具类
    """
    def __init__(self, node):
        Resource.__init__(self, "utils", "utils")

    def sleep(self, s):
        """功能：延时
           输入：s（延时多少，单位秒）
        """
        log(0, 'Sleep %d seconds' % s)
        time.sleep(s)
    
    def sumEqual(self, counts1, counts2):
        """判断两个计数元组的计数和是否相等：相等返回True，不相等返回False"""
        if isinstance(counts1, int):
            counts1 = [counts1]
        if isinstance(counts2, int):
            counts2 = [counts2]
        # 求和
        sum1 = 0
        for count in counts1:
            sum1 = sum1 + count
        sum2 = 0
        for count in counts2:
            sum2 = sum2 + count
        # 判断
        if sum1 == sum2:
            return True
        else:
            return False
    
    def countLost(self, count_list):
        """判断端口组中是否有计数为0：有缺失返回True， 无缺失返回False"""
        l = False
        for count in count_list:
            if count == 0:
                l = True
        return l
    
    def binarization(self, count_list):
        """将列表中的计数进行二值化，例[100,155,0,6] -> [1,1,0,1]"""
        lst = []
        for item in count_list:
            if item == 0:
                lst.append(0)
            else:
                lst.append(1) 
        return lst
    
    def countContrast(self, count_list, contrast_list):
        """比对计数是否符合预期，符合返回True，不符合返回False"""
        if isinstance(count_list, int):
            count_list = [count_list]
        if isinstance(contrast_list, int):
            contrast_list = [contrast_list]
        if len(count_list) != len(contrast_list):
            log(1, 'Unmatched length')
            raise EXCEPTION(1, "Count_contrast: unmatched length")
        match = True
        for i in range(0, len(count_list)):
            if count_list[i] != contrast_list[i]:
                match = False
        return match
    
    def countChange(self, count_list1, count_list2):
        """比对计数是否全部都发生变化，变化返回True，部分变化或没有变化返回False"""
        if isinstance(count_list1, int):
            count_list1 = [count_list1]
        if isinstance(count_list2, int):
            count_list2 = [count_list2]
        if len(count_list1) != len(count_list2):
            log(1, 'Unmatched length')
            raise EXCEPTION(1, "Count_change: unmatched length")
        for i in range(0, len(count_list1)):
            if count_list1[i] == count_list2[i]:
                return False
        return True
    
    def listXnum(self, lst, num):
        """列表乘法"""
        for i in range(0, len(lst)):
            lst[i] = lst[i] * num
    
    def listPlus(self, list1, list2):
        """列表加法"""
        if len(list1) == len(list2):
            return [x+y for x, y in zip(list1, list2)]
        else:
            return False
    
    def extractFrame(self, source, byte_start, len):
        """提取报文"""
        lst = []
        for i in range(0, len):
            hex = source[(byte_start+i)*3+1:(byte_start+i)*3+3]
            val = eval('0x' + hex)
            lst.append(val)
        return lst
    
    def ethFrameValidLen(self, source):
        """获得ETH报文剥离MAC和校验和后的数据长度"""
        src_len = len(source)
        return (src_len - 2 + 1 - 14*3 - 4*3) / 3
    
    def deviationRate(self, lst):
        """偏差率：标准差/均值*100%，保留两位小数"""
        l = len(lst)*1.0
        if l == 0:
            raise EXCEPTION(1, "DeviationRate: len of para is 0")
        u = sum(lst)/l
        if u == 0:
            raise EXCEPTION(1, "DeviationRate: average of sum is 0")
        d = 0.0
        for mem in lst:
            d += (mem - u)**2
            stddev = (d/l)**0.5
        return round(stddev/u, 4)
    
    def allActive(self, lst):
        """判断HOST状态是否都为active"""
        for item in lst:
            if item == 'inactive':
                return False
    def listLength(self,ls):
        """返回列表长度"""
        return len(ls)

    def randomChoice(self,param):
        """随机返回param中的一个元素，其中param是一个有序类型，可以是一个列表，也可以是字符串"""
        return random.choice(param)

    def listAppend(self,lst,element):
        """列表追加元素"""
        lst.append(element)

    def listSum(self,lst):
        """列表元素求和"""
        return sum(lst)

    def listRemove(self,ls,ele):
        """删除列表中第一次出现的元素"""
        ls.remove(ele)
        return ls

    def listDelete(self,ls,index):
        """删除列表中index位置的元素"""
        del ls[index]
        return ls

    def listCount(self, lst, element):
        """查询列表中有多少指定元素"""
        return lst.count(element)

