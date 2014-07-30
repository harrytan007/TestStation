#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of keyword.

"""关键字脚本解析模块。
"""

__authors__ = [
    '"Harry Tan" <tanhy@sugon.com>'
]

import re
import types

import buildin
import dataxml 

class Stack():
    """用于控制缩进的堆栈类。
    """
    def __init__(self):
        self.stack = []
    def push(self,object):
        self.stack.append(object)
    def pop(self):
        return self.stack.pop()
    def length(self):
        return len(self.stack)


class Keyword():
    """关键字脚本处理类，将关键字脚本翻译成标准Python脚本。
    """
    def __init__(self, template, txt, xml, dir):
        self.template = template
        self.dir = dir
        self.txt = txt
        self.xml = xml

        self.lines = self.__getLines(self.txt)
        self.__setIndent(self.lines)
        self.__txt2py(self.lines)
    
    def __getLines(self, txt):
        """加载txt脚本中的所有行。
        """
        fp = open("%s"%txt, "r")
        lines = fp.readlines()
        new_lines = []
        for i in range(0, len(lines)):
            ln = Line(lines[i], self.xml)
            ln.line_no = i+1 #加载行号
            if ln.type == "exec":
                new_lines.append(ln)
        fp.close()
        return new_lines

    def __setIndent(self, lines):
        """更新所有行的缩进量。
        """
        lst = []
        for_stack = Stack()
        while_stack = Stack()
        if_stack = Stack()
        for i in range(0,len(lines)):
            word = lines[i].words[0]
            if word == "FOR":
                for_stack.push(i)
            if word == "ENDFOR":
                lst.append([for_stack.pop(), i])
            if word == "WHILE":
                while_stack.push(i)
            if word == "ENDWHILE":
                lst.append([while_stack.pop(), i])
        for i in range(0,len(lines)):
            block_lst = []
            word = lines[i].words[0]
            if word == "IF":
                if_stack.push([i,"IF"])
            if word == "ELIF":
                if_stack.push([i,"ELIF"])
            if word == "ELSE":
                if_stack.push([i,"ELSE"])
            if word == "ENDIF":
                if_stack.push([i,"ENDIF"])
                if_lst = [None, None]
                while if_lst[1] != "IF":
                    if_lst = if_stack.pop()
                    block_lst.append(if_lst[0])
                lst.append(block_lst[::-1])
        for block in lst:
            full = range(block[0],block[-1]+1)
            for x in block:
                full.remove(x) 
            for x in full:
                lines[x].indent += 4

    def __txt2py(self, lines): 
        """将txt脚本转成py源码。
        """
        for line in lines:
            raw_py = line.line2py(line.words)
            if raw_py != "":
                line.line_py = " "*line.indent + raw_py + "\n"

    def gen(self, dst_file):
        """生成最终py文件。
        """
        pygo = []
        
        #列表重组
        for line in self.lines:
            if line.line_py != "":
                pygo.append(line.line_py)
        #生成py文件
        fo = open("%s"%dst_file, 'w')
        fo.writelines([self.template]+pygo)
        fo.close()

                    
