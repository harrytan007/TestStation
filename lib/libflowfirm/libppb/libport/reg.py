#coding=utf-8

from test_station.resource import Resource

class FlowfirmPort(Resource):
    """Flowfirm端口资源"""
    def __init__(self, node):
        Resource.__init__(self, node.get("name"), "flowfirm_port")
        self.connect = []
        self.__registChildren(node)

    def __registChildren(self, node):
        self.slot_no = int(node.findtext("slot_no"))
        self.if_no = int(node.findtext("if_no")) #端口号
        self.type = node.findtext("type") #端口类型
        self.link = node.findtext("link") #链路，wan或lan
        opb = node.findtext("opb")
        if opb != None:
            self.opb_slot_no = int(opb.split("/")[0]) #对接光保护槽位号
            self.opb_module_no = int(opb.split("/")[1]) #对接光保护模组号

    def get(self):
        """功能：获取端口全称
           输入：无
           输出：端口全称字符串，如'xgei_7/11'
        """
        return '%s_%d/%d' % (self.type, self.slot_no, self.if_no)


def regist(node):
    """注册port资源"""
    if node.tag == "flowfirm_port":
        return FlowfirmPort(node)
