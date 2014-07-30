#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of libserv.

import pexpect
import re
import string
from test_station.libserv.serv import Serv
from test_station.err import EXCEPTION
from test_station.logging.logger import log
from test_station.resource import Resource
from test_station import gl

class Reflow(Serv, Resource):
    def __init__(self, node):
        Serv.__init__(self, None, None)
        Resource.__init__(self, node.get("name"), "reflow")
        self.connect = []
        self.__parse(node)

    def __parse(self, node):
        self.type = node.findtext("type")
        self.ip = node.findtext("ip")
        self.password = node.findtext("passwd")
        self.dir = node.findtext("dir")
        self.if_ip = node.findtext("if_ip")
        self.if_mac = node.findtext("if_mac")
        self.if_name = node.findtext("if_name")
        self.if_port = node.findtext("if_port")

    def login(self):
        self.remoteLogin()

    def __vbReflowGet(self, keyword):
        ss = self.child
        ss.sendline('/usr/local/sbin/reflow_tool -p')
        ss.expect('/usr/local/sbin/reflow_tool -p(.*?)packets recv:(.*?)#', 10)
        m = re.match(r".*packets recv\:(\d+)\s+reflow\:(\d+)", ss.after.replace('\r\n', ''))
        if keyword is 'recv':
            ret = string.atoi(m.group(1))
        elif keyword is 'send':
            ret = string.atoi(m.group(2))
        return ret

    def __netfirmReflowGet(self, keyword):
        ss = self.child
        ss.sendline("%s/reflow_rule find %s"%(self.dir.rstrip("/"), self.if_ip))
        index = ss.expect(["recv:<(.*?)> reflow:<(.*?)>", r"find %s\r\n\x1b]0;root@localhost:~\x07"%self.if_ip], 5)
        if index == 0:
            m = re.match(r".*recv\:\<(\d+)\>\s+reflow\:\<(\d+)\>", ss.after.replace('\r\n', ''))
            if keyword is "recv":
                ret = string.atoi(m.group(1))
            elif keyword is "send":
                ret = string.atoi(m.group(2))
        elif index == 1:
            ret = 0
        return ret

    def reflowGet(self, keyword):
        """功能：获取回流计数
           输入：recv（收到包数），send（回流包数）
           输出：包数
        """
        try:
            if keyword in ["recv", "send"]:
                if self.type == "vb":
                    ret = self.__vbReflowGet(keyword)
                elif self.type == "netfirm":
                    ret = self.__netfirmReflowGet(keyword)
                log(0, "Get %s counts of reflow server(%s): %d" % (keyword, self.if_ip, ret))
                return ret
            else:
                log(2, "Unmatched keyword of getting reflow")
                raise EXCEPTION(1, "Get reflow counts: unmatched keyword of getting reflow")
        except pexpect.TIMEOUT:
            log(2, "Get %s counts of reflow server(%s): time out" % (keyword, self.if_ip))
            raise EXCEPTION(2, "Get %s counts of reflow server(%s): time out" % (keyword, self.if_ip))

    def __vbReflowClear(self):
        ss = self.child
        ss.sendline('/usr/local/sbin/reflow_tool -c')
        ss.expect('/usr/local/sbin/reflow_tool -c\r\n(.*?)', 5)

    def __netfirmReflowClear(self):
        ss = self.child
        ss.sendline("%s/reflow_rule clear %s"%(self.dir.rstrip("/"), self.if_ip))
        ss.expect("#", 5)

    def reflowClear(self):
        try:
            if self.type == "vb":
                self.__vbReflowClear()
            elif self.type == "netfirm":
                self.__netfirmReflowClear()
            log(0, "Clear reflow(%s) counts"%self.if_ip)
        except pexpect.TIMEOUT:
            log(2, "Clear reflow(%s) counts: time out"%self.if_ip)
            raise EXCEPTION(2, "Clear reflow(%s) counts: time out"%self.if_ip)

    def setIfState(self, state):
        ss = self.child
        action = {"up":"add", "down":"del"}
        try:
            if state in ["up", "down"]:
                if self.type == "netfirm":
                    ss.sendline("%s/reflow_rule %s \"%s;%s;%s;\""%(self.dir.rstrip("/"), action[state], self.if_ip, self.if_mac, self.if_port))
                    ss.expect("#", 5)
                    log(0, "Set interface(%s) state: %s"%(self.if_ip, state))
            else:
                log(2, "Unmatched state of setting interface state")
                raise EXCEPTION(1, "Unmatched state of setting interface state")
        except pexpect.TIMEOUT:
            log(2, "Set interface(%s) state: time out"%self.if_ip)
            raise EXCEPTION(2, "Set interface(%s) state: time out"%self.if_ip)

