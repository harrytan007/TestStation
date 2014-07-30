#!/usr/bin/env python
# coding: utf-8

################################################
# @file report.py
# @brief Reporting module of test results
#
# @author hum, mingyr (@sugon.com)
# @date 
#
# @author, tanhy
# @date 2013/04/14
################################################
try:
    import os
    import sys
    import re
    import base64
    import quopri
    import mimetypes
    import email.Generator
    import email.Message
    import cStringIO
    import StringIO
    from smtplib import SMTP as smtp
except ImportError:
    print "import modules failed\n"
    exit()

class Report(object):
    def __init__(self):
        pass
    
    def __del__(self):
        pass
        
class ConvertCaseListToTxt (Report):
    def __init__ (self,conf):
	self.filename = conf.report_name
        self.total_num = 0
        self.pass_num = 0
        self.fail_num = 0
        self.undo_from_case = 0
        self.undo_from_test = 0
        self.test_time = 0
        self.seq_num = { }
        self.count = 0
        self.fd = open(self.filename+'.rpt', "w")
        self.fd.write(os.linesep)
        self.pass_list = []
        self.fail_list = []
        self.undo_from_case_list = []
        self.undo_from_test_list = []
    def convert_to_txt (self,report_list):
        for case in report_list:
            self.detail ='\n'.join(case.detail)
            self.result = self.convert_state(case.result)
            index = self.seq_num[case.name]
            str_1 = "[%s] %s\n%s\n"%(self.seq_num[case.name],case.name,self.result)
            self.fd.write(str_1.encode("utf-8"))
            str_2 = "Detail:\n%s\n%s"%(self.detail, "-"*160)
            self.fd.write(str_2)
            self.fd.write(os.linesep)

    def convert_state (self,state):
        if state == 0:
            return 'Passed'
	if state == 1:
            return 'Failed'
	if state == 2:
            return 'Failed and exit from case'
        if state == 3:
            return 'Failed and exit from test'
    
    def overview (self,report_list):
        for case in report_list:
            self.count += 1
            if case.result == 0:
                self.pass_num += 1
                self.pass_list.append (case.name)               
            if case.result == 1:
                self.fail_num +=1
                self.fail_list.append (case.name)
            if case.result == 2:
                self.undo_from_case += 1
                self.undo_from_case_list.append (case.name)
            if case.result == 3:
                self.undo_from_test += 1
                self.undo_from_test_list.append (case.name)
            self.total_num += 1
            self.test_time += case.end_time - case.begin_time
            self.seq_num[case.name] = self.count

        self.overview_txt = "%s\n\n%s%25s%25s%30s%30s%20s+%.2f\n\n%s\n" % \
                            (72*'*'+'Overview  Result'+72*'*',\
                            'Total: '+ str(self.total_num),\
                            'Passed: '+ str(self.pass_num),'Failed: '+ str(self.fail_num),'Exit From Case: '\
                            + str(self.undo_from_case),'Exit From Test: '+ str(self.undo_from_test),'Test Time: ',self.test_time,\
                           73 *'*'+'Overview List'+73*'*')
        self.fd.write(self.overview_txt)
        self.fd.write(os.linesep)
        self.name_list_txt = '-----PASSED CASES-----\n'       
        for name in self.pass_list:
            self.name_list_txt +='['+str(self.seq_num[name])+'] '+name+'\n'
	self.name_list_txt +='\n'+ '-----FALIED CASES-----\n' 
        for name in self.fail_list:
            self.name_list_txt += '['+str(self.seq_num[name])+'] '+name+'\n'
        self.name_list_txt +='\n'+ '-----EXIT FROM CASE----\n'
        for name in self.undo_from_case_list:
            self.name_list_txt += '['+str(self.seq_num[name])+'] '+name + '\n'
        self.name_list_txt +='\n'+ '-----EXIT FROM TEST----\n' 
        for name in self.undo_from_test_list:
            self.name_list_txt +='['+str(self.seq_num[name])+'] '+ name+ '\n'
        self.name_list_txt += 76*'*'+'Detail'+76*'*'+'\n'
        self.fd.write(self.name_list_txt.encode("utf-8"))
        self.fd.write(os.linesep)   

    def __del__ (self):
        self.fd.close()
