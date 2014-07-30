#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of libserv.

import pexpect
from test_station.libserv.serv import Serv
from test_station.err import EXCEPTION
from test_station.logging.logger import log
from test_station.resource import Resource
from test_station import gl
from test_station.libfile import file

class TestServer(Serv, Resource):
    def __init__(self, node):
        Serv.__init__(self, None, None)
        Resource.__init__(self, node.get("name"), "test_server")
        self.is_fragroute = False
        self.connect = []
        self.__parse(node)

    def release(self):
        if self.is_fragroute:
            ss = self.child
            ss.sendline("killall fragroute")
            ss.expect("#", 5)
            log(0, "Fragroute close")

    def __parse(self, node):
        self.ip = node.findtext("ip")
        self.password = node.findtext("passwd")
        self.if_name = node.findtext("if_name")
        self.if_ip = node.findtext("if_ip")
        self.if_mac = node.findtext("if_mac")

    def login(self):
        self.remoteLogin()

    def __load(self, pcap):
        dir = gl.current_case.dir
        newpcap = "%s-%s"%(dir.strip("/").rpartition("/")[-1],pcap.rpartition("/")[-1])
        src_stream = "%s/%s"%(dir.strip("/"),pcap)
        dst_stream = "/root/autotest/%s"%newpcap

        f = file.File()
        f.connect(self.ip, 1234)
        f.transfer(src_stream, dst_stream)
        return dst_stream

    def __tcpReplay(self, if_name, pcap, num, pps, timeout):
        try:
            ss = self.child
            ss.sendline('tcpreplay -i %s -l %s -p %s %s' % (if_name, num, pps, pcap))
            index = ss.expect(['Actual:', 'No such file or directory'], timeout)
            if index == 0:
                log(0, 'Start tcpreplay: -i %s -l %s -p %s %s' % (if_name, num, pps, pcap))
            elif index == 1:
                log(2, 'Start tcpreplay: No such file or directory')
                raise EXCEPTION(2, 'Set tcpreplay: No such file or directory')

        except pexpect.TIMEOUT:
            log(2, 'Start tcpreplay: time out ...')
            raise EXCEPTION(2, 'Set tcpreplay: time out')

    def replay(self, pcap, num, pps, timeout=10):
        newpcap = self.__load(pcap)
        self.__tcpReplay(self.if_name, newpcap, num, pps,timeout)

    def fragReplay(self, pcap, num, pps, timeout=10):
        newpcap = self.__load(pcap)
        self.__tcpReplay("lo", newpcap, num, pps, timeout)

    def setFragroute(self, rules, ip, mac):

        def setStaticArp(ss, name, ip, mac):
            try:
                ss.sendline('arp -s %s %s -i %s' % (ip, mac, name))
                index = ss.expect(["arp -s %s %s -i %s\r\n\x1b]0;root@localhost:~\x07(.*?)#" % (ip, mac, name), 'SIOCSARP: Network is unreachable', 'SIOCSARP: Invalid argument'], 10)
                if index == 1:
                    log(2, 'Set static arp: Network is unreachable')
                    raise EXCEPTION(2, 'Set static arp: Network is unreachable')
                elif index == 2:
                    print repr(ss.before)
                    log(2, 'Set static arp: Invalid argument')
                    raise EXCEPTION(2, 'Set static arp: Invalid argument')
                log(0, 'Set static arp: %s %s' % (ip, mac))
            except pexpect.TIMEOUT:
                log(2, 'Set static arp: time out')
                raise EXCEPTION(2, 'Set static arp: time out')
    
        def createFragrouteFile(ss, rules):
            try:
                str = ''
                for rule in rules:
                   str += (rule + '\n') 
                ss.sendline('echo -e "%s">/usr/local/etc/fragtmp.conf' % str)
                ss.expect('fragtmp.conf\r\n\x1b]0;root@localhost:~\x07(.*?)#', 10)
                log(0, 'Create fragroute file: fragtmp.conf')
                return "/usr/local/etc/fragtmp.conf"
            except pexpect.TIMEOUT:
                log(2, 'Create fragroute file: time out')
                raise EXCEPTION(2, 'Create fragroute file: time out')

        try:
            ss = self.child
            setStaticArp(ss, self.if_name, ip, mac)
            file = createFragrouteFile(ss, rules)
            ss.sendline("killall fragroute")
            ss.expect("#", 5)
            ss.sendline('/usr/local/sbin/fragroute -f %s %s > /dev/null &' % (file, ip))
            ss.expect("#", 5)
            self.is_fragroute = True
            log(0, 'Start fragroute: -> %s' % ip)
        except pexpect.TIMEOUT:
            print repr(ss.before)
            log(2, 'Start fragroute: time out')
            raise EXCEPTION(2, 'Set fragroute: time out') 
