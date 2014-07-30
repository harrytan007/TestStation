#coding=utf-8

"""xml数据文件解析模块。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

from xml.etree import ElementTree

from test_station.logging.logger import log
from test_station.err import EXCEPTION

class DataXml():
    """用例数据文件的解析类。
    """
    def __init__(self, xmlfile):
        self.tree = self.__parse(xmlfile) 
        self.root = self.tree.getroot()

    def __parse(self, xmlfile):
        return ElementTree.parse(xmlfile)

    def getTemplate(self):
        """从数据文件中获取模板类型。
        """
        lst = self.tree.findall("template")
        for node in lst:
            return node.text
        return None

    def getLevel(self):
        """从数据文件中获取用例等级。
        """
        lst = self.tree.findall("level")
        for node in lst:
            return int(node.text)
        return None

    def __getResourceDict(self, node):
        """获取资源的字典型数据。
        """
        #判断type属性，如果有指定，例如"int"或者"float"，做出相应的类型转换
        if node.get("type") == "INT":
            text = int(node.text)
        elif node.get("type") == "FLOAT":
            text = float(node.text)
        else:
            text = node.text
        return {node.tag:text}

    def getResource(self, name):
        """从数据文件中获取资源。
        """
        dct = {}
        lst = self.tree.findall("resource/unit")
        num = 0
        exist = False
        for node in lst:
            if node.get("name") == name:
                exist = True
                if node.get("num") == None:
                    num = 0
                elif node.get("num") == "ALL":
                    num = "ALL"
                else:
                    num = int(node.get("num"))
                for child in node.getchildren():
                    if child.tag == "connect":
                        cnt_childs = child.getchildren()
                        if cnt_childs == []:
                            dct.update({child.tag:child.text})
                        else:
                            cnt_dct = {}
                            for cnt_child in cnt_childs:
                                cnt_dct.update(self.__getResourceDict(cnt_child))
                            dct.update({child.tag:cnt_dct})
                    else:
                        dct.update(self.__getResourceDict(child))
        if not exist:
            log(2, 'Resource "%s" is not exist' % name)
            raise EXCEPTION(2, 'Resource "%s" is not exist' % name)
        return [dct, num]

    def getData(self, name):
        """从数据文件中获取外部变量值。
        """
        lst = self.tree.findall("data/item")
        for node in lst:
            if node.get("name") == name:
                type = node.findtext("type")
                value = node.findtext("value")
                if type == "INT":
                    return int(value)
                if type == "BOOL":
                    if value == "True":
                        return True                    
                    elif value == "False":
                        return False
                    else:
                        return None
                elif type == "STRING":
                    return '''"%s"'''%value
                elif type == "LIST":
                    exec("value = [%s]"%value) 
                    return value
                elif type == "FLOAT":
                    return float(value)
                else:
                    return None

if __name__ == "__main__":
    xml = "./demo.xml"
    dx = DataXml(xml)
    lst = dx.getResource("cli")
    print lst
    lst = dx.getResource("wan")
    print lst
    data = dx.getData("dir")
    print data
