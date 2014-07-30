#coding=utf-8

from test_station.resource import Resource

class Flowfirm(Resource):
    """一体机资源"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "flowfirm")
        self.__registChildren(node)

    def __registChildren(self, node):
        self.addChild(map(self.libSearch, self.getResources(node)))


def regist(node):
    """注册一体机资源"""
    if node.tag == "flowfirm":
        return Flowfirm(node)