class Line():
    """行类。
    """
    def __init__(self, raw_line, xml):
        self.line = raw_line.strip().replace('$','').rstrip('\n') #修剪后
        self.line_no = None #行号
        self.type = None #行语句类型，"comment", "exec", "null"
        self.line_py = "" #解释后的Python语句
        self.words = [] #关键字实例集
        self.indent = 8 #缩进
        self.xml = xml

        self.type = self.__getType(self.line)
        self.words = self.__getWords(self.line)

    def __getType(self, line):
        """分析并获取行类型。
        """
        if line == '':
            return "null"
        elif line[0] == "#":
            return "comment" 
        else:
            self.line = self.line.split("#")[0]
            return "exec"

    def __getPureWords(self, pure_line):
        return pure_line.split()

    def __getWords(self, line):
        """提取一行中的关键字。
        """
        if self.type != "exec":
            return []
        else:
            lst = []
            while(True):
                braces = re.search(r"{([^}]+)}", line) #大括号
                double_quotations = re.search(r"\"([^\"]+)\"", line) #双引号
                brackets = re.search(r"\s\[(.*)\]", line) #方括号
                #如果存在{}或""或[]
                if braces != None or double_quotations != None or brackets != None:
                    #如果存在{}
                    if braces != None:
                        braces_index = line.index(braces.group(0))
                    else:
                        braces_index = 100000
                    #如果存在""
                    if double_quotations != None:
                        double_quotations_index = line.index(double_quotations.group(0))
                    else:
                        double_quotations_index = 100000
                    #如果存在[]
                    if brackets != None:
                        brackets_index = line.index(brackets.group(0))
                    else:
                        brackets_index = 100000

                    m = min(braces_index,double_quotations_index,brackets_index)
                    if m == braces_index:
                        tmp = line.partition(braces.group(0))
                        lst = lst + self.__getPureWords(tmp[0]) + [Line(braces.group(1), self.xml)]
                        line = tmp[2]
                    elif m == double_quotations_index:
                        tmp = line.partition(double_quotations.group(0))
                        tmp2 = tmp[2]
                        group = double_quotations.group(0)
                        if len(tmp[2])>0:
                            if tmp[2][0:2] == "%(":
                                group = group + tmp[2].partition(" ")[0]
                                tmp2 = tmp[2].partition(" ")[2]
                        lst = lst + self.__getPureWords(tmp[0]) + [group]
                        line = tmp2
                    elif m == brackets_index:
                        tmp = line.partition(brackets.group(0))
                        lst = lst + self.__getPureWords(tmp[0]) + [brackets.group(0).strip().replace("$", "")]
                        line = tmp[2]
                else:
                    lst = lst + self.__getPureWords(line)
                    break
            return lst

    def line2py(self, words):
        """将一行内容转成py源码。
        """
        if words[0] == "SET":
            if type(words[2]) == types.InstanceType:
                return buildin.set(words[1], "("+self.line2py(words[2].words)+")")
            else:
                return buildin.set(words[1], words[2])
        elif words[0] == "GET":
            return buildin.get(words[1], words[2])
        elif words[0] == "FOR":
            str = "for "
            if words[1].__class__.__name__ == "Line":
                str += "(%s) "%self.line2py(words[1])
            else:
                str += "%s "%words[1]
            if words[2] == "IN":
                str += "in "
            m = re.search(r"\[([^\]]+)\]", words[3])
            if "~" in words[3]:
	        range = words[3].split("~")
                def getRangePoint(point):
                    return int(point) if point.isdigit() else point.strip("$")
                str += "range(%s, %s+1):"%(getRangePoint(range[0]), getRangePoint(range[1]))
            elif m != None:
                str += "%s:"%words[3]
            else:
                str += "%s:"%words[3]
            return str
        elif words[0] == "ENDFOR":
            return ""
        elif words[0] == "IF":
            str = "if "
            if len(words) > 1:
                if words[1].__class__.__name__ == "Line":
                    str += "(%s)"%self.line2py(words[1].words)
                else:
                    str += words[1]
            if len(words) > 3:
                if words[2] == "AND":
                    str += " and "
                elif words[2] == "OR":
                    str += " or "
                if words[3].__class__.__name__ == "Line":
                    str += "(%s)"%self.line2py(words[3].words)
                else:
                    str += words[1]
            str += ":"
            return str
        elif words[0] == "ELIF":
            str = "elif "
            if len(words) > 1:
                if words[1].__class__.__name__ == "Line":
                    str += "(%s)"%self.line2py(words[1].words)
                else:
                    str += words[1]
            if len(words) > 3:
                if words[2] == "AND":
                    str += " and "
                elif words[2] == "OR":
                    str += " or "
                if words[3].__class__.__name__ == "Line":
                    str += "(%s)"%self.line2py(words[3].words)
                else:
                    str += words[1]
            str += ":"
            return str
        elif words[0] == "ELSE":
            return "else:"
        elif words[0] == "ENDIF":
            return ""
        elif words[0] == "WHILE":
            str = "while "
            if len(words) > 1:
                if words[1].__class__.__name__ == "Line":
                    str += "(%s)"%self.line2py(words[1].words)
                else:
                    str += words[1]
            if len(words) > 3:
                if words[2] == "AND":
                    str += " and "
                elif words[2] == "OR":
                    str += " or "
                if words[3].__class__.__name__ == "Line":
                    str += "(%s)"%self.line2py(words[3].words)
                else:
                    str += words[1]
            str += ":"
            return str
        elif words[0] == "ENDWHILE":
            return ""
        elif words[0] == "ADD":
            return buildin.add(words[1], words[2])
        elif words[0] == "SUB":
            return buildin.sub(words[1], words[2])
        elif words[0] == "MUL":
            return buildin.mul(words[1], words[2])
        elif words[0] == "DIV":
            return buildin.div(words[1], words[2])
        elif words[0] == "GT":
            return buildin.gt(words[1], words[2])
        elif words[0] == "LT":
            return buildin.lt(words[1], words[2])
        elif words[0] == "EQ":
            return buildin.eq(words[1], words[2])
        elif words[0] == "NEQ":
            return buildin.neq(words[1], words[2])
        elif words[0] == "RESOURCE":
            return buildin.resource(words[1], self.xml)
        elif words[0] == "DATA":
            return buildin.data(words[1], self.xml)
        elif words[0] == "REPORT":
            return buildin.report(words[1], words[2])
        elif words[0] == "EXPECT":
            return buildin.expect(words[1], words[2], words[3])
        elif words[0] == "FATALEXPECT":
            return buildin.fatalExpect(words[1], words[2], words[3])
        elif words[0] == "RUN":
            str = ""
            for word in words[3:]:
                if word.__class__.__name__ == "Line":
                    str += self.line2py(word.words) + ","
                else: 
                    str += word + ","
            return "%s.%s(%s)"%(words[1],words[2],str.strip(","))
        else:
            print "line error: %s"%words
            return ""
           
if __name__ == "__main__":
    t2p = Keyword("demo.txt", "demo.xml", "./")
    t2p.gen("demo.py")
