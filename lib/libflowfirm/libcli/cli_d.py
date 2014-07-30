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
        self.group_type = 'group'
        self.group_no = None
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
        self.group_type = 'group'
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
        self.group_type = 'group'
        self.group_no = 0
        self.action = 1
        self.reboot_save = 1
        self.hit_stat = 1
        self.combined_rule = 0
        self.rule_id = 0
        self.window_num = 0
        self.window_width = 0
        self.window_start_position = 0


class OtherRule:
    def __init__(self):
        self.type = None
        self.group_type = 'group'
        self.group_no = 0


class CliD(Cli):
    def __init__(self, ip, remote_passwd, user, passwd):
        Cli.__init__(self, ip, remote_passwd, user, passwd)

    def __del__(self):
        Cli.__del__(self)

    # Login device
    def login(self):
        self._remote_login()
        self._cli_login('/usr/share/flowfirm_D/bin')

    def _enter_group_view(self, type, group_no):
        try:
            if '%s %d' % (type, group_no) != self.cur_view:  
                ss = self.child
                ss.sendline('%s %d' % (type, group_no))
                ss.expect('%s %d\r\n<(.*?)@(.*?) %s \((.*?):(.*?)\)>' % (type, group_no, type), 5)
                if self.cur_view == 'root':
                    self.state += 1
                self.cur_view = '%s %d' % (type, group_no)
        except pexpect.TIMEOUT:
            log.log(2, 'Enter %s %d view: time out...' % (type, group_no))
            raise EXCEPTION(2, 'Enter %s %d view: time out' % (type, group_no))

    def set_default_action(self, forward_type, group_type=None, group_no=None):
        try:
            ss = self.child
            self._enter_view('service')
            if forward_type == 'forward':
                if type(group_no) != types.StringType:
                    group_no = '%d' % group_no
                ss.sendline('default-action forward %s %s' % (group_type, group_no))
                ss.expect('default-action forward %s %s\r\n<(.*?)@(.*?) service>' % (group_type, group_no), 5)
                log.log(0, 'Set default action: forward -> %s %s ...' % (group_type, group_no))
            elif forward_type == 'no-forward':
                ss.sendline('default-action no-forward')
                ss.expect('default-action no-forward\r\n<(.*?)@(.*?) service>', 5)
                log.log(0, 'Set default action: no-forward')
            else:
                log.log(2, 'Forward type or group number error...')
                raise EXCEPTION(1, 'Set default action: %s' % forward_type)
        except pexpect.TIMEOUT:
            log.log(2, 'Set default %s action: time out...' % forward_type)
            raise EXCEPTION(2, 'Set default %s action: time out' % forward_type)

    def set_unknown_packet(self, type, group_type=None, group_no=None):
        try:
            ss = self.child
            self._enter_view('service')
            if type == 'forward':
                if group_type in ['group', 'vlan']:
                    group_no = '%d' % group_no                
                ss.sendline('packet-in unknown-packet forward %s %s' % (group_type, group_no))
                ss.expect('packet-in unknown-packet forward %s %s\r\n<(.*?)@(.*?) service>' % (group_type, group_no), 5)
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

    def set_authorize(self, mode):
        try:
            ss = self.child
            self._enter_view('system')
            ss.sendline('authorize %s' % mode)
            ss.expect('authorize %s\r\n<(.*?)@(.*?) system>' % mode)
            log.log(0, 'Set authorize: %s ...' % mode)
        except pexpect.TIMEOUT:
            log.log(2, 'Set authorize: time out ...')
            raise EXCEPTION(2, 'Set authorize: time out')             

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

    #def get_version(self):
    #    try:
    #        ss = self.child
    #        self._enter_view('debug')
    #        ss.sendline('show sysversion %d' % board_no)
    #        ss.expect('The system version' % mode)
    #        log.log(0, 'Get system version ...')
    #        return 
    #    except pexpect.TIMEOUT:
    #        log.log(2, 'Get system version: time out ...')
    #        raise EXCEPTION(2, 'Get system version: time out')             

    def clear_fragment(self):
        try:
            ss = self.child
            self._enter_view('service')
            ss.sendline('fragment-reset')
            ss.expect('fragment-reset\r\n<(.*?)@(.*?) service>', 5)
            log.log(0, 'Clear fragment ...')
        except pexpect.TIMEOUT:
            log.log(2, 'Clear fragment: time out ...')
            raise EXCEPTION(2, 'Clear fragment: time out')

    def get_group(self, type, group_no, keyword):
        try:
            ss = self.child
            if keyword in ['active port list', 'uplink load balance', 'downlink load balance']:
                self._enter_group_view(type, group_no)
                ss.sendline('show current-group')
                ss.expect('The Current Group Information(.*?)\r\n<(.*?)@(.*?) %s \((.*?):%d\)>' % (type, group_no), 5)
                ack = self._strip(ss.after)
                #if keyword == 'active port list':
                ret = None
                return ret
            else:
                log.log(2, 'Unmatched keyword of getting group attribute...')
                raise EXCEPTION(1, 'Get group: unmatched keyword')
        except pexpect.TIMEOUT:
            log.log(2, 'Get %s of %s %d: time out...' % (keyword, type, group_no))
            raise EXCEPTION(2, 'Get %s of %s %d: timeout' % (keyword, type, group_no))

    def set_group(self, group_type, group_no, keyword, value=None):
        try:
            ss = self.child
            if keyword in ['active port list', 'no port', 'load balance']:
                self._enter_group_view(group_type, group_no)
                if keyword == 'active port list':
                    if type(value) == types.StringType:
                        value = [value]
                    port_str = ''
                    for i in range(0, len(value)):
                        port_str = port_str + value[i].get() + ','
                    port_str = port_str.strip(',')
                    ss.sendline('no port-all')
                    ss.expect('no port-all\r\n<(.*?)@(.*?) %s \((.*?):%d\)>' % (group_type, group_no))
                    ss.sendline('port %s' % port_str)
                    index = ss.expect(['port %s\r\n<(.*?)@(.*?) %s \((.*?):(.*?)\)>' % (port_str, group_type),\
                                      'is not exist'], 5)
                    if index == 0:
                        log.log(0, 'Set %s %d ports: %s ...' % (group_type, group_no, port_str))
                    elif index == 1:
                        log.log(2, 'Set group: Unmatched port name...')
                        raise EXCEPTION(1, 'Set group: unmatched port name')
                    ret = 0
                elif keyword == 'no port':
                    if value == None:
                        ss.sendline('no port-all')
                        ss.expect('no port-all\r\n<(.*?)@(.*?) %s \((.*?):%d\)>' % (group_type, group_no))
                        log.log(0, 'Remove all ports from group %s...' % group_no)
                    else:
                        if type(value) == types.StringType:
                            value = [value]
                        port_str = ''
                        for i in range(0, len(value)):
                            port_str = port_str + value[i].get() + ','
                        port_str = port_str.strip(',')
                        ss.sendline('no port %s' % port_str)
                        ss.expect('no port %s\r\n<(.*?)@(.*?) %s \((.*?):(.*?)\)>' % (port_str, group_type), 5)
                        log.log(0, 'Remove ports from %s %d: %s ...' % (group_type, group_no, value))
                    ret = 0
                elif keyword == 'load balance':
                    if value in ['dip', 'sip', 'sip-dip', 'sip-dip-sport-dport', 'sip-dip-sport-dport-protocol']:
                        ss.sendline('load-balance downlink %s' % value)
                        index = ss.expect(['load-balance downlink %s\r\n<(.*?)@(.*?) %s \((.*?):(.*?)\)>' % (value, group_type), 'Error:  No ppb board'], 5)
                        if index == 1:
                            log.log(2, 'Set %s %d load balance: no port ...' % (group_type, group_no))
                            raise EXCEPTION(1, 'Set %s %d load balance: no port' % (group_type, group_no))
                        ss.sendline('load-balance uplink %s' % value)
                        ss.expect('load-balance uplink %s\r\n<(.*?)@(.*?) %s \((.*?):(.*?)\)>' % (value, group_type), 5)
                        log.log(0, 'Set %s %d load balance: %s ...' % (group_type, group_no, value))
                        ret = 0
                    else:
                        log.log(2, 'Unmatched value of load balance ...')
                        raise EXCEPTION(1, 'Set group: unmatched value of load balance')
            else:
                log.log(2, 'Unmatched keyword of setting group attribute...')
                raise EXCEPTION(1, 'Set group: unmatched keyword')
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s of %s: time out...' % (keyword, group_type))
            raise EXCEPTION(2, 'Set %s of %s: time out' % (keyword, group_type))

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
                    log.log(0, 'Get %s of interface %s: %s ...' % (keyword, name, ret))
                else:
                    log.log(0, 'Get %s of interface %s: %d ...' % (keyword, name, ret))
            else:
                log.log(2, 'Unmatched keyword of getting port attribute...')
                raise EXCEPTION(1, 'Get port: unmatched keyword of getting port attribute')
            return ret
        except pexpect.TIMEOUT:
            log.log(2, 'Get %s of port %s: time out ...' % (keyword, name))
            raise EXCEPTION(2, 'Get %s of port %s: time out' % (keyword, name))

    def set_port(self, port, keyword, value = None):
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
                        log.log(0, 'Set port %s single-fiber: %s ...' % (name, value))
                    elif value == 'disable':
                        ss.sendline('no single-fiber')
                        ss.expect('no single-fiber\r\n<(.*?)@(.*?) interface (.*?)>', 5)
                        log.log(0, 'Set port %s no single-fiber ...' % name)
                    else:
                        log.log(2, 'Unmatched value of single-fiber ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of single-fiber')
                if keyword == 'type':
                    if value in ['ge', '10ge', 'oc192']:
                        ss.sendline('type %s' % value)
                        ss.expect('type %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 5)
                        if value == 'ge':
                            port.type = 'gei'
                        elif value == '10ge':
                            port.type = 'xgei'
                        elif value == 'oc192':
                            port.type = 'pos'
                        log.log(0, 'Set port %s type: %s ...' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of type ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of type')
                if keyword == 'link-protocol':
                    if value in ['hdlc', 'ppp', 'self-adaptive']:
                        ss.sendline('link-protocol %s' % value)
                        index = ss.expect(['link-protocol %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                        if index == 1:
                            log.log(2, 'Port %s is not a POS port ...' % name)
                            raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                        log.log(0, 'Set port %s link protocol: %s ...' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of link-protocol ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of link-protocol')
                if keyword == 'crc':
                    if value in ['16', '32', 'self-adaptive']:
                        ss.sendline('crc %s' % value)
                        index = ss.expect(['crc %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                        if index == 1:
                            log.log(2, 'Port %s is not a POS port ...' % name)
                            raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                        log.log(0, 'Set port %s crc: %s ...' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of crc ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of crc')
                if keyword == 'scramble':
                    if value in ['disable', 'enable', 'self-adaptive']:
                        ss.sendline('scramble %s' % value)
                        index = ss.expect(['scramble %s\r\n<(.*?)@(.*?) interface (.*?)>' % value, 'is not pos'], 5)
                        if index == 1:
                            log.log(2, 'Port %s is not a POS port ...' % name)
                            raise EXCEPTION(1, 'Set port: port %s is not a POS port' % name)
                        log.log(0, 'Set port %s scramble: %s ...' % (name, value))
                    else:
                        log.log(2, 'Unmatched value of scramble ...')
                        raise EXCEPTION(1, 'Set port: unmatched value of scramble')
                if keyword == 'enable' or keyword == 'disable':
                    ss.sendline('%s' % keyword)
                    ss.expect('%s\r\n<(.*?)@(.*?) interface (.*?)>' % keyword, 5)
                    log.log(0, 'Port %s is %s ...' % (name, keyword))
            else:
                log.log(2, 'Unmatched keyword of setting port attribute ...')
                raise EXCEPTION(1, 'Set port: unmatched keyword of setting port attribute')
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s of %s: time out ...' % (keyword, name))
            raise EXCEPTION(2, 'Set %s of %s: time out' % (keyword, name))

    def port_stable(self, port_list, keyword, timeout=4):
        if keyword in ['input bytes', 'output bytes', 'input packets', 'output packets']:
            stable = 0
            interval = 1
            if type(port_list) == types.InstanceType:
                port_list = [port_list]
            port_num = len(port_list)
            log.log(0, 'Wait until port count is stable ...')
            for i in range(0, (timeout / interval)):
                temp1 = []
                temp2 = []
                for j in range(0, port_num):
                    temp1.append(self._get_port(port_list[j].get(), keyword))
                for j in range(0, port_num):
                    temp2.append(self._get_port(port_list[j].get(), keyword))
                if temp1 == temp2:
                    stable = 1
                    break
                time.sleep(interval - 0.5)
            if stable == 1:
                pass
            else:
                log.log(2, 'Port stability judgement timeout ...')
                raise EXCEPTION(1, 'Port stable: port stability judgement timeout')
        else:
            log.log(2, 'Unmatched keyword of port attribute ...')
            raise EXCEPTION(1, 'Port stable: unmatched keyword of port attribute')

    def get_rule_sum(self, keyword):
        try:
            if keyword in ['mask ipv4', 'mask ipv6', 'flexible ipv4', 'flexible ipv6', \
                           'combined ipv4', 'combined ipv6', 'tcp flag', 'dpi', \
                           'dynamic ipv4', 'dynamic ipv6', 'total']:
                ss = self.child
                self._enter_view('acl')
                ss.sendline('show sum')
                ss.expect('s rules number(.*?)<(.*?)@(.*?) acl>', 5)
                ack = self._strip(ss.after)
                ret = string.atoi(ack[ack.index(keyword) + 1])
                log.log(0, 'Get sum of %s rules ...' % keyword)
            else:
                log.log(2, 'Unmatched keyword of getting rule sum ...')
                raise EXCEPTION(1, 'Get rule sum: unmatched keyword of getting rule sum')
            return ret
        except pexpect.TIMEOUT:
            log.log(2, 'Get rule sum: time out ...')
            raise EXCEPTION(2, 'Get rule sum: time out')

    def _add_dpi_rule(self, obj):
        try:
            ss = self.child
            ss.sendline('dpi %s %s %s %d %d %d %d %d %d %d %d %d' %
                        (obj.dpi, obj.mdpi, obj.group_type, obj.group_no, obj.action, obj.reboot_save,
                         obj.hit_stat, obj.combined_rule, obj.rule_id, obj.window_num, obj.window_width,
                         obj.window_start_position))
            index = ss.expect(['dpi %s %s %s %d %d %d %d %d %d %d %d %d\r\n<(.*?)@(.*?) acl>' %
                              (obj.dpi, obj.mdpi, obj.group_type, obj.group_no, obj.action, obj.reboot_save,
                               obj.hit_stat, obj.combined_rule, obj.rule_id, obj.window_num, obj.window_width,
                               obj.window_start_position),
                               'Window width beyond range'], 5)
            if index == 0:
                log.log(0, 'Set dpi rule: %s %s %s %d %d %d %d %d %d %d %d %d ...' %
                           (obj.dpi, obj.mdpi, obj.group_type, obj.group_no, obj.action, obj.reboot_save,
                            obj.hit_stat, obj.combined_rule, obj.rule_id, obj.window_num, obj.window_width,
                            obj.window_start_position))
            elif index == 1: 
                log.log(2, 'Set dpi rule: window width beyond range...')
                raise EXCEPTION(2, 'Set dpi rule: window width beyond range')
        except pexpect.TIMEOUT:
            log.log(2, 'Set dpi rule: time out ...')
            raise EXCEPTION(2, 'Set dpi rule: time out')

    def _add_ip_rule(self, obj, rule_type):
        try:
            ss = self.child
            if obj.group_type in ['group', 'vlan']:
                group_no = '%d' % obj.group_no
            else:
                group_no = obj.group_no
            ss.sendline('%s %s %s %s %s %d %d %d %d %d %d %s %s %d %d %d %d %d %s' %
                        (rule_type, obj.sip, obj.sip_mask, obj.dip, obj.dip_mask, obj.sport,
                         obj.sport_mask, obj.dport, obj.dport_mask, obj.protocol, obj.protocol_mask,
                         obj.group_type, group_no, obj.action, obj.reboot_save, obj.hit_stat,
                         obj.mask_flag, obj.rule_id, obj.relation_rule))
            index = ss.expect(['%s %s %s %s %s %d %d %d %d %d %d %s %s %d %d %d %d %d %s\r\n<(.*?)@(.*?) acl>' %
                               (rule_type, obj.sip, obj.sip_mask, obj.dip, obj.dip_mask, obj.sport,
                                obj.sport_mask, obj.dport, obj.dport_mask, obj.protocol, obj.protocol_mask,
                                obj.group_type, group_no, obj.action, obj.reboot_save, obj.hit_stat,
                                obj.mask_flag, obj.rule_id, obj.relation_rule), 'Invalid rule type'], 5)
            if index == 0:
                log.log(0, 'Set %s rule: %s %s %s %s %d %d %d %d %d %d %s %s %d %d %d %d %d %s ...' %
                           (rule_type, obj.sip, obj.sip_mask, obj.dip, obj.dip_mask, obj.sport,
                            obj.sport_mask, obj.dport, obj.dport_mask, obj.protocol, obj.protocol_mask,
                            obj.group_type, group_no, obj.action, obj.reboot_save, obj.hit_stat,
                            obj.mask_flag, obj.rule_id, obj.relation_rule))
            elif index == 1:
                log.log(2, 'Set %s rule: invalid rule type ....' % rule_type)
                raise EXCEPTION(1, 'Set %s rule: invalid rule type')
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s rule: time out ...' % rule_type)
            raise EXCEPTION(2, 'Set %s rule: time out' % rule_type)

    def _add_other_rule(self, obj):
        try:
            ss = self.child
            if obj.group_type == 'group':
                ss.sendline('protocol-rule %s group %d' % (obj.type, obj.group_no))
                ss.expect('protocol-rule %s group %d\r\n<(.*?)@(.*?) acl>' % (obj.type, obj.group_no), 5)
        except pexpect.TIMEOUT:
            log.log(2, 'Set %s rule: time out ...' % obj.type)
            raise EXCEPTION(2, 'Set %s rule: time out' % obj.type)

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
            elif 'OtherRule' in name:
                self._add_other_rule(obj)
            else:
                log.log(2, 'No such rule type: %s' % name)
                raise EXCEPTION(1, 'Set rule: no %s rule type' % name)

    def get_forward_port(self, type, sip, dip, sport, dport, protocol, group_no):
        try:
            ss = self.child
            self._enter_view('acl')
            if type == 'ipv4' or type == 'ipv6':
                ss.sendline('show %s-forward-port %s %s %d %d %d %d' % (type, sip, dip, sport, dport, protocol, group_no))
                ss.expect('show %s-forward-port %s %s %d %d %d %d\r\n forward port :   (.*?)<(.*?)@(.*?) acl>' % (type, sip, dip, sport, dport, protocol, group_no), 5)
                #ss.expect('forward port :', 5)
                list = self._strip(ss.after)
                port_name = list[list.index('forward port') + 1]
                log.log(0, 'Get forward port: %s ...' % port_name)
                return port_name
            else:
                log.log(2, 'Unmatched type of getting forward port...')
                raise EXCEPTION(1, 'Get forward port: unmatched type of getting forward type')
        except pexpect.TIMEOUT:
            log.log(2, 'Get rule sum: time out ...')
            raise EXCEPTION(2, 'Get rule sum: time out')

    def clear_rule(self, rule_list=['all']):
        try:
            ss = self.child
            self._enter_view('acl')
            if rule_list == ['all']:
                ss.sendline('no all')
                ss.expect('no all(.*?)Deleting(.*?)<(.*?)@(.*?) acl>', 2000)
                ss.sendline('no protocol-rule-all')
                ss.expect('no protocol-rule-all\r\n<(.*?)@(.*?) acl>', 5)
                log.log(0, 'Clear all rules ...')
            else:
                pass
        except pexpect.TIMEOUT:
            log.log(2, 'Clear rule: time out ...')
            raise EXCEPTION(2, 'Clear rule: time out')

    def set_arp(self, ip, mac, port):
        try:
            port_name = port.get()
            ss = self.child
            self._enter_view('service')
            ss.sendline('arp %s %s %s' % (ip, mac, port_name))
            ss.expect('arp %s %s %s\r\n<(.*?)@(.*?) service>' % (ip, mac, port_name), 5) 
            log.log(0, 'Bind ARP %s/%s to port %s...' % (ip, mac, port_name))
        except pexpect.TIMEOUT:
            log.log(2, 'Set arp: time out...')
            raise EXCEPTION(2, 'Set arp: time out')
