#coding=utf-8

def regist(node):
    """注册rcp客户端资源"""
    if node.tag == "rcp_client":
        import rcp
        return rcp.Rcp(node)
