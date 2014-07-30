#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of test_station.

class EXCEPTION(Exception):
    """平台通用异常类"""
    def __init__(self, level, descr):
        Exception.__init__(self, level, descr)
        self.level = level #异常级别
        self.descr = descr #异常描述


class Err():
    """平台通用错误类"""
    def __init__(self, err_code, detail):
        self.err_code, self.dtl = err_code, detail
