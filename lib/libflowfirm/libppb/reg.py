#coding=utf-8

from test_station.resource import Resource

class FlowfirmPpb(Resource):
    """一体机板卡资源"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "flowfirm_ppb")
        self.__registChildren(node)

    def __registChildren(self, node):
        self.addChild(map(self.libSearch, self.getResources(node)))


def regist(node):
    """注册PPB资源"""
    if node.tag == "flowfirm_ppb":
        return FlowfirmPpb(node)
