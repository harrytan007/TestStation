#coding=utf-8
"""
"""
from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler
import hashlib
 
host = ''
port = 1234
addr = (host,port)
 
class Server(ThreadingMixIn, TCPServer):pass

class Handler(StreamRequestHandler):

    def handle(self):
        print 'got connection from ',self.client_address
        #self.wfile.write('connection %s:%s succeed!' % (host,port))

        def readMsg(rfile):
            str = self.rfile.read(4)
            if not str: return None
            bytes = int(str)
            return self.rfile.read(bytes)

        while True:
            msg = readMsg(self.rfile)
            if msg == None: break
            print msg
            self.msgHandle(msg)

    def sendMsg(self, msg):
        self.request.send(str(len(msg)).zfill(4)+msg)

    def msgHandle(self, msg):
        msg_list = msg.split()
        transaction = msg_list[0]
        func = msg_list[1]
        args = msg_list[2:]
        if transaction == "file_transfer":
            tr = FileTransfer(func, args, self)
            response = tr.handle()
            self.sendMsg("%s %s %s %s"%(response.transaction,response.func,response.err,response.detail))
        else:
            print "Unkown transaction"

class Response():
    def __init__(self,trsct,fc):
        """transaction:业务，比如file_transfer，data_transmit_ixia，data_transmit_sprient,data_transmit_pacp
           func:作用，比如start,getMd5,stop
           err:0代表成功完成任务，1代表失败
           detail:具体的消息内容
        """
        self.transaction = trsct
        self.func = fc
        self.err = 0
        self.detail = None

class Transaction():pass

class FileTransfer(Transaction):

    def __init__(self, func, args, handler):
        self.func = func
        self.args = args
        self.rfile = handler.rfile

    def handle(self):
        dict = {"start":self.start, "getmd5":self.getMd5}
        res = dict[self.func](self.args)
        return res

    def start(self, args):
        dst = args[0]
        res = Response("file_transfer","finish")
        f = open(dst, "wb")   
        while True:   
            #data = self.rfile.read(1024)   

            str = self.rfile.read(4)
            if not str: return None
            bytes = int(str)
            data = self.rfile.read(bytes)

            if (data!="TRANSFER FILE END"):
                f.write(data)   
            else:
                break
        f.flush()
        f.close()
        return res

    def getMd5(self, args):
        strFile = args[0]
        file = None 
        bRet = False  
        strMd5 = ""  
        res = Response("file_transfer","getmd5")
          
        try:  
            file = open(r"%s"%strFile, "rb")
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
            res.detail = strMd5
        except:  
            res.err = 1
            bRet = False
        finally:  
            if file:  
                file.close()   
        return res 


print 'server is running....'
server = Server(("",1234), Handler)
server.serve_forever()

