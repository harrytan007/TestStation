#coding=utf-8
from cli import *

# Some as a struct of rule config
class Ipv4Rule:
    def __init__(self):
        self.sip = '0.0.0.0'
        self.sip_mask = '0.0.0.0'
        self.dip = '0.0.0.0'
        self.dip_mask = '0.0.0.0'
        self.sport = 0
        self.sport_mask = 0
        self.dport = 0
        self.dport_mask = 0
        self.protocol = 0
        self.protocol_mask = 0
        self.group_no = 0
        self.action = 1
        self.reboot_save = 1
        self.hit_stat = 1
        self.mask_flag = 1
        self.rule_id = 0
        self.relation_rule = '0xffffffff'

class Ipv6Rule:
    def __init__(self):
        self.sip = '0::0'
        self.sip_mask = '0::0'
        self.dip = '0::0'
        self.dip_mask = '0::0'
        self.sport = 0
        self.sport_mask = 0
        self.dport = 0
        self.dport_mask = 0
        self.protocol = 0
        self.protocol_mask = 0
        self.group_no = 0
        self.action = 1
        self.reboot_save = 1
        self.hit_stat = 1
        self.mask_flag = 1
        self.rule_id = 0
        self.relation_rule = '0xffffffff'

class DpiRule:
    def __init__(self):
        self.dpi = '000000'
        self.mdpi = '000000'
        self.group_no = 0
        self.action = 1
        self.reboot_save = 1
        self.hit_stat = 1
        self.combined_rule = 0
        self.rule_id = 0
        self.window_num = 0
        self.window_width = 0
        self.window_start_position = 0

class TcpFlagRule:
    def __init__(self):
        self.urg = 0
        self.ack = 0
        self.psh = 0
        self.rst = 0
        self.syn = 0
        self.fin = 0
        self.length = 0
        self.action = 0
        self.if_group_no = 0
        self.rule_id = 0
       
