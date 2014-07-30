#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of libcli.

"""G设备CLI控制模块"""

import types
import string
import re
import time

from cli import Cli
from cli import timeout
from test_station.logging.logger import log
from test_station.err import EXCEPTION

class Rule:
    """规则类,所有类型的规则类都将类作为超类"""
    def str(self,form_list):
        """将输入列表中的项目以字符串的形式输出"""
        s = ''
        dict = vars(self)
        for key in form_list:
            item = dict[key]
            if isinstance(item, int):
                item = '%d' % item
            s = s + item + ' '
        return s.rstrip()

class MplsRule(Rule):
    """mpls规则类,自带可生成命令行字符串的方法"""
    def __init__(self):
        self.transaction_no = 0
        self.mpls_id = 0
       # self.hit_stat = 1
        self.combined_rule = 'trunk'

    def line(self):
        if self.combined_rule == 'trunk':
            return self.str(['transaction_no', 'mpls_id'])
        else:
            return self.str(['transaction_no', 'mpls_id','combined_rule'])

    def lineForShow(self):
        if self.combined_rule == 'trunk':
            return self.str(['transaction_no', 'mpls_id'])
        else:
            return self.str(['transaction_no', 'mpls_id', 'combined_rule'])
    
    def set(self, str):
        lst = str.split()
        self.transaction_no,self.mpls_id = int(lst[0]),int(lst[1])
        if self.combined_rule != 'trunk':
            self.combined_rule = int(lst[2])

class VlanRule(Rule):
    """vlan规则类,自带可生成命令行字符串的方法"""
    def __init__(self):
        self.transaction_no = 0
        self.vlan_id = 0
        #self.hit_stat = 1
        self.combined_rule = 'trunk'

    def line(self):
        if self.combined_rule == 'trunk':
            return self.str(['transaction_no', 'vlan_id'])
        else:
            return self.str(['transaction_no', 'vlan_id', 'combined_rule'])

    def lineForShow(self):
        if self.combined_rule == 'trunk':
            return self.str(['transaction_no', 'vlan_id'])
        else:
            return self.str(['transaction_no', 'vlan_id', 'combined_rule'])
    
    def set(self, str):
        lst = str.split()
        self.transaction_no,self.vlan_id = int(lst[0]),int(lst[1])
        if self.combined_rule != 'trunk':
            self.combined_rule = int(lst[2])

class Ipv4FlexRule(Rule):
    """IPV4灵活规则类,自带可生成命令行字符串的方法"""
    def __init__(self):
        self.sip = '0.0.0.0'
        self.dip = '0.0.0.0'
        self.sport = 0
        self.dport = 0
        self.proto = 0
        self.transaction_no = 0
        self.bidirection_flag = 0
        self.hit_stat = 1
        self.combined_rule = 'trunk'

    def line(self):
        if self.combined_rule == 'trunk':
            return self.str(['sip', 'dip', 'sport', 'dport', 'proto', 'transaction_no', 'bidirection_flag', 'hit_stat'])
        else:
            return self.str(['sip', 'dip', 'sport', 'dport', 'proto', 'transaction_no', 'bidirection_flag', 'hit_stat', 'combined_rule'])

    def lineForShow(self):
        if self.combined_rule == 'trunk':
            return self.str(['sip', 'dip', 'sport', 'dport', 'proto', 'transaction_no', 'bidirection_flag'])
        else:
            return self.str(['sip', 'dip', 'sport', 'dport', 'proto', 'transaction_no', 'bidirection_flag', 'combined_rule'])
    
    def set(self, str):
        lst = str.split()
        self.sip,self.dip,self.sport,self.dport,self.proto = lst[0],lst[1],int(lst[2]),int(lst[3]),int(lst[4])
        self.transaction_no,self.bidirection_flag = int(lst[5]),int(lst[6])
        if self.combined_rule != 'trunk':
            self.combined_rule = int(lst[7])
             

#功能：IPV4掩码规则类
class Ipv4MaskRule(Rule):
    """IPV4掩码规则类"""
    def __init__(self):
        self.sip = '0.0.0.0'
        self.msip = '0.0.0.0'
        self.dip = '0.0.0.0'
        self.mdip = '0.0.0.0'
        self.sport = 0
        self.msport = 0
        self.dport = 0
        self.mdport = 0
        self.proto = 0
        self.mproto = 0
        self.transaction_no = 0
        self.bidirection_flag = 0
        self.hit_stat = 1
        self.combined_rule = 'Trunk'

    def line(self):
        if self.combined_rule == 'Trunk':
            return self.str(['sip', 'msip', 'dip', 'mdip', 'sport', 'msport', 'dport', 'mdport', 'proto', 'mproto', 'transaction_no', 'bidirection_flag', 'hit_stat'])
        else:
            return self.str(['sip', 'msip', 'dip', 'mdip', 'sport', 'msport', 'dport', 'mdport', 'proto', 'mproto', 'transaction_no', 'bidirection_flag', 'hit_stat', 'combined_rule'])

    def lineForShow(self):
        if self.combined_rule == 'Trunk':
            return self.str(['sip', 'msip', 'dip', 'mdip', 'sport', 'msport', 'dport', 'mdport', 'proto', 'mproto', 'transaction_no', 'bidirection_flag'])
        else:
            return self.str(['sip', 'msip', 'dip', 'mdip', 'sport', 'msport', 'dport', 'mdport', 'proto', 'mproto', 'transaction_no', 'bidirection_flag', 'combined_rule'])

    def set(self, str):
        lst = str.split()
        self.sip,self.msip,self.dip,self.mdip = lst[0],lst[1],lst[2],lst[3]
        self.sport,self.msport,self.dport,self.mdport = int(lst[4]),int(lst[5]),int(lst[6]),int(lst[7])
        self.proto,self.mproto = int(lst[8]),int(lst[9])
        self.transaction_no,self.bidirection_flag = int(lst[10]),int(lst[11])
        if self.combined_rule != 'Trunk':
            self.combined_rule = int(lst[12])


class Ipv6FlexRule(Ipv4FlexRule):
    """IPV6灵活规则类"""
    def __init__(self):
        Ipv4FlexRule.__init__(self) 
        self.sip = '0::0'
        self.dip = '0::0'

    def set(self, str):
        Ipv4FlexRule.set(self,str)

class Ipv6MaskRule(Ipv4MaskRule):
    """IPV6掩码规则类"""
    def __init__(self):
        Ipv4MaskRule.__init__(self)
        self.sip = '0::0'
        self.msip = 0
        self.dip = '0::0'
        self.mdip = 0

    def set(self, str):
        Ipv4MaskRule.set(self,str)
        lst = str.split()
        self.msip,self.mdip = int(lst[1]),int(lst[3])


