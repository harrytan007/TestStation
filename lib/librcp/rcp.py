#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of librcp.

"""RCP客户端功能模块。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

import string
import sys, os
import ConfigParser
from test_station.err import EXCEPTION
from test_station.logging.logger import log
from test_station.resource import Resource
from test_station import gl

class Rcp(Resource):
    """RCP客户端资源类
    """

    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "rcp_client")

        def script_path():
            import inspect, os
            caller_file = inspect.stack()[1][1]   
            return os.path.abspath(os.path.dirname(caller_file))

        self.rcp_path = script_path()
        self.add_tool = "%s/g_client_add"%self.rcp_path
        self.case_path = None
        self.auth_path = None

        self.__parse(node)
        
    def __del__(self):
        pass

    def __parse(self, node):
        self.client_ip = node.findtext("client_ip") 

    def set(self, device_ip, user, password):
        """配置RCP客户端
           device_ip：下发目标设备的IP
           user：用户名
           password：密码
        """
        self.case_path = gl.current_case.dir
        self.auth_path = "%s/auth.conf"%(self.case_path.strip("/"))

        str =  "RCP_DEV_IP=%s\nRCP_DEV_PORT=1000\n"%device_ip
        str += "CLIENT_IP=%s\n"%self.client_ip
        str += "USER=%s\nPASSWORD=%s\n"%(user,password)
        str += "BLOCK_NUM=1\nIS_ORDER=1\n"
        f = open(self.auth_path, 'w')
        f.write(str)
        f.close()
        log(0, 'Generate auth.conf ...')

    def walk(self, rules_dir):
        """遍历规则目录下的所有规则
           rules_dir：规则目录
        """
        lst = []
        rules_dir = "%s/%s"%(self.case_path.strip("/"),rules_dir.strip("./"))
        for i in os.walk(rules_dir):
            if i[0] == rules_dir:
                lst.append(i[2])
        return lst

    def add(self, rules_path):
        """规则下发方法。
           rules_path：规则文件的路径，可以是字符串，也可以是字符串组成的列表
        """
        if isinstance(rules_path, str):
            rules_path = "%s/%s"%(self.case_path.strip("/"),rules_path.split("/")[-1])
            rules_path = [rules_path]
        for rule in rules_path:
            cmd = self.add_tool + ' -u ' +  self.auth_path + ' -f ' + rule
            log(0, 'Adding rules ...')
            pipe = os.popen(cmd).read().split('\n')