class CliS(Cli):
    def __init__(self, ip, remote_passwd, user, passwd):
        Cli.__init__(self, ip, remote_passwd, user, passwd)

    def __del__(self):
        Cli.__del__(self)

    # Login device
    def login(self):
        self._remote_login()
        self._cli_login('/usr/share/flowfirm/bin')
        if self.user == 'admin':
            self._enter_no_password()

    def _enter_no_password(self):
        try:
            ss = self.child
            self._enter_view('debug')
            ss.sendline('enter-no-password')
            ss.expect('enter-no-password\r\n<(.*?)@(.*?) debug>', 5)
        except pexpect.TIMEOUT:
            log.log(2, 'Set entering without password: time out...')
            raise EXCEPTION(2, 'Set entering without password: time out')

    def _enter_group_view(self, user, group_no):
        try:
            ss = self.child
            ss.sendline('group %s %d' % (user, group_no))
            ss.expect('group (.*?) (.*?)\r\n<(.*?)@(.*?) group \((.*?):(.*?)\)>', 5)
            self.state += 1
        except pexpect.TIMEOUT:
            log.log(2, 'Enter %s\'s group %d view: time out...' % (user, group_no))
            raise EXCEPTION(2, 'Enter %s\'s group %d view: time out' % (user, group_no))

    def set_default_action(self, forward_type, group_no=1):
        try:
            if forward_type in ['forward', 'no-forward'] and 0 < group_no < 2048:
                ss = self.child
                self._enter_view('service')
                if forward_type == 'forward':
                    ss.sendline('default-action %s %d' % (forward_type, group_no))
                    ss.expect('default-action %s %d\r\n<(.*?)@(.*?) service>' % (forward_type, group_no), 5)
                    log.log(0, 'Set default action: %s -> group %d ...' % (forward_type, group_no))
                elif forward_type == 'no-forward':
                    ss.sendline('default-action %s' % forward_type)
                    ss.expect('default-action %s\r\n<(.*?)@(.*?) service>' % forward_type, 5)
                    log.log(0, 'Set default action: %s' % forward_type)
            else:
                log.log(2, 'Forward type or group number error...')
                raise EXCEPTION(1, 'Set default action: %s' % forward_type)
        except pexpect.TIMEOUT:
            log.log(2, 'Set default %s action: time out...' % forward_type)
            raise EXCEPTION(2, 'Set default %s action: time out' % forward_type)

    def set_unknown_packet(self, type, group_no=None):
        try:
            ss = self.child
            self._enter_view('service')
            if type == 'forward':
                ss.sendline('packet-in unknown-packet forward %d' % group_no)
                ss.expect('packet-in unknown-packet forward %d\r\n<(.*?)@(.*?) service>' % group_no, 5)
                log.log(0, 'Set unknown packet: forward')
            elif type == 'drop':
                ss.sendline('packet-in unknown-packet drop')
                ss.expect('packet-in unknown-packet drop\r\n<(.*?)@(.*?) service>', 5)
                log.log(0, 'Set unknown packet drop...')
            else:
                log.log(2, 'Unmatched type of setting unknown packet...')
                raise EXCEPTION(1, 'Set unknown packet: Unmatched type')
        except pexpect.TIMEOUT:
            log.log(2, 'Set unknown packet: time out...')
            raise EXCEPTION(2, 'Set unknown packet: time out')

    def set_stream_manage_configue(self, state, packet_num=None, ttl_of_tcp=None, ttl_of_udp=None):
        try:
            ss = self.child
            self._enter_view('service')
            if state == 'enable':
                ss.sendline('stream-manage')
                ss.expect('stream-manage\r\n<(.*?)@(.*?) service>', 5)
                if 1 <= packet_num <= 255 and 1 <= ttl_of_tcp <= 600 and 1 <= ttl_of_udp <= 600:
                    ss.sendline('stream-manage configure %d %d %d' % (packet_num, ttl_of_tcp, ttl_of_udp))
                    ss.expect('stream-manage configure %d %d %d\r\n<(.*?)@(.*?) service>' % (packet_num, ttl_of_tcp, ttl_of_udp), 5)
                    log.log(0, 'Set stream-manage configure: packet-num->%d, ttl-of-tcp->%d, ttl-of-udp->%d...' % (packet_num, ttl_of_tcp, ttl_of_udp))
                else:
                    log.log(2, 'Wrong range of values...')
                    raise EXCEPTION(1, 'Set stream manage configure: Wrong range of values')
            elif state == 'disable':
                ss.sendline('no stream-manage')
                ss.expect('no stream-manage\r\n<(.*?)@(.*?) service>', 5)
                log.log(2, 'Set stream manage disable...')
            else:
                log.log(2, 'Unmatched state of stream manage...')
                raise EXCEPTION(1, 'Set stream manage: Unmatched state')
        except pexpect.TIMEOUT:
            log.log(2, 'Set stream manage configure: time out...')
            raise EXCEPTION(2, 'Set stream manage configure: time out')

    def set_stream_manage_group(self, group_no):
        try:
            ss = self.child
            self._enter_view('service')
            ss.sendline('stream-manage group %d' % group_no)
            ss.expect('stream-manage group %d\r\n<(.*?)@(.*?) service>' % group_no, 5)
        except pexpect.TIMEOUT:
            log.log(2, 'Set stream manage group: time out...')
            raise EXCEPTION(2, 'Set stream manage group: time out')

    def set_header_output(self, state, group_no=1):
        try:
            ss = self.child
            self._enter_view('service')
            if state == 'enable':
                ss.sendline('header-output')
                ss.expect('header-output\r\n<(.*?)@(.*?) service>', 5)
                ss.sendline('header-output group %d' % group_no)
                ss.expect('header-output group %d\r\n<(.*?)@(.*?) service>' % group_no, 5)
                log.log(0, 'Set header output enable: group %d', group_no)
            elif state == 'disable':
                ss.sendline('no header-output')
                ss.expect('no header-output\r\n<(.*?)@(.*?) service>', 5)
                ss.sendline('no header-output group')
                ss.expect('no header-output group\r\n<(.*?)@(.*?) service>', 5)
                log.log(0, 'Set header output disable')
            else:
                log.log(2, 'Unmatched state of header output...')
                raise EXCEPTION(1, 'Set header output: Unmatched state')
        except pexpect.TIMEOUT:
            log.log(2, 'Set header output: time out...')
            raise EXCEPTION(2, 'Set header output: time out')

    def set_sample(self, state, group_no=None, period=None, rate=None):
        try:
            ss = self.child
            self._enter_view('service')
            if state == 'enable':
                ss.sendline('sample group %d' % group_no)
                ss.expect('sample group %d\r\n<(.*?)@(.*?) service>' % group_no, 5)
                ss.sendline('sample period %d' % period)
                ss.expect('sample period %d\r\n<(.*?)@(.*?) service>' % period, 5)
                ss.sendline('sample rate %d' % rate)
                ss.expect('sample rate %d\r\n<(.*?)@(.*?) service>' % rate, 5)
                log.log(0, 'Set sample enable: group-no->%d, period->%d, rate->%d' % (group_no, period, rate)) 
            elif state == 'disable':
                ss.sendline('no sample')
                ss.expect('no sample\r\n<(.*?)@(.*?) service>', 5)
                ss.sendline('no sample group')
                ss.expect('no sample group\r\n<(.*?)@(.*?) service>', 5)
                log.log(0, 'Set sample diable')
            else:
                log.log(2, 'Unmatched state of sample...')
                raise EXCEPTION(1, 'Set sample: Unmatched state')
        except pexpect.TIMEOUT:
            log.log(2, 'Set sample: time out...')
            raise EXCEPTION(2, 'Set sample: time out')

    def set_stream_lock(self, type, sip, dip, sport, dport, proto):
        try:
            if type(type) == type(sip) == type(dip) == types.StringType and \
               type(sport) == type(dport) == type(proto) == types.IntType:
                self._enter_view('acl')
                ss = self.child
                ss.sendline('stream-lock %s %s %s %d %d %d' % (type, sip, dip, sport, dport, proto))
                ss.expect('stream-lock %s %s %s %d %d %d\r\n<(.*?)@(.*?) acl>' % (type, sip, dip, sport, dport, proto), 5)
                log.log(0, 'Set stream lock: %s %s %s %d %d %d ...' % (type, sip, dip, sport, dport, proto))
            else:
                log.log(2, 'Set stream lock: type error(string or int) ...')
                raise(1, 'Set stream lock: type error') 
        except pexpect.TIMEOUT:
            log.log(2, 'Set stream lock: time out...')
            raise EXCEPTION(2, 'Set stream lock: time out')

    def set_authorize(self, username, mode):
        try:
            ss = self.child
            self._enter_view('system')
            ss.sendline('authorize %s %s' % (username, mode))
            ss.expect('authorize %s %s\r\n<(.*?)@(.*?) system>' % (username, mode))
            log.log(0, 'Set %s\'s authorize: %s ...' % (username, mode))
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s\'s authorize: time out ...' % username)
            raise EXCEPTION(2, 'Set %s\'s authorize: time out' % username)             

    def add_rule_mode(self, rule_mode_list):
        try:
            if type(rule_mode_list) == types.ListType:
                pass
            elif type(rule_mode_list) == types.StringType:
                rule_mode_list = [rule_mode_list]
            else:
                log.log(2, 'Rule mode list type error...')
                raise EXCEPTION(2, 'Add rule mode: rule mode list type error')
            ss = self.child
            self._enter_view('service')
            line = ''
            for rule_mode in rule_mode_list:
                line = line + rule_mode + ','
            line = line.strip(',')
            ss.sendline('rule-mode %s' % line)
            index = ss.expect(['rule-mode %s\r\n<(.*?)@(.*?) service>' % line, 'The flexible rule is exist'], 5)
            if index == 0:
                log.log(0, 'Add rule mode: %s ...' % line)
            elif index == 1:
                log.log(0, 'Add rule mode: the flexible rule is exist ...')
        except pexpect.TIMEOUT:
            log.log(2, 'Add rule mode: time out...')
            raise EXCEPTION(2, 'Add rule mode: time out')

    def get_group(self, user, group_no, keyword):
        try:
            if keyword in ['active port list', 'uplink load balance', 'downlink load balance']:
                ss = self.child
                self._enter_group_view(user, group_no)
                ss.sendline('show current-group')
                ss.expect('The Current Group Information(.*?)\r\n<(.*?)@(.*?) group \((.*?):%d\)>' % group_no, 5)
                ack = self._strip(ss.after)
                #if keyword == 'active port list':
                ret = None
                return ret
            else:
                log.log(2, 'Unmatched keyword of getting group attribute...')
                raise EXCEPTION(1, 'Get group: unmatched keyword')
        except pexpect.TIMEOUT:
            log.log(2, 'Get %s of group %d: time out...' % (keyword, group_no))
            raise EXCEPTION(2, 'Get %s of group %d: timeout' % (keyword, group_no))

    def set_group(self, user, group_no, keyword, value=None):
        try:
            if keyword in ['active port list', 'no port', 'load balance']:
                ss = self.child
                self._enter_group_view(user, group_no)
                if keyword == 'active port list':
                    if type(value) == types.ListType:
                        pass
                    elif type(value) == types.StringType:
                        value = [value]
                    port_str = ''
                    for i in range(0, len(value)):
                        port_str = port_str + value[i].get() + ','
                    port_str = port_str.strip(',')
                    ss.sendline('no port-all')
                    ss.expect('no port-all\r\n<(.*?)@(.*?) group \((.*?):%d\)>' % group_no)
                    ss.sendline('port %s' % port_str)
                    index = ss.expect(['port %s\r\n<(.*?)@(.*?) group \((.*?):(.*?)\)>' % port_str,
                                      'is not exist'], 5)
                    if index == 0:
                        log.log(0, 'Set %s\'s group %d ports: %s ...' % (user, group_no, port_str))
                    elif index == 1:
                        log.log(2, 'Set group: unmatched port name...')
                        raise EXCEPTION(1, 'Set group: unmatched port name')
                elif keyword == 'no port':
                    if value == None:
                        ss.sendline('no port-all')
                        ss.expect('no port-all\r\n<(.*?)@(.*?) group \((.*?):%d\)>' % group_no)
                        log.log(0, 'Remove all ports from %s\'s group %s...' % (user, group_no))
                    else:
                        if type(value) == types.ListType:
                            pass
                        elif type(value) == types.StringType:
                            value = [value]
                        port_str = ''
                        for i in range(0, len(value)):
                            port_str = port_str + value[i].get() + ','
                        port_str = port_str.strip(',')
                        ss.sendline('no port %s' % port_str)
                        ss.expect('no port %s\r\n<(.*?)@(.*?) group \((.*?):(.*?)\)>' % port_str, 5)
                        log.log(0, 'Remove ports from group %d: %s ...' % (group_no, port_str))
                    ret = 0
                elif keyword == 'load balance':
                    if value in ['dip', 'sip', 'sip-dip', 'sip-dip-sport-dport', 'sip-dip-sport-dport-protocol']:
                        ss.sendline('load-balance downlink %s' % value)
                        index = ss.expect(['load-balance downlink %s\r\n<(.*?)@(.*?) group \((.*?):(.*?)\)>' % value, 'Error:  No ppb board'], 5)
                        if index == 1:
                            log.log(2, 'Set group %d load balance: no port ...' % group_no)
                            raise EXCEPTION(1, 'Set group %d load balance: no port' % group_no)
                        ss.sendline('load-balance uplink %s' % value)
                        ss.expect('load-balance uplink %s\r\n<(.*?)@(.*?) group \((.*?):(.*?)\)>' % value, 5)
                        log.log(0, 'Set group %d load balance: %s ...' % (group_no, value))
                        ret = 0
                    else:
                        log.log(2, 'Unmatched value of load balance ...')
                        raise EXCEPTION(1, 'Set group: unmatched value of load balance')
            else:
                log.log(2, 'Unmatched keyword of setting group attribute...')
                raise EXCEPTION(1, 'Set group: unmatched keyword')
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s of group: time out...' % keyword)
            raise EXCEPTION(2, 'Set %s of group: time out' % keyword)

    def _get_port(self, name, keyword):
        ss = self.child
        self._enter_interface_view(name)
        ss.sendline('show current-interface')
        ss.expect('interface detail information(.*?)<(.*?)@(.*?) interface %s>' % name, 5)
        ack = self._strip(ss.after)
        ack = ack[ack.index(keyword) + 1]
        if keyword in ['link', 'mode', 'fiber', 'type']:
            ret = ack
        elif keyword in ['input bytes', 'output bytes', 'input packets', 'output packets']:
            ret = string.atoi(ack)
        return ret

    def get_port(self, port, keyword):
        try:
            if keyword in ['link', 'mode', 'fiber', 'type', 'input bytes', 'output bytes', \
                           'input packets', 'output packets']:
                name = port.get()
                ret = self._get_port(name, keyword)
                if type(ret) == types.StringType:
                    log.log(0, 'Get %s of interface %s: %s' % (keyword, name, ret))
                else:
                    log.log(0, 'Get %s of interface %s: %d' % (keyword, name, ret))
            else:
                log.log(2, 'Unmatched keyword of getting port attribute...')
                raise EXCEPTION(1, 'Get port: unmatched keyword of getting port attribute')
            return ret
        except pexpect.TIMEOUT:
            log.log(2, 'Get %s of port %s: time out...' % (keyword, name))
            raise EXCEPTION(2, 'Get %s of port %s: time out' % (keyword, name))

    def set_port(self, port, keyword, value=None):
        try:
            if keyword in ['mode', 'single-fiber', 'type', 'link-protocol', 'crc', 'scramble',
                           'enable', 'disable']:
                name = port.get()
                ss = self.child
                self._enter_interface_view(name)
                if keyword == 'single-fiber':
                    if value in ['rx', 'tx']:
                        ss.sendline('single-fiber %s' % value)
                        ss.expect('single-fiber %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                        log.log(0, 'Set port %s single-fiber: %s' % (name, value))
                    elif value == 'disable':
                        ss.sendline('no single-fiber')
                        ss.expect('no single-fiber\r\n<(.*?)@(.*?) interface (.*?)>', 5)
                        log.log(0, 'Set port %s no single-fiber' % name)
                    else:
                        log.log(2, 'Unmatched value of single-fiber ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of single-fiber')
                if keyword == 'type':
                    if value in ['10ge', 'oc192']:
                        ss.sendline('type %s' % value)
                        ss.expect('type %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                        if value == '10ge':
                            port.type = 'xgei'
                        elif value == 'oc192':
                            port.type = 'pos'
                        log.log(0, 'Set port %s type: %s' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of type ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of type')
                if keyword == 'link-protocol':
                    if value in ['hdlc', 'ppp', 'self-adaptive']:
                        ss.sendline('link-protocol %s' % value)
                        index = ss.expect(['link-protocol %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                        if index == 1:
                            log.log(2, 'Port %s is not a POS port' % name)
                            raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                        log.log(0, 'Set port %s link protocol: %s' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of link-protocol ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of link-protocol')
                if keyword == 'crc':
                    if value in ['16', '32', 'self-adaptive']:
                        ss.sendline('crc %s' % value)
                        index = ss.expect(['crc %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                        if index == 1:
                            log.log(2, 'Port %s is not a POS port' % name)
                            raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                        log.log(0, 'Set port %s crc: %s' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of crc ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of crc')
                if keyword == 'scramble':
                    if value in ['disable', 'enable', 'self-adaptive']:
                        ss.sendline('scramble %s' % value)
                        index = ss.expect(['scramble %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                        if index == 1:
                            log.log(2, 'Port %s is not a POS port' % name)
                            raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                    else:
                        log.log(2, 'Unmatched value of scramble ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of scramble')
                if keyword == 'enable' or keyword == 'disable':
                    ss.sendline('%s' % keyword)
                    ss.expect(['%s\r\n<(.*?)@(.*?) interface (.*?)>' % keyword], 5)
                    log.log(0, 'Port %s is %s...' % (name, keyword))
            else:
                log.log(2, 'Unmatched keyword of setting port attribute...')
                raise EXCEPTION(1, 'Set port: unmatched keyword of setting port attribute')
            log.log(0, 'Set %s of %s: %s...' % (keyword, name, value))
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s of %s: time out...' % (keyword, name))
            raise EXCEPTION(2, 'Set %s of %s: time out' % (keyword, name))

    def get_rule_sum(self, keyword):
        try:
            if keyword in ['mask ipv4', 'mask ipv6', 'flexible ipv4', 'flexible ipv6', \
                           'combined ipv4', 'combined ipv6', 'tcp flag', 'dpi', \
                           'dynamic ipv4', 'dynamic ipv6', 'total']:
                ss = self.child
                self._enter_view('acl')
                ss.sendline('show sum')
                ss.expect('s rules(.*?)<(.*?)@(.*?) acl>', 5)
                ack = self._strip(ss.after)
                ret = string.atoi(ack[ack.index(keyword + ' sum') + 1])
                log.log(0, 'Get sum of %s rules...' % keyword)
            else:
                log.log(2, 'Unmatched keyword of getting rule sum...')
                raise EXCEPTION(1, 'Get rule sum: unmatched keyword of getting rule sum')
            return ret
        except pexpect.TIMEOUT:
            log.log(2, 'Get rule sum: time out...')
            raise EXCEPTION(2, 'Get rule sum: time out')

    def _add_dpi_rule(self, obj):
        try:
            ss = self.child
            ss.sendline('dpi %s %s %d %d %d %d %d %d %d %d %d' %\
                        (obj.dpi, obj.mdpi, obj.group_no, obj.action, obj.reboot_save,\
                         obj.hit_stat, obj.combined_rule, obj.rule_id, obj.window_num, obj.window_width,\
                         obj.window_start_position))
            ss.expect('dpi %s %s %d %d %d %d %d %d %d %d %d\r\n<(.*?)@(.*?) acl>' %\
                      (obj.dpi, obj.mdpi, obj.group_no, obj.action, obj.reboot_save,\
                       obj.hit_stat, obj.combined_rule, obj.rule_id, obj.window_num, obj.window_width,\
                       obj.window_start_position))
            log.log(0, 'Set dpi rule: %s %s %d %d %d %d %d %d %d %d %d' %\
                    (obj.dpi, obj.mdpi, obj.group_no, obj.action, obj.reboot_save,\
                     obj.hit_stat, obj.combined_rule, obj.rule_id, obj.window_num, obj.window_width,\
                     obj.window_start_position))
        except pexpect.TIMEOUT:
            log.log(2, 'Set dpi rule: time out...')
            raise EXCEPTION(2, 'Set dpi rule: time out')

    def _add_ip_rule(self, obj, rule_type):
        try:
            ss = self.child
            ss.sendline('%s %s %s %s %s %d %d %d %d %d %d %d %d %d %d %d %d %s' %\
                        (rule_type, obj.sip, obj.sip_mask, obj.dip, obj.dip_mask, obj.sport,\
                         obj.sport_mask, obj.dport, obj.dport_mask, obj.protocol, obj.protocol_mask,\
                         obj.group_no, obj.action, obj.reboot_save, obj.hit_stat,\
                         obj.mask_flag, obj.rule_id, obj.relation_rule))
            index = ss.expect(['%s %s %s %s %s %d %d %d %d %d %d %d %d %d %d %d %d %s\r\n<(.*?)@(.*?) acl>' %\
                               (rule_type, obj.sip, obj.sip_mask, obj.dip, obj.dip_mask, obj.sport,\
                                obj.sport_mask, obj.dport, obj.dport_mask, obj.protocol, obj.protocol_mask,\
                                obj.group_no, obj.action, obj.reboot_save, obj.hit_stat,\
                                obj.mask_flag, obj.rule_id, obj.relation_rule), 'Invalid rule type'], 5)
            if index == 0:
                log.log(0, 'Set %s rule: %s %s %s %s %d %d %d %d %d %d %d %d %d %d %d %d %s...' %\
                           (rule_type, obj.sip, obj.sip_mask, obj.dip, obj.dip_mask, obj.sport,\
                            obj.sport_mask, obj.dport, obj.dport_mask, obj.protocol, obj.protocol_mask,\
                            obj.group_no, obj.action, obj.reboot_save, obj.hit_stat,\
                            obj.mask_flag, obj.rule_id, obj.relation_rule))
            elif index == 1:
                log.log(2, 'Set %s rule: invalid rule type ....' % rule_type)
                raise EXCEPTION(1, 'Set %s rule: invalid rule type')
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s rule: time out...' % rule_type)
            raise EXCEPTION(2, 'Set %s rule: time out' % rule_type)

    def _add_tcp_flag_rule(self, obj):
        try:
            ss = self.child
            ss.sendline('tcp-flag %d %d %d %d %d %d %d %d %d' %
                        (obj.urg, obj.ack, obj.psh, obj.rst, obj.syn, obj.fin, obj.length,
                         obj.action, obj.if_group_no, obj.rule_id))
            ss.expect('tcp-flag %d %d %d %d %d %d %d %d %d\r\n<(.*?)@(.*?) acl>' %
                      (obj.urg, obj.ack, obj.psh, obj.rst, obj.syn, obj.fin, obj.length,
                       obj.action, obj.if_group_no, obj.rule_id), 5)
            log.log('Set tcp-flag rule: %d %d %d %d %d %d %d %d %d...' %
                    (obj.urg, obj.ack, obj.psh, obj.rst, obj.syn, obj.fin, obj.length,
                     obj.action, obj.if_group_no, obj.rule_id))
        except pexpect.TIMEOUT:
            log.log(2, 'Set tcp-flag rule: time out...' % rule_type)
            raise EXCEPTION(2, 'Set tcp-flag rule: time out' % rule_type)

    def add_rule(self, rule_list):
        self._enter_view('acl')
        for i in range(0, len(rule_list)):
            obj = rule_list[i]
            name = obj.__class__.__name__
            if 'Ipv4Rule' in name:
                self._add_ip_rule(obj, 'ipv4')
            elif 'Ipv6Rule' in name:
                self._add_ip_rule(obj, 'ipv6')
            elif 'DpiRule' in name:
                self._add_dpi_rule(obj)
            elif 'TcpFlagRule' in name:
                self._add_tcp_flag_rule(obj)
            else:
                log.log(2, 'No such rule type: %s' % name)
                raise EXCEPTION(1, 'Set rule: no %s rule type' % name)

    def set_dpi_dynamic(self, state='enable'):
        try:
            ss = self.child
            self._enter_view('acl')
            if state == 'enable':
                ss.sendline('dpi-dynamic')
                ss.expect('dpi-dynamic\r\n<(.*?)@(.*?) acl>', 5)
                log.log(0, 'Set dpi-dynamic enable...')
            elif state == 'disable':
                ss.sendline('no dpi-dynamic')
                ss.expect('no dpi-dynamic\r\n<(.*?)@(.*?) acl>', 5)
                log.log(0, 'Set dpi-dynamic disable...')
        except pexpect.TIMEOUT:
            log.log(2, 'Set dpi-dynamic %s: time out...' % state)
            raise EXCEPTION(2, 'Set dpi-dynamic %s: time out' % state)

    def clear_rule(self, rule_list=['all']):
        try:
            ss = self.child
            self._enter_view('acl')
            if rule_list == ['all']:
                ss.sendline('no all')
                ss.expect('no all(.*?)Deleting(.*?)<(.*?)@(.*?) acl>')
                log.log(0, 'Clear all rules...')
            else:
                pass
        except pexpect.TIMEOUT:
            log.log(2, 'Clear rule: time out...')
            raise EXCEPTION(2, 'Clear rule: time out')