class DpiRule(Rule):
    """DPI规则类"""
    def __init__(self):
        self.dpi = '00000000'
        self.mdpi = '00000000'
        self.transaction_no = 0
        self.hit_stat = 0
        self.window_start_position = 0
        self.combined_rule = 'Trunk'

    def line(self):
        if self.combined_rule == 'Trunk':
            return self.str(['dpi', 'mdpi', 'transaction_no', 'hit_stat', 'window_start_position'])
        else:
            return self.str(['dpi', 'mdpi', 'transaction_no', 'hit_stat', 'window_start_position', 'combined_rule'])

    def lineForShow(self):
        return self.line()

    def set(self, str):
        lst = str.split()
        self.dpi,self.mdpi,self.transaction_no = lst[0],lst[1],int(lst[2])
        self.hit_stat,self.window_start_position = int(lst[3]),int(lst[4]),int(lst[5])
        if self.combined_rule != "Trunk":
            self.combined_rule = int(lst[6])


permission = {'admin':('restore','setHeaderStrip','setInfoCarry','clearFragmentTable','clearPort','setRcpPermitIp','reset',
'addRuleMode','delRuleMode',"setCommonRuleMode",'setTransaction','getTransactionHost','setTransactionHost','clearTransactionHost','getPort','setPort','portStable',
'addRule','clearRule','dpiMatch','clearTransactionRule','getTransactionRule','getTransactionHit','getRuleHit',"getRule", 'clearHit',
'setTransactionPriority','setIpInIpGlobal',"setIpInIpPacketType",'setIpInIpGlobalHash','setLinkProtection','setAclQuota','setIp','removeIp','setTransactionAgeTime', 
'setFragmentAge','setFragmentCache',"setKeepAliveProtocol","setKeepAliveInterval","setPortIp"),
'debug':('setAccurateCount')}


