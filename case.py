#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of test_station.

"""脚本模板。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

from err import EXCEPTION

class Case():
    """测试用例脚本的模板超类"""
    def __init__(self):
        self.level = None #本测试用例级别
        self.name = None #用例名称
        self.pool = None #资源池
        self.conf = None #测试配置
        self.reglist = [] #已获取的资源列表
        self.report = None #本测试用例报告

    def attr(self):
        """配置用例属性"""
        log(2, "Null attr() of Case")
        raise EXCEPTION(2, "Null attr() of Case")

    def init(self):
        """用例初始化准备，包括配置软环境等"""
        pass

    def go(self):
        """用例执行主体"""
        log(2, "Null go() of Case")
        raise EXCEPTION(2, "Null go() of Case")

    def getResource(self, dct, num=None):
        """用例执行时动态获取所需资源，并对其注册和初始化"""
        resource = self.pool.get(dct, num)
        if not isinstance(resource, list):
            rsc = [resource]
        else:
            rsc = resource
        self.reglist += rsc
        map(lambda r:r.init(), rsc) #对获取的资源进行初始化
        return resource
