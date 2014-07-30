#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of libixia.

### Import necessary modules
import sys
import re
import os
import _tkinter
import time
import datetime

from test_station.logging.logger import log
from test_station.err import EXCEPTION
from test_station.resource import Resource
from test_station import gl
from test_station.libfile import file

if sys.version_info < (3, 0):
    from Tkinter import Tcl
else:
    from tkinter import Tcl

### IxiaPort class
class IxiaPort(Resource):
    '''Ixia port controlling class'''

    ref_count = {}
    init_dict = {}
    passport = ""
    
    ###@brief Parse RPC result from TclServer
    ###@param arg RPC result
    ###@return A dictionary, with key code indicating result,
    ###0 for success and <0 for failure; when failure, key reason
    ###log the corresponding explaination 
    @staticmethod
    def parse(arg):
        if (re.match('^\d+.*', arg)) is not None:
            return {'code':0, 'reason':arg[2:]}
        elif (re.match('^\-\d+.*', arg)) is not None:
            return {'code':-1, 'reason':arg[3:]}
        else:
            return {'code':-2, 'reason':'Unknown error code'}
    
    ###@brief Constructor
    ###@param tcl_server TCL服务器实例
    ###@param ixia_port ixia端口实例
    ###@return Always return None, which is demanded
    ###by language specification
    def __init__(self, node):
        
        # if this is the first instance of port in the script
        # explicitly connect to the chassis
        Resource.__init__(self, node.get("name"), "ixia_port")
        self.ts_version = None
        self.user = gl.test_user
        self.path = None
        self.key = None
        self.is_init = False
        self.server = None
        self.initial = False
        self.tx = False
        self.rx = False
        self.interp = None
        self.connect = []
        self.__parse(node)
        self.version = self.ts_version
        self.path = self.ts_stream_path
        self.key = ("%s:%s"%(self.ts_addr[0], self.chassis_ip))
        self.server = " %d %s "%(self.ts_addr[1], self.ts_addr[0])

    def __parse(self, node):
        self.chassis_ip = node.findtext('ip')
        self.card_no = int(node.findtext('card_no'))
        self.port_no = int(node.findtext('port_no'))
        self.type = node.findtext('type')
        ts_addr = node.findtext("ts_addr").split(":")
        self.ts_addr = [ts_addr[0], int(ts_addr[1])]
        self.ts_version = node.findtext("ts_version")
        self.ts_stream_path = node.findtext("ts_stream_path")

    ###@brief Execute TCL expression
    ###@param command TCL command in string
    ###@return Return the corresponding RPC result
    def __execute(self, command):
        tcl = self.interp
        return tcl.eval(command)
    
    ###@brief Destructor
    def release(self):
        log(0, "-- (%s) Release start --"%self.kind)
        if self.is_init:
            IxiaPort.ref_count[self.key] = IxiaPort.ref_count[self.key] - 1
            #Try to release the device
            if self.initial == True:
                ### Never release the port
                #ret = self.__execute("tc_exec %s port_release %s" % (self.server, self.portmap))
                if self.tx == True:
                    self.__execute("tc_exec %s stop_tx %s" % (self.server, self.portmap))
                if self.rx == True:
                    self.__execute("tc_exec %s stop_rx %s" % (self.server, self.portmap))
                            
            if IxiaPort.ref_count[self.key] == 0:
                if IxiaPort.init_dict[self.key] == True:
                    ret = self.__execute("tc_exec %s ixia_exit %s" % (self.server, self.chassis_ip))
                else:
                    IxiaPort.init_dict[self.key] == False

    def init(self):
        self.is_init = True
        if self.key in IxiaPort.ref_count:
            IxiaPort.ref_count[self.key] = IxiaPort.ref_count[self.key] + 1
        else:
            IxiaPort.ref_count[self.key] = 1
            IxiaPort.init_dict[self.key] = False
            
        self.interp = Tcl()
        
        #Setup Tcl testing environment
        ret = self.__execute('source %s/tc-utils.tcl' % os.path.abspath(os.path.dirname(__file__)))
        if ret:
            log(2, ret)
            return None

        #Check activity of the server
        ret = self.__execute("tc_init " + self.server)
        log(0, 'Communicate with tcl server: %s, %d' % (self.ts_addr[0], self.ts_addr[1]))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, c['reason'])
            return None
        else:
            passport = c['reason'].strip()

        if IxiaPort.passport == "":
            IxiaPort.passport = passport
       
        def getHoldingTime():
            now = datetime.datetime.now()
            delta = datetime.timedelta(days=1)
            n_days = now + delta
            from_time = now.strftime("%m%d")
            to_time = n_days.strftime("%m%d")
            return "%s_%s"%(from_time,to_time)

        if IxiaPort.ref_count[self.key] > 0:
            ret = self.__execute("tc_exec %s ixia_init %s %s" % (self.server, self.chassis_ip, "%s_%s"%(self.user,getHoldingTime())))
            log(0, "Ixia init: %s, %d/%d" % (self.chassis_ip, self.card_no, self.port_no))
            c = IxiaPort.parse(ret)
            if c['code'] == -1:
                log(2, "In __init__(): " + c['reason'])
                return None
            else:
                IxiaPort.init_dict[self.key] = True
        
        self.portmap = "{%s %d %d}" % (self.chassis_ip, self.card_no, self.port_no)
        
        ret = self.__execute("tc_exec %s port_owning %s" % (self.server, self.portmap))
        log(0, "Take ownership: %s" % self.user)
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In __init__(): " + c['reason'])
            return None      
        
        self.initial = True
        self.loaded = False
        self.stats = {"Link State": bool, \
                      "Line Speed": int, \
                      "Frames Sent": int, \
                      "Valid Frames Received": int, \
                      "Bytes Sent": int, \
                      "Bytes Received": int }
    
    ###@brief Load configuration into device
    ###@param config Configuration file information
    ###@param multiple 原始流速率的倍数，支持浮点，例如原始流速率为100%，multiple为0.5，则实际流速率为50%
    ###Currently it consistutes case name, port config file name
    ###and stream config file name, separated by hyphen
    ###@return Always return 0, on error exception is thrown out
    def load(self, stream, multiple):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
           
        dir = gl.current_case.dir
        port_path = "%s/port_%s.tcl"%(self.path,self.type)
        newtcl = "%s-%s"%(dir.strip("/").rpartition("/")[-1],stream.rpartition("/")[-1])
        stream_path = "%s/%s"%(self.path,newtcl)
        src_stream = "%s/%s"%(dir.strip("/"),stream)
        dst_stream = r"C:\autotest_G\NETFIRM\%s"%newtcl   

        f = file.File()
        f.connect(self.ts_addr[0], 1234)
        f.transfer(src_stream, dst_stream)

        log(0, 'Set multiple of initial stream-rate: x%-5.4f' % multiple)

        ret = self.__execute("tc_exec %s port_load %s %s %s %d" % (self.server, self.portmap, port_path, stream_path, multiple*10000000))

        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In load(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            self.loaded = True
            return 0
    
    ###@brief Start transmitting packets
    ###@param block Indicates method should behave in
    ###synchronous way or asynchronous way, True for synchronous
    ###@return Always return 0, on error exception is thrown out
    def startTransmit(self, block=False):
        if self.initial == False:
            log(2, "(startTransmit) Instance not properly instanitiated")
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        if self.loaded == False:
            log(2, "(startTransmit) Configuration unloaded")
            raise(EXCEPTION(1, "Configuration unloaded"))
        
        log(0, 'Start ixia transmit')
        ret = self.__execute("tc_exec %s start_tx %s %d" % (self.server, self.portmap, (1 if block else 0)))

        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In startTransmit(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            if block == False:
                self.tx = True
            return 0
    ###@brief Pause transmitting packets
    ###@note Un-implemented
    def pauseTransmit(self):
        pass
    
    ###@brief Stop transmitting packets
    ###@return Always return 0, on error exception is thrown out
    def stopTransmit(self):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        ret = self.__execute("tc_exec %s stop_tx %s" % (self.server, self.portmap))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In stopTransmit(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            time.sleep(1)
            self.tx = False
            log(0, 'Stop ixia transmit')
            return 0
    
    ###@brief Start capturing packets
    ###@return Always return 0, on error exception is thrown out
    def startCapture(self):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        ret = self.__execute("tc_exec %s start_rx %s" % (self.server, self.portmap))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In startCapture(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            self.rx = True
            log(0, 'Start capture')
            return 0

    ###@brief Stop capturing packets
    ###@return Always return 0, on error exception is thrown out 
    def stopCapture(self):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        ret = self.__execute("tc_exec %s stop_rx %s" % (self.server, self.portmap))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In stopCapture(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            self.rx = False
            log(0, 'Stop capture')
            return 0
    
    ###@brief Get statistics
    ###@param keyword Always the same statistics label when using IxExplorer
    ###@return Return the statistics, on error exception is thrown out 
    def getStats(self, keyword):
        if self.initial == False:
            log(2, 'Get statisic(%s): instance not properly instanitiated' % keyword)
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        if self.tx or self.rx:
            log(2, 'Get statisic(%s): ixia is still running, stop it first' % keyword)
            raise(EXCEPTION(1, "Ixia is still running, stop it first"))
        
        ret = self.__execute("tc_exec %s get_stat %s {%s}" % (self.server, self.portmap, keyword))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In getStats(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            convert = self.stats[keyword]
            if convert != None:
                log(0, 'Get statistic(%s): %d' % (keyword, convert(c['reason'])))
                return convert(c['reason'])
            else:
                log(0, 'Get statistic(%s): %d' % (keyword, c['reason']))
                return c['reason']
    
    ###@brief Clear statistics
    ###@return Always return 0, on error exception is thrown out 
    def clearStats(self):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        ret = self.__execute("tc_exec %s clear_stat %s" % (self.server, self.portmap))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In clearStats(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            log(0, 'Clear ixia stats')
            return 0
    
    ###@brief Get packet view of transmitting stream
    ###@param streamId The corresponding stream identifier
    ###@param pktNum Packet to be transmitted in the stream
    ###@return Return the frame, on error exception is thrown out 
    def getTxFrame(self, streamId, pktNum):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        if self.loaded == False:
            raise(EXCEPTION(1, "Configuration unloaded"))

        ret = self.__execute("tc_exec %s get_tx_frame %s %d %d" % (self.server, self.portmap, streamId, pktNum))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In getTxFrame(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            return c['reason']
        
    ###@brief Get captured packet
    ###@param pktNum Packet number in the capture buffer
    ###@return Return the frame, on error exception is thrown out     
    def getRxFrame(self, pktNum):
        if self.initial == False:
            raise(EXCEPTION(1, "Instance not properly instanitiated"))
        
        ret = self.__execute("tc_exec %s get_rx_frame %s %d" % (self.server, self.portmap, pktNum))
        c = IxiaPort.parse(ret)
        if c['code'] == -1:
            log(2, "In getRxFrame(): " + c['reason'])
            raise(EXCEPTION(1, c['reason']))
        else:
            return c['reason']    

