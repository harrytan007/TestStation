#coding=utf-8
#
# Copyright (C) 2013-2014 Harry Tan <tanhy@sugon.com>
# 
# This file is part of logging.

import logging

def log_init(filename):
    """日志功能初始化"""
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename=filename + '.log',
                        filemode='w')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)
    return console

def log(level, message):
    """测试用例脚本和子模块均可调用
       level = 0: 普通信息
       level = 1: 警告信息
       level = 2: 错误信息
       message：日志内容
    """
    if level in [0, 1, 2]:
        if level == 0:
            logging.info(message)
        elif level == 1:
            logging.warning(message)
        elif level == 2:
            logging.error(message)
        return 0
    else:
        print 'Unmatched value of log level...'
        return -1

def log_fake(level, message):
    d = {0:'INFO', 1:'WARNING', 2:'ERROR'}
    if level == 0:
        print '%s     %s' % (d[level], message)
    elif level == 1:
        print '%s  %s' % (d[level], message)
    elif level == 2:
        print '%s    %s' % (d[level], message)

def close(handle):
    handle.close()
