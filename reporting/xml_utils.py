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
        
class ConverCaseListToXmlReport(Report):
    def __init__(self, conf):
        self.report_file = conf.report.name
        self.fd = open(self.report_file, "w")
        self.fd.write('<?xml version="1.0" encoding="UTF-8"?>');
        self.fd.write(os.linesep)
        self.fd.write('<testcases>')
        self.fd.write(os.linesep)
        
    def __del__(self):
        self.fd.write('</testcases>')
        self.fd.write(os.linesep)        
        self.fd.close()
        
    def convert_to_xml(self, case_list):
        for case in case_list:
            fmt = """
            <testcase>
                <name>%s</name>
                <descr>%s</descr>
                <result>%s</result>
                <detail>%s</detail
            </testcase>
            """
            self.case_xml = fmt % (case.name.case.descr,case.result,case.detail)
            self.fd.write(case-xml)
            self.fd.write(linesep)
