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
        

class ConvertCaseListToHtml(Report):
    def __init__(self, conf):
        self.report_file = conf.report_name
	self.mail_server = conf.mail_server
        self.sender = conf.sender
        self.send_password = conf.sender_password
        self.address_list = conf.address_list
        self.html_counter = [0]
        self.fd = open(self.report_file+'.html', "w")
        header = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd"
    >
<html>
<head>
    <meta content="text/html; charset=UTF-8" http-equiv="Content-Type">
    <title>自动化测试结果报告</title>
    <style type="text/css">
        body {
            font-size: 14px;
        }
        table {
            width: 80%;
            overflow: hidden;
            margin-left: auto;
            margin-right: auto;
            border: solid 1px;  
        }
        table th {
            padding-left: 30px;
            padding-right: 30px;
            padding-top: 10px;
            padding-bottom: 10px;
            font-family: serif;
            font-size: 18px;
            color: #030303;
        }
        .col1 {
            width: 20%
        }
        .col2 {
            width: 30%;
        }
        .col3 {
            width: 20%;
        }
        .col4 {
            width: 30%;
        }
        .odd {
            background-color: #00C0E0;
        }
        .even {
            background-color: #EFEFEF;
        }
    </style>

</head>
<body>
    <div>
        <table>
            <tr>
                <th class="col1">测例名称</th><th class="col2">测例描述</th><th class="col3">结束状态</th><th class="col4">成功结果/失败原因</th>
            </tr>
        
        """
        self.fd.write(header)
        self.fd.write(os.linesep)
        
    def __del__(self):
        footer = """
        </table>
    </div>
</body>
</html>        
        """
        self.fd.close()
        
    def convert_to_html(self,report_list):
        for case in report_list:
            self.html_counter[0] += 1
            if self.html_counter[0] %2 == 1:
                fmt = """
                <tr class="odd">
                <td class="col1">%s</td><td class="col2">%s</td><td class="col3">%s</td><td class="col4">%s</td>
                </tr>
                """
                html = fmt % (case.name, case.descr, case.result, case.detail)
            else:
                fmt = """
                <tr class="even">
                    <td class="col1">%s</td><td class="col2">%s</td><td class="col3">%s</td><td class="col4">%s</td>
                </tr>
                """
                html_string = fmt % (case.name, case.descr, case.result, case.detail)

                self.fd.write(html_string)
                self.fd.write(os.linesep)

   
