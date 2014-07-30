#coding=utf-8

from test_station.resource import Resource

class Switch(Resource):
    """交换机资源"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "switch")
        self.connect = []


def regist(node):
    """注册switch资源"""
    if node.tag == "switch":
        return Switch(node)
