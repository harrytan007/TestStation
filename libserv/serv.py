#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of libserv.

import pexpect
import string
import inspect
from test_station.err import EXCEPTION
from test_station.logging.logger import log


class Ssh():
    def __init__(self):
        self.child = None
        self.state = None

def sshLoginServ(ip, username, password):
    try:
        ssh = Ssh()
        ss = pexpect.spawn('ssh root@%s' % ip)
        ssh.child = ss
        index = ss.expect(['password:', 'yes/no', 'Host key verification failed'], 10)
        if index == 0:
            pass
        elif index == 1:
            ss.sendline('yes')
            ss.expect(['password:'], 10)
            pass
        elif index == 2:
            ssh.state = -2
            return ssh
        ss.sendline(password)
        index = ss.expect(['#', 'try again.'], 10)
        if index == 0:
            ssh.state = 0
            return ssh
        elif index == 1:
            ssh.state = -1
            return ssh
    except pexpect.TIMEOUT:
        ssh.state = -3
        return ssh

class Serv():
    def __init__(self, ip, password):
        #self.name = (inspect.stack()[1][-2][0]).split('=')[0].strip()
        self.ip = ip
        self.password = password
        self.child = None

    # Login remote device.
    def remoteLogin(self):
        ret = sshLoginServ(self.ip, 'root', self.password)
        self.child = ret.child
        if ret.state == 0:
            log(0, 'Login root@%s' % self.ip)
        elif ret.state == -1:
            log(2, 'Password error')
            raise EXCEPTION(2, 'Login remote: password error')
        elif ret.state == -2:
            log(2, 'Host key verification failed')
            raise EXCEPTION(2, 'Remote login: host key verification failed')
        elif ret.state == -3:
            log(2, 'Remote login(%s): time out'%self.ip)
            raise EXCEPTION(2, 'Remote login(%s): time out'%self.ip)
    # Logout remote device.
    def remoteLogout(self):
        ss = self.child
        ss.sendline('logout')
        log(0, 'Logout from %s' % self.ip)

    def cd(self, dir):
        try:
            ss = self.child
            ss.sendline('cd %s' % dir)
            ss.expect('cd %s\r\n[root@(.*?) (.*?)]#' % dir, 10)
            log(0, 'Enter directory: %s' % dir)
        except pexpect.TIMEOUT:
            log(2, 'Enter directory: time out')
            raise EXCEPTION(2, 'Enter directory: time out')

    def setIfState(self, name, state):
        try:
            ss = self.child
            ss.sendline('ifconfig %s %s'%(name,state))
            ss.expect('#')
            log(0, 'Set interface %s: %s' % (name, state))
        except pexpect.TIMEOUT:
            log(2, 'Set interface %s: time out' % name)
            raise EXCEPTION(2, 'Set interface %s: time out' % name) 
