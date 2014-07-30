#coding=utf-8

from test_station.resource import Resource

class Ixia(Resource):
    """Ixia发包逻辑系统"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "ixia")
        self.__registChildren(node)

    def __registChildren(self, node):
        self.addChild(map(self.libSearch, self.getResources(node)))


def regist(node):
    """注册ixia资源"""
    if node.tag == "ixia":
        return Ixia(node)
