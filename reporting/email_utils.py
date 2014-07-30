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
        

class Sender(object):
    def __init__(self, conf):
        self.from_addr = conf.sender
        self.smtp = smtp(conf.mail_server)
	self.debug = False
        self.password = conf.sender_password
        self.report_file = conf.report_name+'.html'
        self.address_list = conf.address_list
        self.smtp.set_debuglevel((1 if self.debug == True else 0))
        try:
            if self.username == None:
                self.smtp.login('gaoxun@sugon.com', '1q2w3e4r')
            else:
                self.smtp.login(self.from_addr,self.password)
        except Exception:
            self.init = False
        else:
            self.init = True
            
    def send(self):
        if self.init == False:
            print("Instance not properly instanitiated")
            return -1
        
        self.msgs = [email.Message.Message() for to in self.address_list]        
        for msg , to in zip(self.msgs, self.address_list):
            msg["From"] = self.from_addr
            msg["To"] = to
            msg["Subject"] = "Auto-Test Result Reporting"
            msg["MIME-Version"] = "1.0"
            msg["Content-Type"] = "Multipart/mixed"
            msg.preamble = "MIME Message"
            msg.epilogue = ""
        
        content_type, ignored = mimetypes.guess_type(self.report_file)
        if content_type == None:
            content_type = "Application/octet-stream"
        content_encoded = cStringIO.StringIO()
        with open(self.report_file, "rb") as f:
            main_type = content_type[:content_type.find("/")]
            if main_type == "text":
                cte = "quoted-printable"
                quopri.encode(f, content_encoded, 1)
            else:
                cte = "base64"
                base64.encode(f, content_encoded)
            f.close()
        
        sub_msg = email.Message.Message()
        sub_msg.add_header("Content-Type", content_type, name = self.report_file)
        sub_msg.add_header("Content-Transfer-Encoding", cte)
        sub_msg.set_payload(content_encoded.getvalue())
        content_encoded.close()
        for msg, to in zip(self.msgs,self.address_list):
            msg.attach(sub_msg)
            f = StringIO.StringIO()
            g = email.Generator.Generator(f)
            g.flatten(msg)
            try:
                self.smtp.sendmail(self.from_addr, to, f.getvalue())    
            except Exception:
                print("send to %s failed" % to)
            f.close()
        
    def __del__(self):
        self.smtp.quit()
