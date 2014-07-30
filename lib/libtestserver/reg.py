#coding=utf-8

def regist(node):
    """注册test_server资源"""
    if node.tag == "test_server":
        import test_server 
        return test_server.TestServer(node)
