#coding=utf-8
"""CLI控制模块,为各个设备的CLI专用模块提供超类"""

import pexpect
import types
import sys, os

from test_station.logging.logger import log,log_fake
from test_station.err import EXCEPTION
#from test_station.libserv.serv import sshLogin 
from test_station.resource import Resource
from test_station import gl


def timeout(fn):
    """为CLI类中的方法提供超时装饰器"""
    def wraped(*argv, **kwgs):
        try:
            return fn(*argv, **kwgs)
        except pexpect.TIMEOUT:
            log(2, "(%s) timeout"%fn.__name__)
            raise EXCEPTION(1, "(%s) timeout"%fn.__name__)
    return wraped


class Rollback():
    def __init__(self):
        self.func_name = None #函数名
        self.parr = [] #参数列表

    def run(self):
        pass


class Cli(Resource):
    """CLI超类，其中包括必要的成员变量和几个设备CLI相重合的功能"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "flowfirm_cli")
        self.child = None
        self.state = 0
        self.cur_view = None
        self.rollbacking = False
        self.rollback_stack = []
        self.is_login = False
        self.__parse(node)
        
        if self.user != 'debug':
            self._addRollback('clearPort', '')
        
    def __parse(self, node):
        self.type = node.findtext("type")
        self.remote_ip = node.findtext('remote_ip')
        self.remote_passwd = node.findtext('remote_passwd')
        self.user = node.findtext('user')
        self.passwd = node.findtext('passwd')

    def release(self):
        log(0, "-- (%s) Release start --"%self.kind)
        if self.is_login:
            self._logout()

    def rollback(self):
        """开始回滚命令"""
        if self.state > 1:
            self.rollbacking = True
            log(0, "-- (%s) Rollback start --"%self.kind)
            while(self.rollback_stack != []):
                method = self.rollback_stack.pop()
                exec('self.%s(%s)' % (method[0], method[1]))

    def _addRollback(self, method_name, arg):
        """将新的回滚命令加进回滚队列中"""
        if self.rollbacking == False:
            for method in self.rollback_stack:
                if method_name == method[0] and arg == method[1]:
                    return 1
            self.rollback_stack.append([method_name, arg])
            return 0

    def _permissionCheck(self, func_name):
        if func_name not in self.permission[self.user]:
            log(2, "User permission of %s(): error"%func_name)
            raise EXCEPTION(1, "User permission of %s(): error"%func_name)    

    def _remoteLogin(self):
        """登陆设备shell命令行"""
        try:
            ss = pexpect.spawn('ssh root@%s' % self.remote_ip)
            self.child = ss
            index = ss.expect(['yes/no', 'Host key verification failed', 'please input your name:'], 10)
            if index == 0:
                ss.sendline('yes')
                ss.expect(['please input your name:'], 10)
                pass
            elif index == 1:
                log(2, 'Host key verification failed')
                raise EXCEPTION(2, 'Remote login: host key verification failed')
                return ss
            elif index == 2:
                pass
        except pexpect.TIMEOUT:
            log(2, 'Remote login: time out')
            raise EXCEPTION(2, 'Login remote: time out')
            return ss
        self.state += 1
        log(0, 'Login CLI(%s)'%self.remote_ip)
        self.cur_view = 'auth'
          
    def _remoteLogout(self):
        """从设备shell命令行退出"""
        ss = self.child
        ss.sendline('logout')
        self.state -= 1
        log(0, 'Logout from %s' % self.remote_ip)

    @timeout
    def _userAuth(self, name, passwd): 
        """用户验证"""
        ss = self.child
        ss.sendline(name)
        ss.expect('please input your password:', 5)
        ss.sendline(self.passwd)
        index = ss.expect(['<%s@(.*?)>' % name, 'the password is error', 'the username does not exist', 
                          'The number of (.*?) connections exceeds the maximum number of connections', ' Device connection failure'], 5)
        if index == 0:
            self.state += 1
            self.cur_view = 'root'
            log(0, 'Login CLI(%s)' % name) 
        elif index == 1:
            log(2, 'Login CLI: The password is error')
            raise EXCEPTION(2, 'Login CLI: password error')
        elif index == 2:
            log(2, 'Login CLI: The username does not exist')
            raise EXCEPTION(2, 'Login CLI: the username does not exist')
        elif index == 3:
            log(2, 'Login CLI: too many connections')
            raise EXCEPTION(2, 'Login CLI: too many connections')
        elif index == 4:
            log(2, 'Login CLI: device connection failure')
            raise EXCEPTION(2, 'Login CLI: device connection failure')        

    @timeout 
    def _cliLogout(self):
        """注销CLI"""
        ss = self.child
        ss.sendline('logout')
        self.state -= 1
        self.cur_view = 'shell'

    def _logout(self):
        """全部注销退出"""
        ss = self.child
        if self.state == 3:
            self._exitView()

        if self.state == 2:
            self._cliLogout()
        
        log_fake(0, 'Logout CLI(%s)' % self.user)
        
        ss.close()

    def _strip(self, input):
        """提取关键数据"""
        temp = input.replace('\r\n', '  ')
        temp = temp.replace(':', '')
        temp = temp.replace('------------------------------------------------------------', '')
        temp = temp.split('  ')
        while '' in temp:
            temp.remove('')
        i = 0
        for x in temp:
            temp[i] = x.strip()
            i+=1
        return temp

    @timeout
    def _enterView(self, view_name):
        """进入某视图"""
        if view_name != self.cur_view: 
            if view_name == 'root':
                self._exitView()
            else:
                ss = self.child
                try_time = 2
                for i in range(0, try_time):
                    ss.sendline(view_name)
                    index = ss.expect(['%s\r\n<(.*?)@(.*?) (.*?)>' % view_name, ' Device connection failure'], 5)
                    if index == 0:
                        if self.cur_view == 'root':
                            self.state += 1
                        self.cur_view = view_name
                        break
                    elif index == 1:
                        log(1, 'Enter %s view: device connection failure, try again')
                if i > try_time - 1:
                    log(2, 'Enter %s view: device connection failure')
                    raise EXCEPTION(2, 'Enter %s view: device connection failure')

    @timeout
    def _exitView(self):
        """退出视图"""
        ss = self.child
        ss.sendline('exit')
        index = ss.expect(['exit\r\n<(.*?)@(.*?)>', ' Device connection failure'], 5)
        if index == 0:
            pass
        elif index == 1:
            log(1, "Exit view: device connection failure, but don't need to try again")
        self.state -= 1
        self.cur_view = 'root'

    @timeout
    def _enterInterfaceView(self, port_name):
        """进入端口视图"""
        if 'interface %s' % port_name != self.cur_view:
            ss = self.child
            ss.sendline('interface %s' % port_name)
            index = ss.expect(['interface %s\r\n<(.*?)@(.*?) interface (.*?)>' % port_name,\
                              'The interface name is'], 5)
            if index == 0:
                if self.cur_view == 'root':
                    self.state += 1
                self.cur_view = 'interface %s' % port_name
            elif index == 1:
                log(2, 'Unmatched port name')
                raise EXCEPTION(1, 'Enter interface view: unmatched port name')

    @timeout
    def restore(self):
        """功能：恢复出厂设置"""
        self._permissionCheck('restore')
        ss = self.child
        log(0, 'Restore system')
        self._enterView('system')
        ss.sendline('restore')
        ss.expect('restore\r\n<(.*?)@(.*?) system>', 5)
        for i in range(0, 50):
            time.sleep(1)
            ss.sendline('show group')
            index1 = ss.expect(['Device connection failure', 'Error:  Device is busy', 'show group\r\n<(.*?)@(.*?)>'], 5)
            if index1 == 0 or index1 == 1:
                continue
            ss.sendline('acl')
            index2 = ss.expect(['Device connection failure', 'Error:  Error code = 6!', 'acl\r\n<(.*?)@(.*?) acl>'], 5)
            if index2 == 0 or index2 == 1:
                continue
            elif index1 == 2 and index2 == 2:
                break
        if i >= 49:
            raise EXCEPTION(2, 'Restore: failed')

    @timeout
    def setHeaderStrip(self, state, type=None):
        """功能：设置报文头剥离
           输入：state（剥离使能，enable为剥离，disable为取消剥离），type（剥离类型，包括'all'/'ip'/'mpls'/'vlan'，state为disable时可缺省）
        """
        self._permissionCheck('setHeaderStrip')
        ss = self.child
        self._enterView('service')
        if state == 'enable' and type in ['all', 'ip', 'mpls', 'vlan']:
            ss.sendline('packet-out header-strip %s' % type)
            ss.expect('packet-out header-strip %s\r\n<(.*?)@(.*?) service>' % type, 5)
            log(0, 'Set header strip enable: %s' % type)
            self._addRollback('setHeaderStrip', '\'disable\'')
        elif state == 'disable':
            ss.sendline('no packet-out header-strip')
            ss.expect('no packet-out header-strip\r\n<(.*?)@(.*?) service>', 5)
            log(0, 'Set header strip disable')
        else:
            log(2, 'Unmatched state or type of setting header strip')
            raise EXCEPTION(1, 'Set header strip: Unmatched state or type of setting header strip...')

    @timeout
    def setInfoCarry(self, state):
        """功能：设置信息携带
           输入：state（设置使能，enable为设置，disable为取消）
        """
        self._permissionCheck('setInfoCarry')
        ss = self.child
        self._enterView('service')
        if state == 'enable':
            ss.sendline('packet-out info-carry')
            ss.expect('packet-out info-carry\r\n<(.*?)@(.*?) service>', 5)
            log(0, 'Set info carry: enable')
            self._addRollback('setInfoCarry', '\'disable\'')
        elif state == 'disable':
            ss.sendline('no packet-out info-carry')
            ss.expect('no packet-out info-carry\r\n<(.*?)@(.*?) service>', 5)
            log(0, 'Set info carry: disable')
        else:
            log(2, 'Set info carry: unmatched state of setting information carry')
            raise EXCEPTION(1, 'Set info carry: unmatched state of setting information carry')

    @timeout
    def setFragmentAge(self, time):
        """功能：设置分片老化时间"""
        self._permissionCheck('setFragmentAge')
        ss = self.child
        if 10<=time<=2000:
            self._enterView('service')
            ss.sendline('fragment-age %d'%time)
            ss.expect('fragment-age %d\r\n<(.*?)@(.*?) service>'%time, 5)
            log(0, 'Set fragment age: %d'%time)
            if time != 2000:
                self._addRollback('setFragmentAge', '2000')
        else:
            log(2, 'Set fragment age: out of age range')
            raise EXCEPTION(1, 'Set fragment age: out of age range')

    @timeout
    def setFragmentCache(self, cache):
        """功能：设置分片缓存容量"""
        self._permissionCheck('setFragmentCache')
        ss = self.child
        if 0<=cache<=32:
            self._enterView('service')
            ss.sendline('fragment-cache %d'%cache)
            ss.expect('fragment-cache %d\r\n<(.*?)@(.*?) service>'%cache, 5)
            log(0, 'Set fragment cache: %d'%cache)
            if cache != 32:
                self._addRollback('setFragmentCache', '32')
        else:
            log(2, 'Set fragment cache: out of cache range')
            raise EXCEPTION(1, 'Set fragment cache: out of cache range')

    @timeout
    def clearFragmentTable(self):
        """功能：清除分片缓存"""
        self._permissionCheck('setInfoCarry')
        ss = self.child
        self._enterView('service')
        ss.sendline('fragment-reset')
        ss.expect('fragment-reset\r\n<(.*?)@(.*?) service>', 5)
        log(0, 'Clear fragment table')

    @timeout
    def clearPort(self, port_list=[]):
        """功能：清除端口计数
           输入：port_list（端口列表，端口为Port类的实例；缺省为空列表，代表全清）
        """
        self._permissionCheck('clearPort')
        ss = self.child
        if port_list == []:
            self._enterView('root')
            ss.sendline('clear interface-all')
            ss.expect('clear interface-all\r\n<(.*?)@(.*?)>', 5)
            log(0, 'Clear interface all')
        else:
            for port in port_list:
                port_name = port.get()
                self._enterInterfaceView(port_name)
                ss.sendline('clear interface %s' % port_name)
                ss.expect('clear interface %s\r\n<(.*?)@(.*?) interface (.*?)>' % port_name, 5)
                log(0, 'Clear interface %s' % port_name)

    @timeout
    def setRcpPermitIp(self, ip):
        """功能：设置RCP允许IP
           输入：ip（被允许的IP）
        """
        self._permissionCheck('setRcpPermitIp')
        ss = self.child
        self._enterView('rcp')
        ss.sendline('permit %s' % ip) 
        ss.expect('permit %s\r\n<(.*?)@(.*?) rcp>' % ip, 5)
        log(0, 'Set rcp permit ip: %s' % ip)

    @timeout
    def reset(self, board_no):
        """功能：重启板卡
           输入：board_no（板卡槽位号，1到14）
        """
        self._permissionCheck('reset')
        if 0 < board_no < 15:
            ss = self.child
            self._enterView('hardware')
            ss.sendline('reset linecard %d' % board_no)
            ss.expect('(yes or no) :', 5)
            ss.sendline('yes')
            ss.expect('yes\r\n(.*?)<(.*?)@(.*?) hardware>', 5)
            log(0, 'Reset linecard %d' % board_no)
        else:
            log(2, 'Wrong linecard number: %d' % board_no)
            raise EXCEPTION(2, 'Wrong linecard number: %d' % board_no)

    def getCount(self, port_list, keyword):
        """功能：收集端口计数并保存
        """
        if type(port_list) == types.InstanceType:
            port_list = [port_list]
        lst = []
        for port in port_list:
            count = self.getPort(port, keyword)
            lst.append(count)
        return lst
