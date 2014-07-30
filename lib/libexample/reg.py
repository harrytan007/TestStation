#coding=utf-8

from test_station.resource import Resource

class Example(Resource):
    """一体机资源"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "example")
        self.__registChildren(node)

    def __registChildren(self, node):
        self.addChild(map(self.libSearch, self.getResources(node)))


def regist(node):
    """注册资源"""
    if node.tag == "example":
        return Example(node)
