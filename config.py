#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of config.

"""解析XML配置文件模块。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

from xml.etree import ElementTree
import gl

class Parse():
    """XML解析模块"""
    def __init__(self):
        pass

    def getElementTreeRoot(self, xmlfile):
        tree = ElementTree.parse(xmlfile)
        return tree.getroot()

    def getResources(self, node):
        return [x for x in node.getchildren() if x.get("name") != None and x.get("lib")]

    def str2list(self, str):
        return str.replace(' ','').replace('\n', '').strip(',').split(',')


class ConfTest(Parse):
    """测试任务配置类"""
    def __init__(self, xmlfile):
        self.rollback = True
        self.execute = []
        self.script_library = []
        self.__parse(xmlfile)

    def __parse(self, xmlfile):
        """解析测试配置文件"""
        def common(self, node):
            self.test_suite_path = node.findtext("test_suite_path", "../test_suite") #测试用例集目录
            self.log_name = node.findtext("log_name", "unknown_test") #日志名称
            self.report_name = node.findtext("report_name", "unknown_test") #报告名称
            self.test_user = node.findtext("test_user", "unknown") #测试用户
            gl.test_user = self.test_user
            self.local_ip = node.findtext("local_ip") #本地测试客户端IP
            self.mail_server = None #邮件服务器IP
            self.sender = None #发件人用户名
            self.sender_passwd = None #发件人密码
            self.addressee_list = None #收件人列表
        def cases(self, node):
            def newCase(node):
                case = Case()
                case.name = node.get("name")
                case.py = node.findtext("py")
                case.xml = node.findtext("xml")
                case.txt = node.findtext("txt")
                return case
            def findCase(cases, name):
                for case in cases:
                    if case.name == name: return case
                return None
            sl = node.find("script_library")
            self.script_library = map(newCase, sl.findall("case")) #脚本库
            exe = node.find("execute")
            self.rollback = True if exe.get("rollback")=="true" else False #回滚标志
            self.order = exe.get("order") #脚本执行顺序
            self.template = node.findtext("template") #使用的脚本模板
            for name in Parse().str2list(exe.text):
                self.execute.append(findCase(self.script_library, name)) #待执行的脚本

        test = Parse().getElementTreeRoot(xmlfile).find("test")
        common(self, test)
        cases(self, test)


class Case():
    """单个测试用例属性配置"""
    def __init__(self):
        self.name = None #用例名称
        self.dir = None #用例所在目录路径
        self.py = None #Python文件
        self.txt = None #关键字脚本文件
        self.xml = None #数据文件
        self.restore = False #是否用例开始前恢复出厂设置
    def __eq__(self, name):
        return self.name == name

