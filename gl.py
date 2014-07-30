#coding=utf-8
conf = None #全局配置文件的路径
test_conf = None #测试配置文件的路径
resources_conf = None #资源配置文件的路径

class CurrentCase():
    def __init__(self):
        self.dir = None #全局当前测试用例路径 

current_case = CurrentCase()

test_user = None #全局测试用户名 
local_ip = None #全局本地ip
