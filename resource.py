#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of resource.

"""资源模型及相关方法。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

import config 

class Resource(config.Parse):
    """资源类"""
    def __init__(self, name, kind):
        self.name = name #资源名称
        self.kind = kind #资源种类
        self.libdir = None #资源路径
        self.children = [] #子资源

    def init(self):
        """资源初始化"""
        pass

    def release(self):
        """资源释放"""
        pass

    def rollback(self):
        """资源已执行的操作回滚"""
        pass

    def addChild(self, child):
        """加入新的子资源"""
        if not isinstance(child, list):
            child = [child]
        self.children += child

    def libSearch(self, node):
        name, lib = node.get("name"), node.get("lib")
        lib = lib.replace("/", ".").strip(".")
        if name != None and lib != None:
            exec("from lib.%s import reg"%lib)
            return reg.regist(node)
