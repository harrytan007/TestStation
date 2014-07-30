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
from test_server.case import Case

class Example(Case):
    """示例测试用例模板，测试用例脚本必须通过重写该模板类实现"""
    def __init__(self):
        Case.__init__(self)

template = 
"#coding=utf-8\n"+
"from test_station.template.example import Example\n"+
"class TestCase(Example):\n"+
"    def go(self):\n"
