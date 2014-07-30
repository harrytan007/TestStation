#coding=utf-8

def regist(node):
    """注册reflow资源"""
    if node.tag == "reflow":
        import reflow
        return reflow.Reflow(node)
