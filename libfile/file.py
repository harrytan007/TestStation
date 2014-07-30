#coding=utf-8

"""文件传输功能模块。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

import hashlib
from socket import *

class Socket():

    def __init__(self):
        self.sock = None

    def connect(self, host, port):
        self.sock = socket(AF_INET,SOCK_STREAM)
        self.sock.connect((host,port))

    def sendMsg(self, msg):
        self.sock.send(str(len(msg)).zfill(4)+msg)

    def send(self, data):
        self.sock.send(data)
    
    def readMsg(self):
        str = self.sock.recv(4)
        if not str: return None
        bytes = int(str)
        return self.sock.recv(bytes)

    """
    def readMsg(self,size):
        msg = self.sock.recv(size)
        return msg 
    """

    def close(self):
        self.sock.close()
class File(Socket):
    
    def __init__(self):
        Socket.__init__(self)

    def getMd5(self, dstfile):
        self.sendMsg(r"file_transfer getmd5 %s"%dstfile)
        while True:
            #msg = self.readMsg(self.rfile)
            msg = self.readMsg()
            if msg == None: break
            if msg == "none":
                return None
            else:
                msg_lst = msg.split(" ")
                transaction = msg_lst[0]
                func = msg_lst[1]
                err = msg_lst[2]
                md5 = msg_lst[3]
            if (transaction == "file_transfer" and func == "getmd5" and err == "0"):
                return md5 
            if(transaction == "file_transfer" and func == "getmd5" and err == "1"):
                return "getmd5 error"
            else:
                return "unknown transation"

    def calculateMd5(self, srcfile):
        file = None
        strMd5 = ""
        try:
            file = open(r"%s"%srcfile, "rb")
            md5 = hashlib.md5()
            strRead = ""

            while True:
                strRead = file.read(8096)
                if not strRead:
                    break
                md5.update(strRead)
            #read file finish  
            bRet = True
            strMd5 = md5.hexdigest()
            return strMd5
        except:
            return "can not get md5"
        finally:
            if file:
                file.close()

    def getResponse(self):
            while True:
                msg = self.readMsg()
                if msg == None: break
                if msg == "none":
                    return None
                else:
                    msg_lst = msg.split(" ")
                    transaction = msg_lst[0]
                    func = msg_lst[1]
                    err = msg_lst[2]
                    detail = msg_lst[3]
                if (transaction == "file_transfer" and func == "finish" and err == "0"):
                    return "transfer done" 
                else:
                    return "transfer failed"
        
    def transfer(self, srcfile, dstfile):
        if (self.getMd5(dstfile) != self.calculateMd5(srcfile)):
            self.sendMsg(r"file_transfer start %s"%dstfile)
            f = open(srcfile, "rb")
            while True:   
                data = f.read(1024)   
                if not data:   
                    self.sendMsg("TRANSFER FILE END")
                    f.close()
                    break
                while len(data) > 0:   
                    intSent = self.sendMsg(data)   
                    if intSent == None: 
                        break
                    #print intSent
                    data = data[intSent:]   
            return self.getResponse()  
        else:  
            return "file exists"
        self.close()
    

if __name__ == "__main__":
    host = "10.0.24.16"
    port = 1234
    file = File()
    file.connect(host, port)  
    file.transfer("./demo.py",r"/home/gaoxun/trunk/autotest/test_agent/demo.py")
    file.connect(host, port)  
    file.transfer("./demo1.py",r"/home/gaoxun/trunk/autotest/test_agent/demo1.py")
