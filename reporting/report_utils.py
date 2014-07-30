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
        
class XmlReport(Report):
    """change case value to xml format"""
    def __init__(self, report_file):
        self.fd = open(report_file, "w")
        self.fd.write('<?xml version="1.0" encoding="UTF-8"?>');
        self.fd.write(os.linesep)
        self.fd.write('<testcases>')
        self.fd.write(os.linesep)
        
    def __del__(self):
        self.fd.write('</testcases>')
        self.fd.write(os.linesep)        
        self.fd.close()
        
    def case2xml(self, obj, converter):
        case_xml = converter(obj) if converter != None else ("<testcase>%s</testcase>" % str(obj))
        self.fd.write(case_xml)
        self.fd.write(os.linesep)

class TxtReport(Report):
    def __init__(self, report_file):
        self.fd = open(report_file, "w")
        self.fd.write(os.linesep)
        
    def __del__(self): 
        self.fd.close()
    def case2txt(self, obj, converter):
        case_txt = converter(obj) if converter != None else str(obj)
        self.fd.write(case_txt)
        self.fd.write(os.linesep)

class HtmlReport(Report):
    def __init__(self, report_file):
        self.fd = open(report_file, "w")
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
        
    def case2html(self, obj, converter):
        case_html = converter(obj) if converter != None else str(obj)
        self.fd.write(case_html)
        self.fd.write(os.linesep)

class Sender(object):
    def __init__(self, server, username = None, password = None, debug = False):
        self.smtp = smtp(server)
        self.smtp.set_debuglevel((1 if debug == True else 0))
        try:
            if username == None:
                self.smtp.login('mingyr@sugon.com', 'm1i2n3g4')
            else:
                self.smtp.login(username, password)
        except Exception:
            self.init = False
        else:
            self.init = True
            
    def send(self, report_file, from_addr, to_addrs):
        if self.init == False:
            print("Instance not properly instanitiated")
            return -1
        
        self.msgs = [email.Message.Message() for to in to_addrs]        
        for msg , to in zip(self.msgs, to_addrs):
            msg["From"] = from_addr
            msg["To"] = to
            msg["Subject"] = "Auto-Test Result Reporting"
            msg["MIME-Version"] = "1.0"
            msg["Content-Type"] = "Multipart/mixed"
            msg.preamble = "MIME Message"
            msg.epilogue = ""
        
        content_type, ignored = mimetypes.guess_type(report_file)
        if content_type == None:
            content_type = "Application/octet-stream"
        content_encoded = cStringIO.StringIO()
        with open(report_file, "rb") as f:
            main_type = content_type[:content_type.find("/")]
            if main_type == "text":
                cte = "quoted-printable"
                quopri.encode(f, content_encoded, 1)
            else:
                cte = "base64"
                base64.encode(f, content_encoded)
            f.close()
        
        sub_msg = email.Message.Message()
        sub_msg.add_header("Content-Type", content_type, name = report_file)
        sub_msg.add_header("Content-Transfer-Encoding", cte)
        sub_msg.set_payload(content_encoded.getvalue())
        content_encoded.close()
        for msg, to in zip(self.msgs, to_addrs):
            msg.attach(sub_msg)
            f = StringIO.StringIO()
            g = email.Generator.Generator(f)
            g.flatten(msg)
            try:
                self.smtp.sendmail(from_addr, to, f.getvalue())    
            except Exception:
                print("send to %s failed" % to)
            f.close()
        
    def __del__(self):
        self.smtp.quit()
    
def converter_factory(style):
    html_counter = [0]
    xml_Counter = [0]
    txt_counter = [0]
    def html_converter(obj):
        html_counter[0] += 1
        if html_counter[0] % 2 == 1:
            fmt = """
            <tr class="odd">
                <td class="col1">%s</td><td class="col2">%s</td><td class="col3">%s</td><td class="col4">%s</td>
            </tr>
            """
            html = fmt % (obj.name, obj.descr, obj.result, obj.detail)
            return html
        else:
            fmt = """
            <tr class="even">
                <td class="col1">%s</td><td class="col2">%s</td><td class="col3">%s</td><td class="col4">%s</td>
            </tr>
            """
            html_string = fmt % (obj.name, obj.descr, obj.result, obj.detail)
            return html_string
    def xml_converter(obj):
        xml_counter[0] += 1
        fmt = """
        <testcase>
            <name>%s</name>
            <descr>%s</descr>
            <state>%s</state>
            <result>%s</result>
        </testcase>
        """
        xml_string = fmt % (obj.name, obj.descr, obj.result, obj.detail)
        return xml_string
    def txt_converter(obj):
        txt_counter[0] += 1
        detail = '\n'.join(obj.detail)
        result = converter_state(obj.result)
        return "%10s%20s%40s\n\n%s\n\n" % (obj.name, obj.descr, result, detail)
        
    if style == "html":
        html_counter[0] = 0
        return html_converter
    elif style == "xml":
        xml_counter[0] = 0
        return xml_converter
    elif style == "txt":
        txt_counter[0] = 0
        return txt_converter
    else:
        return None


def converter_state(result):
    if result == 0:
        return 'Passed'
    elif result == 1:
        return 'Failed'
    elif result == 2:
        return 'Failed'
    elif result == 3:
        return 'Failed and exited'

def test():
    class Testcase(object):
        def __init__(self, name, descr, result, detail):
            def attributesFromDict(d):
                self = d.pop('self')
                for n, v in d.iteritems( ):
                    setattr(self, n, v)
            attributesFromDict(locals())
 
    report = HtmlReport("report-test.html")
    converter = converter_factory("html")  
    case1 = Testcase("case1", "case1", "pass", "normal")
    case2 = Testcase("case2", "case2", "failed", "abnormal")

    report.case2html(case1, converter)
    report.case2html(case2, converter)
    
    sender = Sender('mail.sugon.com')
    sender.send("report-test.html", "mingyr@sugon.com", ["mingyr@sugon.com"])

if __name__ == '__main__':
    test()
