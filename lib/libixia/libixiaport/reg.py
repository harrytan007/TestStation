#coding=utf-8

def regist(node):
    """注册ixia_port资源"""
    if node.tag == "ixia_port":
        import ixia
        return ixia.IxiaPort(node)
