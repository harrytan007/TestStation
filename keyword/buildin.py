#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of keyword.

"""内建脚本处理函数。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

import dataxml 

def set(obj, val):
    """SET关键字的实现:赋值
    """
    return "%s = %s"%(obj,val)

def get(obj, attr):
    """GET关键字的实现:获取属性
    """
    return "%s.%s"%(obj,attr)

def add(a, b):
    """ADD关键字的实现:加
    """
    return "%s + %s"%(a,b)

def sub(a, b):
    """SUB关键字的实现:减
    """
    return "%s - %s"%(a,b)

def mul(a, b):
    """MUL关键字的实现:乘
    """
    return "%s * %s"%(a,b)

def div(a, b):
    """DIV关键字的实现:除
    """
    return "%s / %s"%(a,b)

def gt(a, b):
    """GT关键字的实现:大于
    """
    return "%s > %s"%(a,b)

def lt(a, b):
    """LT关键字的实现:小于
    """
    return "%s < %s"%(a,b)

def eq(a, b):
    """EQ关键字的实现:等于
    """
    return "%s == %s"%(a,b)

def neq(a, b):
    """NEQ关键字的实现:不等于
    """
    return "%s != %s"%(a,b)

def resource(name, xml):
    """RESOURCE关键字的实现:载入资源
    """
    dx = dataxml.DataXml(xml)
    lst = dx.getResource(name)
    dct = lst[0]
    num = lst[1]
    if num == "ALL": num = "None"
    return "%s = self.getResource(%s, %s)"%(name,str(dct),num)

def data(name, xml):
    """DATA关键字的实现:载入数据
    """
    dx = dataxml.DataXml(xml)
    data = dx.getData(name)
    return "%s = %s"%(name,str(data))

def report(state, str):
    """REPORT关键字的实现:插入报告
    """
    return "self.report.insertNew(%s,%s)"%(state,str)

def expect(title, expect, actual):
    """EXPECT关键字的实现:期望比较
    """
    return "self.report.expectNew(%s,%s,%s)"%(title,expect,actual)

def fatalExpect(title, expect, actual):
    """FATALEXPECT关键字的实现:期望比较
    """
    return "self.report.fatalExpect(%s,%s,%s)"%(title,expect,actual)
