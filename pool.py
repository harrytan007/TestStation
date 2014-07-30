#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of resource.

"""资源池功能模块。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

from test_station.logging.logger import log
from test_station.err import EXCEPTION
from resource import Resource
from config import Parse

class Queue:
    """队列实现"""
    def __init__(self):
        self.queue = []

    def push(self, item):
        self.queue.append(item)

    def pop(self):
        return self.queue.pop(0) if self.queue != [] else None

    def isempty(self):
        return self.queue == []


class Pool(Resource):
    """逻辑资源池，资源集合的原始组织形式"""
    def __init__(self, xmlfile):
        Resource.__init__(self, "pool", "pool")
        self.__registChildren(xmlfile)
        self.__createMap(xmlfile)

    def __registChildren(self, xmlfile):
        node = Parse().getElementTreeRoot(xmlfile).find("resources")
        self.addChild(map(self.libSearch, node.getchildren()))
    
    def __createMap(self, xmlfile):
        """根据配置文件中map映射关系，建立各个资源的连接情况"""
        def nameScan(rs, name):
            for r in rs:
                if r.name == name:
                    return r
            return None

        def fullNameScan(rs, fullname):
            for name in fullname.split(":"):
                ret =  nameScan(rs, name)
                if ret == None:
                    break
                else:
                    rs = ret.children
            return ret

        node = Parse().getElementTreeRoot(xmlfile).find("resources_map")
        for con in node.findall("con"):
            r1,r2 = fullNameScan(self.children, con.get("con1")),fullNameScan(self.children, con.get("con2"))
            r1.connect.append(r2)
            r2.connect.append(r1)

    def get(self, dct, num=None):
        """根据字典获取资源"""
        if dct == {}:
            return []
        lst = []
        try:
            iter = self.__search(self.children, dct)
            if not num:
                for rsc in iter:
                    lst.append(rsc)
            elif num == 0:
                return iter.next()
            else:
                while num != 0:
                    lst.append(iter.next())
                    num -= 1
        except StopIteration:
            log(2, "Resources(%s) aren't enough"%dct)
            raise EXCEPTION(1, "Resources(%s) aren't enough"%dct)
        return lst

    def __search(self, rscs, dct):
        """BFS方式搜索资源池，查找匹配dct的资源，找到一个立即返回"""
        queue = Queue()
        for rsc in rscs:
            queue.push(rsc)
        while not queue.isempty():
            rsc = queue.pop()
            if self.__match(rsc, dct):
                yield rsc
            for child_rsc in rsc.children:
                queue.push(child_rsc)

    def __match(self, r, dct):
        """模糊匹配"""
        match = True
        for (key, value) in dct.items():
            if key == "connect":
                if isinstance(value, dict):
                    lst = []
                    for cnt in self.__search(r.connect, value):
                        lst.append(cnt)
                    if lst == []:
                        match = False 
                elif value == "null":
                    if r.connect != []:
                        match = False
                else:
                    match = False
            else:
                if (key, value) not in r.__dict__.items():
                    match = False
                    break
        return match