class CliG(Cli):
    """G设备CLI类"""
    def __init__(self, node):
        Cli.__init__(self, node)
        if self.user != 'debug':
            self._addRollback('clearHit', '')
        self.permission = permission

    def login(self):
        """登陆CLI"""
        self._remoteLogin()
        if self.state == 1:
            self._userAuth(self.user, self.passwd)
        self.is_login = True

    @timeout
    def _enterTransactionView(self, trans_no):
        """进入transaction视图"""
        if 'transaction %d' % trans_no != self.cur_view:
            ss = self.child
            ss.sendline("transaction %d" % trans_no)
            ss.expect('transaction %d\r\n<(.*?)@(.*?) transaction %d>' % (trans_no, trans_no), 5)
            if self.cur_view == 'root':
                self.state += 1
            self.cur_view = 'transaction %d' % trans_no

    @timeout
    def _enterLinkProtectionView(self, opb_slot_no, module_no):
        """进入link-protection视图"""
        if 'link-protection %d/%d' % (opb_slot_no, module_no) != self.cur_view:
            ss = self.child
            ss.sendline('link-protection %d/%d' % (opb_slot_no, module_no))
            ss.expect('link-protection %d/%d\r\n<(.*?)@(.*?) link-protection %d/%d>' % (opb_slot_no, module_no,opb_slot_no, module_no), 5)
            if self.cur_view == 'root':
                self.state += 1
            self.cur_view = 'link-protection %d/%d' % (opb_slot_no, module_no)

    #功能：配置rule-mode
    #输入：trans_no（业务组号），rule_mode_list（rule-mode列表，例['sip', 'sip-dip']）
    @timeout
    def addRuleMode(self, trans_no, rule_mode_list):
        """配置rule-mode
           输入：trans_no（业务组号），rule_mode_list（rule-mode列表，例['sip', 'sip-dip']）
        """
        self._permissionCheck('addRuleMode')
        if isinstance(rule_mode_list, list):
            pass
        elif isinstance(rule_mode_list, str):
            rule_mode_list = [rule_mode_list]
        else:
            log(2, 'Add rule mode of transaction %d: rule mode list type error' % trans_no)
            raise EXCEPTION(2, 'Add rule mode of transaction %d: rule mode list type error' % trans_no)
        ss = self.child
        self._enterView('service')
        rule_mode_list += ["mask"] #TODO 后续需要修正
        #while "mask" in rule_mode_list: rule_mode_list.remove("mask") #TODO 后续需要修正
        #while "dpi" in rule_mode_list: rule_mode_list.remove("dpi") #TODO 后续需要修正
        if rule_mode_list == []: return None
        line = ''
        for rule_mode in rule_mode_list:
            line = line + rule_mode + ','
        line = line.strip(',')
        ss.sendline('rule-mode %d %s' % (trans_no, line))
        index = ss.expect(['rule-mode %d %s\r\n<(.*?)@(.*?) service>' % (trans_no, line), 'The flexible rule is exist'], 5)
        if index == 0:
            log(0, 'Add rule mode of transaction %d: %s' % (trans_no, line))
        elif index == 1:
            log(0, 'Add rule mode of transaction %d: the flexible rule is exist' % trans_no)
        self._addRollback('delRuleMode', '')
        if ['clearRule', ''] in self.rollback_stack:
            self.rollback_stack.remove(['clearRule', ''])
        self._addRollback('clearRule', '')

    @timeout
    def delRuleMode(self, trans_no=None):
        """删除rule-mode
           输入：trans_no（业务组号）
        """
        self._permissionCheck('delRuleMode')
        if trans_no == None:
            trans_no = ''
        elif isinstance(trans_no, int):
            trans_no = '%d' % trans_no 
        ss = self.child
        self._enterView('service')
        ss.sendline('no rule-mode-all %s' % trans_no)
        index = ss.expect(['no rule-mode-all %s\r\n<(.*?)@(.*?) service>' % trans_no, 'is exist'], 5)
        if index == 0:
            if trans_no == '':
                trans_no = 'all'
            log(0, 'Delete rule mode: %s' % trans_no)
        elif index == 1:
            log(0, 'Delete rule mode: rules are exist')
            raise EXCEPTION(2, 'Delete rule mode: rules are exist')

    @timeout
    def _getCommonRuleMode(self):
        """获取全局常用规则类型
        """
        ss = self.child
        self._enterView("service")
        ss.sendline("show rule-mode-common")
        index = ss.expect(["show rule-mode-common\r\n(.*?)The service rule mode configure(.*?)<(.*?)@(.*?) service>", "show rule-mode-common\r\n<(.*?)@(.*?) service>"], 5)
        if index == 0:
            lst = ss.after.split()
            bg = lst.index("configure*************")+1
            ed = lst.index("service>")-1
            return lst[bg:ed]
        elif index == 1:
            return []

    @timeout
    def _delCommonRuleMode(self, lst):
        """删除全局常用规则类型
        """
        ss = self.child
        self._enterView("service")
        if lst == []:
            return None
        line = ''
        for rule_mode in lst:
            line = line + rule_mode + ','
        line = line.strip(',')
        ss.sendline("no rule-mode-common %s"%line)
        index = ss.expect(["no rule-mode-common %s\r\n<(.*?)@(.*?) service>"%line, "The flexible rule is exist"], 5)
        if index == 0:
            return len(lst)
        elif index == 1:
            log(2, "(_delCommonRuleMode)The flexible rule is exist")
            raise EXCEPTION(1, "(_delCommonRuleMode)The flexible rule is exist") 

    @timeout
    def setCommonRuleMode(self, lst):
        """设置全局常用规则类型，最多支持6种
        """
        self._permissionCheck("setCommonRuleMode")
        self._enterView("service")
        cur_common_rulemode = self._getCommonRuleMode()
        self._delCommonRuleMode(cur_common_rulemode)
        line = ''
        for rule_mode in lst:
            line = line + rule_mode + ','
        line = line.strip(',')
        ss = self.child
        ss.sendline("rule-mode-common %s"%line)
        index = ss.expect(["rule-mode-common %s\r\n<(.*?)@(.*?) service>"%line], 5) 
        if index == 0:
            log(0, "Set common rule mode: %s"%line)
            if line != "sip,dip,sip-dip,sip-sport-proto,dip-dport-proto,sip-dip-sport-dport-proto":
                self._addRollback("setCommonRuleMode", "[\'sip\',\'dip\',\'sip-dip\',\'sip-sport-proto\',\'dip-dport-proto\',\'sip-dip-sport-dport-proto\']")
           
    @timeout
    def setTransaction(self, trans_no, keyword, value=None):
        """设置业务组
           输入：trans_no（业务组号），keyword（设置对象关键字)，value（设置值）
        """
        self._permissionCheck('setTransaction')
        ss = self.child
        if keyword in ['age-time', 'port', 'no port', 'load balance']:
            self._enterTransactionView(trans_no)
            if keyword == 'age-time':
                ss.sendline('age-time %d' % value)
                ss.expect('age-time %d\r\n<(.*?)@(.*?) transaction (.*?)>' % value)
                log(0, 'Set transaction %d age time: %d' % (trans_no, value))
                self._addRollback('setTransaction', '%d, \'age-time\', 0' % trans_no)
            elif keyword == 'port':
                if not isinstance(value, list):
                    value = [value]
                port_str = ''
                #for i in range(0, len(value)):
                #    port_str = port_str + value[i].get() + ','
                for port in value:
                    port_str = port_str + port.get() + ","
                port_str = port_str.strip(',')
                ss.sendline('port %s' % port_str)
                index = ss.expect(['port %s\r\n<(.*?)@(.*?) transaction (.*?)>' % port_str,\
                                  'is not exist'], 5)
                if index == 0:
                    log(0, 'Add transaction %d ports: %s' % (trans_no, port_str))
                    self._addRollback('setTransaction', '%d, \'no port\'' % trans_no) 
                elif index == 1:
                    log(2, 'Set transaction: Unmatched port name')
                    raise EXCEPTION(1, 'Set tansaction: unmatched port name')
            elif keyword == 'no port':
                if value == None:
                    ss.sendline('no port-all')
                    ss.expect('no port-all\r\n<(.*?)@(.*?) transaction (.*?)>')
                    log(0, 'Remove all ports from transaction %d' % trans_no)
                else:
                    if not isinstance(value, list):
                        value = [value]
                    port_str = ''
                    #for i in range(0, len(value)):
                    #    port_str = port_str + value[i].get() + ','
                    for port in value:
                        port_str = port_str + port.get() + ","
                    port_str = port_str.strip(',')
                    ss.sendline('no port %s' % port_str)
                    ss.expect('no port %s\r\n<(.*?)@(.*?) transaction (.*?)>' % port_str, 5)
                    log(0, 'Remove ports from transaction %d: %s' % (trans_no, port_str))
            elif keyword == 'load balance':
                if value in ['dip', 'sip', 'sip-dip', 'sip-dip-sport-dport', 'sip-dip-sport-dport-protocol']:
                    ss.sendline('load-balance %s' % value)
                    index = ss.expect(['load-balance %s\r\n<(.*?)@(.*?) transaction (.*?)>' % value, 'Error:  No ppb board'], 5)
                    if index == 1:
                        log(2, 'Set transaction %d load balance: no port' % trans_no)
                        raise EXCEPTION(1, 'Set transaction %d load balance: no port' % trans_no)
                    log(0, 'Set transaction %d load balance: %s' % (trans_no, value))
                    self._addRollback('setTransaction', '%d, \'load balance\', \'sip\'' % trans_no) 
                else:
                    log(2, 'Unmatched value of %s' % keyword)
                    raise EXCEPTION(1, 'Set transaction: unmatched value of %s' % keyword)
        else:
            log(2, 'Set %s of transaction: unmatched keyword' % keyword)
            raise EXCEPTION(1, 'Set %s of transaction: unmatched keyword' %keyword)

    @timeout
    def getTransactionHost(self, trans_no, host_no, keyword):
        """功能：获取业务组HOST信息
           输入：trans_no（业务组号），host_no（HOST序号），keyword（关键字）
           输出：获取值
        """
        self._permissionCheck('getTransactionHost')
        ss = self.child
        if keyword in ['ip', 'mac', 'state']:
            self._enterTransactionView(trans_no)
            ss.sendline('show current-transaction')
            ss.expect('host-no   ip                mac                 state(.*?)------------------------------------------------------------', 5)
            lst = ss.after.split()
            ret = lst[lst.index('%d' % host_no) + lst.index(keyword)]
            log(0, 'Get %s of transaction %d host %d: %s' % (keyword, trans_no, host_no, ret))
            return ret
        else:
            log(2, 'Get transaction host: unmatched keyword')
            raise EXCEPTION(1, 'Get transaction host: unmatched keyword')

    @timeout
    def setTransactionHost(self, trans_no, host_no, keyword, value=None):
        """功能：配置业务组HOST
           输入：trans_no（业务组号），host_no（HOST序号）
                 keyword（配置对象，包含'no host'/'ip'/'mac'），
                 value（配置值。'no host'：int型列表（缺省为全删），'ip':'10.0.0.1'，'mac'：'10-00-00-00-00-00'）
        """
        self._permissionCheck('setTransactionHost')
        ss = self.child
        if keyword in ['ip', 'mac']:
            self._enterTransactionView(trans_no)
            if keyword == 'ip':
                ss.sendline('host %d ip %s' % (host_no, value))
                index = ss.expect(['host %d ip %s\r\n<(.*?)@(.*?) transaction (.*?)>' % (host_no, value), 'Fail to add a host, host ip or mac has been taken'], 5)
                if index == 0:
                    log(0, 'Set transaction %d host %d ip: %s' % (trans_no, host_no, value))
                    self._addRollback('clearTransactionHost', '%d' % trans_no)
                elif index == 1:
                    log(2, 'set transaction %d host ip: fail to add a host, host ip or mac has been taken' % trans_no)
                    raise EXCEPTION(1, 'Set transaction %d host ip: fail to add a host, host ip or mac has been taken' % trans_no)
            elif keyword == 'mac':
                ss.sendline('host %d mac %s' % (host_no, value))
                index = ss.expect(['host %d mac %s\r\n<(.*?)@(.*?) transaction (.*?)>' % (host_no, value), 'Fail to add a host, host ip or mac has been taken'], 5)
                if index == 0:
                    log(0, 'Set transaction %d host %d mac: %s' % (trans_no, host_no, value))
                    self._addRollback('clearTransactionHost', '%d' % trans_no)
                elif index == 1:
                    log(2, 'set transaction %d host mac: fail to add a host, host ip or mac has been taken' % trans_no)
                    raise EXCEPTION(1, 'Set transaction %d host mac: fail to add a host, host ip or mac has been taken' % trans_no)
        else:
            log(2, 'Set %s of transaction host: unmatched keyword' % keyword)
            raise EXCEPTION(1, 'Set %s of transaction host: unmatched keyword' % keyword)

    @timeout
    def clearTransactionHost(self, trans_no, host_no=None):
        """功能：配置业务组HOST
           输入：trans_no（业务组号），host_no（HOST序号）
        """
        self._permissionCheck('clearTransactionHost')
        ss = self.child
        self._enterTransactionView(trans_no)
        if host_no is None:
            ss.sendline('no host-all')
            ss.expect('no host-all\r\n<(.*?)@(.*?) transaction (.*?)>', 5)
            log(0, 'Remove all hosts from transaction %d' % trans_no)
        else:
            ss.sendline('no host %d' % host_no)
            ss.expect('no host %d\r\n<(.*?)@(.*?) transaction (.*?)>'%host_no, 5)
            log(0, 'Remove host %d from transaction %d'%(host_no, trans_no))

    def _getPort(self, name, keyword):
        ss = self.child
        self._enterInterfaceView(name)
        ss.sendline('show current-interface')
        ss.expect('interface detail information(.*?)<(.*?)@(.*?) interface %s>' % name, 5)
        m = re.match(r".*?%s\s+\:\s+(\w+).*?" % keyword, ss.after.replace('\r\n', ''))
        value = m.group(1)
        if keyword in ['link', 'mode', 'fiber', 'type']:
            v = value
        elif keyword in ['input bytes', 'output bytes', 'input packets', 'output packets']:
            v = string.atoi(value)
        return v

    #def _getPorts(self, names, keyword):
    #    ss = self.child
    #    self._enterView('root')
    #    ss.sendline('show interface')

    @timeout
    def getPort(self, port, keyword):
        """功能：获得某端口信息
           输入：port（端口号，Port类的实例），
                 keyword（获取端口的对象关键词，包含'link'/'mode'/'fiber'/'type'/'input bytes'/'output bytes'/'input packets'/'output pacets'）
           输出：获得信息结果
        """
        self._permissionCheck('getPort')
        if keyword in ['link', 'mode', 'fiber', 'type', 'input bytes', 'output bytes', \
                       'input packets', 'output packets']:
            name = port.get()
            ret = self._getPort(name, keyword)
            if isinstance(ret, str):
                log(0, 'Get %s of interface %s: %s' % (keyword, name, ret))
            elif isinstance(ret, int):
                log(0, 'Get %s of interface %s: %d' % (keyword, name, ret))
            else:
                log(2, 'Getting value is unknown')
                raise EXCEPTION(1, 'Get port: getting value is unknown')
        else:
            log(2, 'Unmatched keyword of getting port attribute')
            raise EXCEPTION(1, 'Get port: unmatched keyword of getting port attribute')
        return ret

    @timeout
    def setPort(self, port, keyword, value = None):
        """功能：配置端口
           输入：port（Port类的实例）
                 keyword（配置端口的对象关键词，包含'mode'/'single-fiber'/'type'/'link-protocol'/'crc'/'scramble'/'enable'/'disable'），
                 value（配置值。'single-fiber'：'rx'（单纤接收）、'tx'（单纤发送）、'diable'（双纤模式），'type':'ge'、'10ge'，
                 'link-protocol'：'hdlc'、'ppp'、'self-adaptive', 'crc':'16'、'32'、'self-adaptive'，'scramble':'disable'、
                 'enable'、'self-adaptive'，'enable'：端口使能，值省略，'disable'：端口不使能，值省略）
        """
        self._permissionCheck('setPort')
        if keyword in ['mode', 'single-fiber', 'type', 'link-protocol', 'crc', 'scramble',
                       'enable', 'disable', 'auto-negotiation', 'mtu', 'ip']:
            if type(port) == types.InstanceType: 
                name = port.get()
            elif isinstance(port, str):
                name = port
            ss = self.child
            self._enterInterfaceView(name)
            if keyword == 'single-fiber':
                if value in ['rx', 'tx']:
                    ss.sendline('single-fiber %s' % value)
                    ss.expect('single-fiber %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                    log(0, 'Set port %s single-fiber: %s' % (name, value))
                    self._addRollback('setPort', '\'%s\', \'single-fiber\', \'disable\'' % name)
                elif value == 'disable':
                    ss.sendline('no single-fiber')
                    ss.expect('no single-fiber\r\n<(.*?)@(.*?) interface (.*?)>', 5)
                    log(0, 'Set port %s no single-fiber' % name)
                else:
                    log(2, 'Unmatched value of single-fiber')
                    raise EXCEPTION(1, 'Set port: unmatched value of single-fiber ...')
            if keyword == 'type':
                if value in ['ge', '10ge']:
                    ss.sendline('type %s' % value)
                    ss.expect('type %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                    if value == 'ge':
                        port.type = 'gei'
                    elif value == '10ge':
                        port.type = 'xgei'
                    log(0, 'Set port %s type: %s' % (name, value))
                    self._addRollback('setPort', '\'%s\', \'type\', \'ge\'' % name)
                else:
                    log(2, 'Unmatched value of type')
                    raise EXCEPTION(1, 'Set port: unmatched value of type')
            if keyword == 'link-protocol':
                if value in ['hdlc', 'ppp', 'self-adaptive']:
                    ss.sendline('link-protocol %s' % value)
                    index = ss.expect(['link-protocol %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                    if index == 1:
                        log(2, 'Port %s is not a POS port' % name)
                        raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                    log(0, 'Set port %s link protocol: %s' % (name, value))
                else:
                    log(2, 'Unmatched value of link-protocol')
                    raise EXCEPTION(1, 'Set port: unmatched value of link-protocol')
            if keyword == 'crc':
                if value in ['16', '32', 'self-adaptive']:
                    ss.sendline('crc %s' % value)
                    index = ss.expect(['crc %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                    if index == 1:
                        log(2, 'Port %s is not a POS port' % name)
                        raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                    log(0, 'Set port %s crc: %s' % (name, value))
                else:
                    log(2, 'Unmatched value of crc')
                    raise EXCEPTION(1, 'Set port: unmatched value of crc')
            if keyword == 'scramble':
                if value in ['disable', 'enable', 'self-adaptive']:
                    ss.sendline('scramble %s' % value)
                    index = ss.expect(['scramble %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                    if index == 1:
                        log(2, 'Port %s is not a POS port' % name)
                        raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                    log(0, 'Set port %s scramble: %s' % (name, value))
                else:
                    log(2, 'Unmatched value of scramble')
                    raise EXCEPTION(1, 'Set port: unmatched value of scramble')
            if keyword == 'auto-negotiation':
                if value in ['disable', 'enable']:
                    ss.sendline('auto-negotiation %s' % value)
                    index = ss.expect('auto-negotiation %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                    log(0, 'Set port %s auto-negotiation: %s' % (name, value))
                else:
                    log(2, 'Unmatched value of auto-negotiation')
                    raise EXCEPTION(1, 'Set port: unmatched value of auto-negotiation')
            if keyword == 'mtu':
                ss.sendline('mtu %d' % value)
                index = ss.expect(['mtu %d\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'It is not a front port,you can not configure MTU'], 5)
                if index == 0:
                    log(0, 'Set port %s mtu: %d' % (name, value))
                    self._addRollback('setPort', '\'%s\', \'mtu\', 1518' % name)
                elif index == 1:
                    log(2, 'Set port %s mtu: It is not a front port,you can not configure MTU'%name)
                    raise EXCEPTION(1, 'Set port %s mtu: It is not a front port,you can not configure MTU'%name)
            if keyword == 'ip':
                ss.sendline('ip %s' % value)
                index = ss.expect('ip %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                log(0, 'Set port %s ip: %s' % (name, value))
                m = re.match(r"(.*)\_(\d+)\/(\d+)", name)
		self._addRollback('setPort', "\'%s\', \'ip\', \'192.168.%s.%s\'"%(name, m.group(2), m.group(3)))
            if keyword == 'enable' or keyword == 'disable':
                ss.sendline('%s' % keyword)
                ss.expect('%s\r\n<(.*?)@(.*?) interface (.*?)>' % keyword, 5)
                log(0, 'Port %s is %s' % (name, keyword))
                if keyword == 'disable':
                    self._addRollback('setPort', "\'%s\', \'enable\'"%name)
        else:
            log(2, 'Set port: unmatched keyword of setting port attribute')
            raise EXCEPTION(1, 'Set port: unmatched keyword of setting port attribute')

    def portStable(self, port_list, keyword, timeout=4):
        """功能：等待计数停止
           输入：port_list（Port类的实例列表），keyword（对象计数），timeout（等待时长，时间一到即判断计数已停止，不精确）
        """
        self._permissionCheck('portStable')
        if keyword in ['input bytes', 'output bytes', 'input packets', 'output packets']:
            stable = 0
            interval = 1
            if type(port_list) == types.InstanceType:
                port_list = [port_list]
            port_num = len(port_list)
            log(0, 'Wait until port count is stable')
            for i in range(0, (timeout / interval)):
                temp1 = []
                temp2 = []
                for j in range(0, port_num):
                    temp1.append(self._getPort(port_list[j].get(), keyword))
                for j in range(0, port_num):
                    temp2.append(self._getPort(port_list[j].get(), keyword))
                if temp1 == temp2:
                    stable = 1
                    break
                time.sleep(interval - 0.5)
            if stable == 1:
                pass
            else:
                log(2, 'Port stability judgement timeout')
                raise EXCEPTION(1, 'Port stable: port stability judgement timeout')
        else:
            log(2, 'Unmatched keyword of port attribute')
            raise EXCEPTION(1, 'Port stable: unmatched keyword of port attribute')
    @timeout
    def getRule(self, type, str):
        """获取规则实例。
        """
        dict = {"MplsRule":"MplsRule", "VlanRule":"VlanRule", "Ipv4FlexRule":"Ipv4FlexRule", "Ipv4MaskRule":"Ipv4MaskRule", "Ipv6FlexRule":"Ipv6FlexRule", "Ipv6MaskRule":"Ipv6MaskRule", "Dpi":"Dpi"}
        if type in dict:
            exec("rule = %s()"%dict[type])
            rule.set(str)
            return rule

        else:
            log(2, "Get rule instance: unmatched rule type")
            raise EXCEPTION(1, "Get rule instance: unmatched rule type")

    @timeout
    def _addVlanRule(self, obj, rule_type):
        ss = self.child
        ss.sendline('%s %s' % (rule_type, obj.line()))
        index = ss.expect(['%s %s\r\n<(.*?)@(.*?) acl>' % (rule_type, obj.line()), 
                           'The rule type is not allowed'], 5)
        if index == 0:
            log(0, 'Set vlan rule: %d %d' %
                       (obj.transaction_no, obj.vlan_id))
            self._addRollback('clearRule', '')
        elif index == 1: 
            log(2, 'The rule type is not allowed')
            raise EXCEPTION(2, 'Set vlan rule: the rule type is not allowed')
    
    @timeout
    def _addMplsRule(self, obj, rule_type):
        ss = self.child
        ss.sendline('%s %s' % (rule_type, obj.line()))
        index = ss.expect(['%s %s\r\n<(.*?)@(.*?) acl>' % (rule_type, obj.line()), 
                           'The rule type is not allowed'], 5)
        if index == 0:
            log(0, 'Set mpls rule: %d %d' %
                       (obj.transaction_no, obj.mpls_id))
            self._addRollback('clearRule', '')
        elif index == 1: 
            log(2, 'The rule type is not allowed')
            raise EXCEPTION(2, 'Set mpls rule: the rule type is not allowed')
    
    @timeout
    def _addDpiRule(self, obj):
        ss = self.child
        ss.sendline('dpi %s %s %d %d %d' %
                    (obj.dpi, obj.mdpi, obj.transaction_no, obj.hit_stat, obj.window_start_position))
        index = ss.expect(['dpi %s %s %d %d %d\r\n<(.*?)@(.*?) acl>' %
                           (obj.dpi, obj.mdpi, obj.transaction_no, obj.hit_stat, obj.window_start_position),
                           'Window width beyond range'], 5)
        if index == 0:
            log(0, 'Set dpi rule: %s %s %d %d %d' %
                       (obj.dpi, obj.mdpi, obj.transaction_no, obj.hit_stat, obj.window_start_position))
            self._addRollback('clearRule', '')
        elif index == 1: 
            log(2, 'Set dpi rule: window width beyond range')
            raise EXCEPTION(2, 'Set dpi rule: window width beyond range')

    @timeout
    def _addIpRule(self, obj, rule_type):
        ss = self.child
        ss.sendline('%s %s' % (rule_type, obj.line()))
        index = ss.expect(["%s %s\r\n<(.*?)@(.*?) acl>" % (rule_type, obj.line()), 
                           'Communication between in  management board and the business board is failure', 
                           'config acl-quato first', 
                           'The rule exist', 
                           'The rule type contain port but undefined proto', 
                           'The rule type is not allowed',
                           'The space of rule table is not enough,config acl-quota first*(.*?)<(.*?)>',
                           "Communication between the management board and the business board is failure"], 5)
        if index == 0:
            log(0, 'Set rule: %s %s' %(rule_type, obj.line()))
            self._addRollback('clearRule', '')
        elif index == 1:
            log(2, 'Set %s rule: rules conflicts' % rule_type)
            raise EXCEPTION(1, 'Set %s rule: rules conflicts' % rule_type)
        elif index == 2:
            log(2, 'Set %s rule: acl-quato not enough' % rule_type)
            raise EXCEPTION(2, 'Set %s rule: acl-quato not enough' % rule_type)
        elif index == 3:
            log(1, 'Set %s rule: rule exist' % rule_type)
        elif index == 4:
            log(2, 'Set %s rule: rule type contain port but undefined proto' % rule_type)
            raise EXCEPTION(2, 'Set %s rule: rule type contain port but undefined proto' % rule_type)
        elif index == 5:
            log(2, "Set %s rule: the rule type is not allowed" % rule_type)
            raise EXCEPTION(2, 'Set %s rule: the rule type is not allowed' % rule_type)
        elif index == 6:
            log(2, 'Set %s rule: space of rule table is not enough,config acl-quota first' % rule_type)
            raise EXCEPTION(2, 'Set %s rule: space of rule table is not enough,config acl-quota first' % rule_type)
        elif index == 7:
            log(2, "Set %s rule: Communication between the management board and the business board is failure" % rule_type)
            raise EXCEPTION(2, "Set %s rule: Communication between the management board and the business board is failure" % rule_type)

    def addRule(self, rule_list):
        """功能：加载规则
           输入：rule_list（各种规则类的实例列表）
        """
        self._permissionCheck('addRule')
        self._enterView('acl')
        #for i in range(0, len(rule_list)):
        #    obj = rule_list[i]
        for obj in rule_list:
            name = obj.__class__.__name__
            d = {'MplsRule':'mpls', 'VlanRule':'vlan', 'Ipv4FlexRule':'ipv4-flexible-extend', 'Ipv6FlexRule':'ipv6-flexible-extend', \
                 'Ipv4MaskRule':'ipv4-mask-extend', 'Ipv6MaskRule':'ipv6-mask-extend', "DpiRule":"dpi"}
            if name == 'DpiRule':
                self._addDpiRule(obj)
            elif name == 'VlanRule':
                self._addVlanRule(obj, d[name])
            elif name == 'MplsRule':
                self._addMplsRule(obj, d[name])
            else:
                self._addIpRule(obj, d[name])

    @timeout
    def clearRule(self, rule_list=['all']):
        """功能：删除规则
          输入：rule_list（待删规则实例的列表，缺省为全删）
        """
        self._permissionCheck('clearRule')
        ss = self.child
        self._enterView('acl')
        if rule_list == ['all']:
            ss.sendline('no all')
            ss.expect('no all(.*?)rule number:(.*?)<(.*?)@(.*?) acl>', 2000)
            log(0, 'Clear all rules')
        else:
            pass

    @timeout
    def dpiMatch(self, layer): 
        """功能：设置DPI匹配层数
           输入：layer（层数）
        """
        self._permissionCheck('dpiMatch')
        ss = self.child
        self._enterView('acl')
        ss.sendline('dpi-match %d' % layer)
        ss.expect('dpi-match %d\r\n<(.*?)@(.*?) acl>' % layer, 5)
        log(0, 'Set dpi-match: %d layer' % layer)

    @timeout
    def clearTransactionRule(self, type, trans_no=None):
        """功能：删除某业务组相关的规则
           输入：type（待删除的规则类型，如'dpi'），trans_no（业务组号）
           输出：已删除的规则数量
        """
        self._permissionCheck('clearTransactionRule')
        if type in ['ipv4-flexible', 'ipv6-flexible', 'ipv4-mask', 'ipv6-mask', 'dpi']:
            ss = self.child
            self._enterView('acl')
            if trans_no == None:
                trans_no = ''
            else:
                trans_no = ' %d' % trans_no
            ss.sendline('no %s-all%s' % (type, trans_no))
            ss.expect('no %s-all%s(.*?)rule number:(.*?)<(.*?)@(.*?) acl>' % (type, trans_no), 2)
            ack = self._strip(ss.after)
            ret = string.atoi(ack[ack.index('rule number') + 1])
            log(0, 'Clear %s rules of transaction%s: %d' % (type, trans_no, ret))
        else:
            log(2, 'Clear transaction rule: unmatched type of clearing transaction rules')
            raise EXCEPTION(1, 'Clear transaction rule: unmatched type of clearing transaction rules')
        return ret
        
    def _getSumHit(self, trans_no, keyword):
        """获取某业务组的规则数/命中计数
           输入：trans_no（业务组号），keyword（对象关键字，包含'rule'/'hit'）
           输出：获取结果，int型整数
        """
        if keyword in ['rule', 'hit']:
            ss = self.child
            self._enterView('acl')
            ss.sendline('show sum-hit %d' % trans_no)
            ss.expect('show sum-hit %d\r\n(.*?)<(.*?)@(.*?) acl>' % trans_no, 5)
            lst = ss.after.split()
            ret = string.atoi(lst[lst.index(keyword) + 3])
            log(0, 'Get %s sum of transaction %d: %d' % (keyword, trans_no, ret))
        else:
            log(2, 'Unmatched keyword of getting sum hit')
            raise EXCEPTION(1, 'Get rule sum: unmatched keyword of getting sum hit')
        return ret

    @timeout
    def getTransactionRule(self, trans_no):
        """获取某业务组的规则数
           输入：trans_no（业务组号）
           输出：获取结果，int型整数
        """
        self._permissionCheck('getTransactionRule')
        return self._getSumHit(trans_no, 'rule')

    @timeout
    def getTransactionHit(self, trans_no):
        """获取某业务组的命中计数
           输入：trans_no（业务组号）
           输出：获取结果，int型整数
        """
        self._permissionCheck('getTransactionHit')
        return self._getSumHit(trans_no, 'hit')

    @timeout
    def getRuleHit(self, rule):
        """获取某条规则的命中计数
           输入：rule（规则实例）
           输出：int型整数
        """
        self._permissionCheck('getRuleHit')
        ss = self.child
        self._enterView('acl')
        name = rule.__class__.__name__
        d = {'MplsRule':'mpls', 'VlanRule':'vlan', 'Ipv4FlexRule':'ipv4-flexible', 'Ipv6FlexRule':'ipv6-flexible', 'Ipv4FlexExtRule':'ipv4-flexible-extend',\
             'Ipv6FlexExtRule':'ipv6-flexible-extend', 'Ipv4MaskRule':'ipv4-mask', 'Ipv6MaskRule':'ipv6-mask',\
             'Ipv4MaskExtRule':'ipv4-mask-extend', 'Ipv6MaskExtRule':'ipv6-mask-extend', 'DpiRule':'dpi'}
        ss.sendline('show %s %s' % (d[name], rule.lineForShow()))
        index = ss.expect(['show %s %s(.*?)Hit-number(.*?)<(.*?)@(.*?) acl>'%(d[name], rule.lineForShow()), "show %s %s\r\n<(.*?)@(.*?) acl>"%(d[name], rule.lineForShow)], 10)
        if index == 0:
            ack = ss.after.split()
            hit = string.atoi(ack[ack.index("Hit-number") + 5])
            log(0, 'Get hit of rule(%s %s): %d' % (d[name], rule.lineForShow(), hit))
            return hit
        elif index == 1:
            log(2, "Get rule hit: no this rule")
            raise EXCEPTION(1, "Get rule hit: no this rule")

    @timeout
    def clearHit(self, type=None):
        """清除命中计数
           输入：
        """
        self._permissionCheck('clearHit')
        ss = self.child
        self._enterView('acl')
        if type in ['ipv4-flexible', 'ipv4-mask', 'ipv6-flexible', 'ipv6-mask', 'dpi']:
            ss.sendline('clear hit %s-all' % type)
            ss.expect('clear hit %s-all\r\n<(.*?)@(.*?) (.*?)>' % type, 10)
            log(0, 'Clear hit: %s' % type) 
        elif type == None:
            ss.sendline('clear hit all')
            index = ss.expect(['clear hit all\r\n<(.*?)@(.*?) (.*?)>', 'Communication between the management board and the business board is failure'],10)
            if index == 0:
                log(0, 'Clear hit: all')
            elif index == 1:
                log(2, 'clear hit all: Communication between the management board and the business board is failure')
                raise EXCEPTION(1, "ommunication between the management board and the business board is failure")

    @timeout
    def setTransactionPriority(self, service):
        """功能：设置业务优先级
           输入：service（待设置的优先业务，包含'discard'/'reflow'）
        """
        self._permissionCheck('setTransactionPriority')
        ss = self.child
        self._enterView('service')
        if service in ['discard', 'reflow']:
            ss.sendline('transaction-priority %s' % service)
            ss.expect('transaction-priority %s\r\n<(.*?)@(.*?) (.*?)>' % service, 5)
            log(0, 'Set transaction priority: %s' % service)
            if service == 'reflow':
                self._addRollback('setTransactionPriority', '\'discard\'')
        else:
            log(2, 'Set transaction priority: Unmatched service')
            raise EXCEPTION(2, 'Set transaction priority: Unmatched service')

    @timeout
    def setIpInIpGlobal(self, mode):
        """功能：设置全局ip-in-ip模式
           输入：mode（匹配模式，包含'inner'/'outer'/'pass-through'）
        """
        self._permissionCheck('setIpInIpGlobal')
        ss = self.child
        self._enterView('service')
        if mode in ['inner', 'outer', 'pass-through']:
            ss.sendline('ip-in-ip %s' % mode)
            ss.expect('ip-in-ip %s\r\n<(.*?)@(.*?) (.*?)>' % mode, 5)
            log(0, 'Set global ip-in-ip: %s' % mode)
            if mode != "inner":
                self._addRollback('setIpInIpGlobal', '\'inner\'')
        else:
            log(2, 'Set global ip-in-ip: Unmatched mode')
            raise EXCEPTION(2, 'Set global ip-in-ip: Unmatched mode')

    @timeout
    def setIpInIpPacketType(self, mode, type):
        """功能：设置各类隧道报文的ip-in-ip模式
           输入：mode（匹配模式，包含'inner-packet'/'outer-packet'/'pass-through-packet'/'default'）
                 type（隧道报文类型，包含grev0|grev1|gtpv0|gtpv1|ipv4inipv4|ipv4inipv6|ipv6inipv4|ipv6inipv6|l2tpv2|teredo|ipsec-ah|ipsec-esp|min-ip|pptp）
        """
        self._permissionCheck('setIpInIpPacketType')
        ss = self.child
        self._enterView('service')
        if mode in ['inner-packet','outer-packet','pass-through-packet','default'] and \
           type in ['grev0','grev1','gtpv0','gtpv1','ipv4inipv4','ipv4inipv6','ipv6inipv4','ipv6inipv6','l2tpv2','teredo','ipsec-ah','ipsec-esp',"ah-esp",'min-ip','pptp']:
            ss.sendline('ip-in-ip %s %s'%(mode,type))
            ss.expect('ip-in-ip %s %s\r\n<(.*?)@(.*?) (.*?)>'%(mode,type), 5)
            log(0, 'Set packet type ip-in-ip: %s %s'%(mode,type))
            if mode != "default":
                self._addRollback('setIpInIpPacketType', '\'default\',\'%s\''%type)
        else:
            log(2, 'Set packet type ip-in-ip: Unmatched mode')
            raise EXCEPTION(2, 'Set packet type ip-in-ip: Unmatched mode')

    @timeout
    def setIpInIpGlobalHash(self, mode):
        """功能：设置全局ip-in-ip哈希
           输入：mode（匹配模式，包含'inner'/'outer'）
        """
        self._permissionCheck('setIpInIpGlobalHash')
        ss = self.child
        self._enterView('service')
        if mode in ['inner', 'outer']:
            ss.sendline('ip-in-ip hash %s' % mode)
            ss.expect('ip-in-ip hash %s\r\n<(.*?)@(.*?) (.*?)>' % mode, 5)
            log(0, 'Set global ip-in-ip hash: %s' % mode)
            if mode != "outer":
                self._addRollback('setIpInIpGlobal', '\'outer\'')
        else:
            log(2, 'Set global ip-in-ip hash: Unmatched mode')
            raise EXCEPTION(2, 'Set global ip-in-ip hash: Unmatched mode')

    @timeout
    def setLinkProtection(self, opb_slot_no, module_no, keyword, value=None, rollback=False):
        """功能：设置链路保护
           输入：opb_slot_no（光保护板槽位号），module_no（模块号），
                 keyword（设置对象，包含'electric-protection'/'optical-protection'/'link-partner'/'no link-partner'），
                 value（设置值，'electric-protection'/'optical-protection'：'bypass'/'interdict'，'link-partner'：Port类实例的列表，'no link-partner'：可省略）
        """
        self._permissionCheck('setLinkProtection')
        ss = self.child
        if keyword in ['electric-protection', 'optical-protection', 'link-partner', 'no link-partner']:
            self._enterLinkProtectionView(opb_slot_no, module_no)
            if keyword in ['electric-protection', 'optical-protection']:
                if value in ['bypass', 'interdict']:
                    ss.sendline('%s %s' % (keyword, value))
                    ss.expect('%s %s\r\n<(.*?)@(.*?) link-protection (.*?)>' % (keyword, value))
                    log(0, 'Set link-protection %s/%s: %s %s' % (opb_slot_no, module_no, keyword, value))
                    if rollback == False:
                        if keyword == 'optical-protection':
                            mode = 'bypass'
                        else:
                            mode = 'interdict'
            elif keyword == 'link-partner':
                if isinstance(value, list) and len(value) == 2 and type(value[0]) == types.InstanceType and type(value[1]) == types.InstanceType:
                    ss.sendline('link-partner %s %s' % (value[0].get(), value[1].get()))
                    ss.expect('link-partner %s %s\r\n<(.*?)@(.*?) link-protection (.*?)>' % (value[0].get(), value[1].get()))
                    log(0, 'Set link-protection: link-partner %s %s' % (value[0].get(), value[1].get()))
                else:
                    log(2, 'Set link partner of link-protection: Unmatched value')
                    raise EXCEPTION(2, 'Set link partner of link-protection: Unmatched value')
            elif keyword == 'no link-partner':
                ss.sendline('no link-partner')
                ss.expect('no link-partner\r\n<(.*?)@(.*?) link-protection (.*?)>')
                log(0, 'Set link-protection: link-protection clear') 
        else:
            log(2, 'Unmatched keyword of setting transaction attribute')
            raise EXCEPTION(1, 'Set group: unmatched keyword')

    @timeout
    def setAclQuota(self, trans_no, type, num):
        """功能：设置规则容量
           输入：trans_no（业务组号），type（规则类型，'ipv4-mask'/'ipv6-mask'/'ipv4-flexible'/'ipv6-flexible'/'dpi'），num（容量大小）
        """
        self._permissionCheck('setAclQuota')
        ss = self.child
        self._enterView('system')
        if type in ['ipv4-mask', 'ipv6-mask', 'ipv4-flexible', 'ipv6-flexible', 'dpi']:
            ss.sendline('acl-quota %d %s %d' % (trans_no, type, num))
            index = ss.expect(["acl-quota %d %s %d\r\n<(.*?)@(.*?) (.*?)>" % (trans_no, type, num), "Rules exist,you can not configure, please delete rules"], 5)
            if index == 0:
                log(0, 'Set acl-quota of transaction %d %s: %d' % (trans_no, type, num))
            elif index == 1:
                log(2, "(setAclQuota) Rules exist,you can not configure, please delete rules")
                raise EXCEPTION(1, "(setAclQuota) Rules exist,you can not configure, please delete rules")
        else:
            log(2, 'Set acl-quota: Unmatched rule type')
            raise EXCEPTION(2, 'Set acl-quota: Unmatched rule type')

    @timeout
    def setKeepAliveProtocol(self, proto):
        """功能：设置后端保活协议
           输入：proto（协议）
        """
        self._permissionCheck("setKeepAliveProtocol")
        ss = self.child
        self._enterView("system")
        if proto in ["arp", "icmp", "bfd"]:
            ss.sendline("keep-alive-protocol %s"%proto)
            index = ss.expect(["keep-alive-protocol %s\r\n<(.*?)@(.*?) (.*?)>"%proto], 5)
            if index == 0:
                log(0, "Set keep alive protocol: %s"%proto)
                if proto != "icmp":
                    self._addRollback("setKeepAliveProtocol", "\'icmp\'")
        else:
            log(2, "(setKeepAliveProtocol) Unmatched protocol type")
            raise EXCEPTION(2, "(setKeepAliveProtocol) Unmatched protocol type")

    @timeout
    def setKeepAliveInterval(self, time):
        """功能：设置后端保活探测间隔
           输入：time（间隔时间，ms）
        """
        self._permissionCheck("setKeepAliveInterval")
        ss = self.child
        self._enterView("system")
        if 10<time<3600000:
            ss.sendline("keep-alive-interval %d"%time)
            index = ss.expect(["keep-alive-interval %d\r\n<(.*?)@(.*?) (.*?)>"%time], 5)
            if index == 0:
                log(0, "Set keep alive interval: %d"%time)
                if time != 300:
                    self._addRollback("setKeepAliveInterval", "300")
        else:
            log(2, "(setKeepAliveInterval) Unmatched interval range")
            raise EXCEPTION(2, "(setKeepAliveProtocol) Unmatched interval range")

    @timeout
    def setIp(self, ip, netmask):
        """功能：设置设备后端ip
           输入：ip（ip地址），netmask（子网掩码）
        """
        self._permissionCheck('setIp')
        ss = self.child
        self._enterView('system')
        ss.sendline('ip %s %s' % (ip, netmask))
        index = ss.expect(['ip %s %s\r\n<(.*?)@(.*?) (.*?)>' % (ip, netmask), 'The keep-alive source ip is conflict'], 5)
        if index == 0 or index == 1:
            log(0, 'Set ip: %s/%s' % (ip, netmask))
        self._addRollback('removeIp', '\'%s\', \'%s\'' % (ip, netmask))

    @timeout
    def removeIp(self, ip, netmask):
        """功能：移除设备后端ip
           输入：ip（ip地址），netmask（子网掩码）
        """
        self._permissionCheck('removeIp')
        ss = self.child
        self._enterView('system')
        ss.sendline('no ip %s %s' % (ip, netmask))
        ss.expect('no ip %s %s\r\n<(.*?)@(.*?) (.*?)>' % (ip, netmask), 5)
        log(0, 'Remove ip: %s/%s' % (ip, netmask))

    @timeout
    def setPortIp(self, port_list):
        """功能：设置lan口ip
           输入：port_list（端口实例列表）
        """
        self._permissionCheck("setPortIp")
        ss = self.child
        for port in port_list:
            port_name = port.get()
            ip = port.ip
            self._enterView("interface %s"%port_name)
            ss.sendline("ip %s"%ip)
            index = ss.expect(["ip %s\r\n<(.*?)@(.*?) (.*?)>"%ip], 5)
            if index == 0:
                log(0, 'Set interface %s ip: %s'%(port_name, ip))

    @timeout
    def setTransactionAgeTime(self, trans_no, time):
        """功能：配置业务组规则老化时间
           输入：trans_no（业务组号），time（老化时间）
        """
        self._permissionCheck('setTransactionAgeTime')
        ss = self.child
        if 0<=time<=65535:
            self._enterTransactionView(trans_no)
            ss.sendline('age-time %d'%time)
            index = ss.expect(['age-time %d\r\n<(.*?)@(.*?) transaction (.*?)>'%time], 5)
            if index == 0:
                log(0, 'Set transaction %d age-time: %d' % (trans_no, time))
                self._addRollback('setTransactionAgeTime', '%d, 0'%trans_no)
        else:
            log(2, 'Set transaction age-time: unmatched time')
            raise EXCEPTION(1, 'Set transaction age-time: unmatched time')

    @timeout
    def setAccurateCount(self, state):
        """功能：配置精确计数
           输入：state（'disable' or 'enable'）
        """
        self._permissionCheck('setAccurateCount')
        ss = self.child
        self._enterView('debug')
        if state is 'enable':
            ss.sendline('accurate-count')
            index = ss.expect(['accurate-count\r\n<(.*?)@(.*?) debug>'], 5)
            if index == 0:
                log(0, 'Set accurate-count: enable')
                self._addRollback('setAccurateCount', '\'disable\'')
        elif state is 'disable':
            ss.sendline('no accurate-count')
            index = ss.expect(['no accurate-count\r\n<(.*?)@(.*?) debug>'], 5)
            if index == 0:
                log(0, 'Set accurate-count: disable')
        else:
            log(2, 'Set accurate-count: unmatched para')
            raise EXCEPTION(1, 'Set accurate-count: unmatched para')
