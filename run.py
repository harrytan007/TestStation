#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of test_station.

"""测试平台的执行模块，包含执行所需要的各种组件。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

import string
import os
import sys
import copy
import time
import traceback

import config
import pool
from test_station.reporting import report
from test_station.logging.logger import log
from test_station.logging.logger import log_init
from err import EXCEPTION
from keyword import keyword
import gl

class Test():
    """测试驱动类"""

    def __init__(self):
        self.conf = None #测试配置
        self.pool = None #资源池
        self.report_lst = []
        #初始化流程
        init_time = time.strftime('%m%d%H%M%S',time.localtime(time.time()))

        def confParse(init_time):
            """解析配置文件，将结果加载"""
            self.conf = config.ConfTest(gl.test_conf)
            self.conf.report_name = self.conf.report_name+'_'+init_time

        def initPool():
            self.pool = pool.Pool(gl.resources_conf)

        def initLog(init_time):
            """初始化日志，日志名称补上初始化时间"""
            log_init(self.conf.log_name+'_'+init_time)

        confParse(init_time)
        initLog(init_time)
        initPool()
        self.__importTemplate()

    def __importTemplate(self):
        exec("from test_station.template import %s"%self.conf.template)
        exec("self.template = %s.template"%self.conf.template)
       

    def __importCase(self, case):

        #如果case中存在py文件，优先执行py文件
        if case.py != None:
            py = self.conf.test_suite_path.rstrip('/') + '/' + case.py
            dir = py.rpartition("/")[0]
        else:
            txt = self.conf.test_suite_path.rstrip('/') + '/' + case.txt
            xml = self.conf.test_suite_path.rstrip('/') + '/' + case.xml
            dir = txt.rpartition("/")[0]
            py = "%s/%s_%s.py"%(dir,txt.rpartition("/")[-1].split(".")[0], xml.rpartition("/")[-1].split(".")[0])
            case.py = py
            #生成新的py文件，并覆盖原文件
            tp = keyword.Keyword(self.template, txt, xml, dir)
            tp.gen(py) 
       
        sys.path.append(dir)
        gl.current_case.dir = dir

        module_name = case.py.rpartition("/")[-1].split(".")[0]
        mod = __import__(module_name)
        sys.modules.pop(module_name)
        sys.path.remove(dir)
        return mod

    def __handleException(self, x, rpt):
        """处理用例抛出的异常"""
        if x.level == 0:
            pass
        elif x.level == 1:
            rpt.result = 1
            rpt.detail.append(x.descr)
        elif x.level == 2:
            rpt.result = 3
            rpt.detail.append(x.descr)
        else:
            raise EXCEPTION(2, "Exception level error") 

    def __runCase(self, case):
        mod = self.__importCase(case)
        test_case = mod.TestCase()
        test_case.pool = copy.deepcopy(self.pool)
        test_case.conf = copy.deepcopy(self.conf)
        test_case.report = report.Report()
        case_name = case.name
        test_case.report.name = case_name
        test_case.report.begin_time = time.time()
        log(0, '<< %s >>'%(case_name))
        
        def process(fn, case):
            """执行函数fn，同时对函数的异常进行处理"""
            try:
                fn()
            except EXCEPTION, x:
                self.__handleException(x, case.report)
            except:
                tb = traceback.format_exc()
                log(2, "\n%s"%tb)
                case.report.insert('error', tb)

        process(test_case.go, test_case)
        test_case.report.end_time = time.time()
        rpt = copy.deepcopy(test_case.report)
        for rsc in test_case.reglist:
            if self.conf.rollback: 
                process(rsc.rollback, test_case)
            rsc.release()
        del test_case, case
        return rpt

    def __getCaseList(self):
        if self.conf.order == "random":
            import random
            random.shuffle(self.conf.execute)
        return self.conf.execute

    def __run(self, report_list):
        """运行普通用例集"""
        case_list = self.__getCaseList()
        for case in case_list:
            rpt = self.__runCase(case)
            report_list.append(rpt)
            if rpt.result == 3:
                break
            print '\n'

    def doIt(self):
        """功能：执行测试"""
        lst = []
        self.__run(lst)
        self.report_list = lst

    def doReport(self):
        """功能：生成测试报告"""
        log(0, 'Generating report')
        report.do_report(self.conf, self.report_list)
