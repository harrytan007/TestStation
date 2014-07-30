#coding=utf-8

def regist(node):
    """注册rcp客户端资源"""
    if node.tag == "utils":
        import utils
        return utils.Utils(node)
