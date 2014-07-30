#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of reporting.
import html_utils
import email_utils
import txt_utils
import xml_utils
#import report_utils
from test_station.logging.logger import log
from test_station.err import EXCEPTION


class _Report():
    """单个用例测试报告内容"""
    def __init__(self):
        self.name = None #用例名称
        self.descr = ' ' #用例描述
        self.begin_time = None
        self.end_time = None
        self.result = 0  #测试结果：0:pass, 1:failed, 2:failed and exit from this case, 3:failed and exit from this test
        self.detail = [] #详细测试结果


class Report(_Report):
    """报告处理类"""
    def __init__(self):
        _Report.__init__(self)

    #def add(self, str):
    def insert(self, state=None, str=None):
        """报告中加入自定义内容,
           state是报告状态设置，包括：'info', 'error', 'fatal'，可缺省；
           str是自定义的字符串。
        """
        if str is None and state is not None:
            str = state
            state = None
        elif str is None and state is None:
            log(2, "Report insert: para number error")
            raise EXCEPTION(1, "Report insert: para number error")

        if state is None or state is 'info':
            self.detail.append(str)
        elif state is 'error':
            self.result = 1
            self.detail.append('<ERROR> '+str)
        elif state is 'fatal':
            self.result = 2
            self.detail.append('<FATAL> '+str)
            raise EXCEPTION(1, "")
        else:
            log(2, "Report insert: the 1st para error")
            raise EXCEPTION(1, "Report insert: the 1st para error")

    def insertNew(self, state=None, str=None):
        """报告中加入自定义内容,
           state是报告状态设置，包括：'info', 'error', 'fatal'，可缺省；
           str是自定义的字符串。
        """
        if str is None and state is not None:
            str = state
            state = None
        elif str is None and state is None:
            log(2, "Report insert: para number error")
            raise EXCEPTION(1, "Report insert: para number error")

        if state is None or state == 'info':
            self.detail.append(str)
        elif state is 'error':
            self.result = 1
            self.detail.append('<ERROR> '+str)
        elif state is 'fatal':
            self.result = 2
            self.detail.append('<FATAL> '+str)
            raise EXCEPTION(1, "")
        else:
            log(2, "Report insert: the 1st para error")
            raise EXCEPTION(1, "Report insert: the 1st para error")

    def expect(self, state, title=None, expect_str=None, fact_str=None):
        """报告中加入期望值对比的内容；
           state是报告状态设置，包括：'info', 'error', 'fatal',不可缺省；
           title就这次对比的标题，可缺省；
           expect_str是期望的结果，不可缺省；
           fact_str是实际的结果，不可缺省。
        """
        if fact_str is None and expect_str is not None:
            fact_str = expect_str
            expect_str = title
            title = None
        elif fact_str is None and expect_str is None:
            log(2, "Report expect: para number error")
            raise EXCEPTION(1, "Report expect: para number error")

        if title is not None:
            self.detail.append('-'+title)

        if state is None or state is 'info':
            self.detail.append('EXPECT: '+expect_str+' | FACT: '+fact_str)
        elif state is 'error':
            self.result = 1
            self.detail.append('<ERROR> EXPECT: '+expect_str+' | FACT: '+fact_str)
        elif state is 'fatal':
            self.result = 2
            self.detail.append('<FATAL> EXPECT: '+expect_str+' | FACT: '+fact_str)
            raise EXCEPTION(1, "")
        else:
            log(2, "Report expect: the 1st para error")
            raise EXCEPTION(1, "Report expect: the 1st para error")

    def expectNew(self, title, expect, fact): 
        """报告中加入期望值对比的内容；
           title就这次对比的标题，可缺省；
           expect是期望的结果，不可缺省；
           fact是实际的结果，不可缺省。
        """
        if expect == fact:
            self.detail.append("%s EXPECT: %s | FACT: %s"%(title,expect,fact))
        else:
            self.result = 1
            self.detail.append("<ERROR> %s EXPECT: %s | FACT: %s"%(title,expect,fact))

    def fatalExpect(self, title, expect, fact): 
        """报告中加入期望值对比的内容；
           title就这次对比的标题，可缺省；
           expect是期望的结果，不可缺省；
           fact是实际的结果，不可缺省。
        """
        if expect == fact:
            self.detail.append("%s EXPECT: %s | FACT: %s"%(title,expect,fact))
        else:
            self.result = 2
            self.detail.append("<FATAL> %s EXPECT: %s | FACT: %s"%(title,expect,fact))
            raise EXCEPTION(1, "")
        

def do_report(conf, lst):
    """生成测试报告"""
    mail_server = conf.mail_server
    sender = conf.sender
    addressee_list = conf.addressee_list
    # 生成txt，包括概览信息及详细信息
    txt = txt_utils.ConvertCaseListToTxt(conf)
    txt.overview(lst)
    txt.convert_to_txt (lst)
    # 生成html并发送邮件
    if (mail_server != None and sender != None and addressee_list != None) == True:
        html = ConvertCaseListToHtml (conf)
        html.convert_to_html(lst)
	#email = email_utils.Sender(conf)
        #email.send()

def test():
    class TestConf ():
        def __init__(self,file_name):
            self.report_name = file_name
            self.mail_server = "mail.sugon.com"
            self.sender = "gaoxun@sugon.com"
            self.sender_password = "1q2w3e4r"
            self.address_list = ["gaoxun@sugon.com"]

    class TestReport ():
        def __init__(self,na,de,bt,et,re,det):
            self.name = na
            self.descr = de
            self.begin_time = bt
            self.end_time = et
            self.result = re
            self.detail = det

    conf = TestConf ('gx_test')
    txt = txt_utils.ConvertCaseListToTxt(conf)
    report_1 = TestReport ('case1','a passed test',1,2,0,['a','b'])
    report_2 = TestReport ('case2','a failed test',2,4,1,['c','d'])
    report_3 = TestReport ('case3','exit from case',5,8,0,['e','f'])
    report_4 = TestReport ('case4','exit from test',9,13,0,['g','h'])
    report_list = [report_1,report_2,report_3,report_4]
    txt.overview(report_list)
    txt.convert_to_txt(report_list)

    html = html_utils.ConvertCaseListToHtml(conf)
    html.convert_to_html(report_list)
    # email = email_utils.Sender(conf)
    # email.send()

if __name__ == '__main__':
    test()
    print 'hello' 
