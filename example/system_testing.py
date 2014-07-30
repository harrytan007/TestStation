#!/usr/bin/python
#coding=utf-8

import sys

config = sys.argv[1]
resource = sys.argv[2]

def getTestStationPath(file):
    from xml.etree import ElementTree
    cf = ElementTree.parse(config).getroot().find("test")
    return cf.findtext("test_station_path")

sys.path.append(getTestStationPath(config)) #加载测试平台路径

from test_station import run
from test_station import gl

try:
    gl.test_conf = config
    gl.resources_conf = resource

    test = run.Test() #创建测试项目实例
    test.doIt() #测试开始

finally:
    pass
    test.doReport() #生成测试报告
