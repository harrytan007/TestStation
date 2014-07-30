#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of test_station.

"""G设备脚本模板。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

from test_station.err import EXCEPTION
from test_station.case import Case

class FlowfirmG(Case):
    """G设备测试用例模板，测试用例脚本必须通过重写该模板类实现"""
    def __init__(self):
        Case.__init__(self)

template = \
"#coding=utf-8\n"+\
"from test_station.template.flowfirm_g import FlowfirmG\n"+\
"class TestCase(FlowfirmG):\n"+\
"    def go(self):\n"
