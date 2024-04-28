# -*- coding: utf-8 -*-

import sys
import os

FIVE_VOLTAGE_PATTERN = False

def _init():  # 初始化
    global _global_dict
    _global_dict = {}

def set_value(key, value):
    #定义一个全局变量
    _global_dict[key] = value

def get_value(key):
    #获得一个全局变量，不存在则提示读取对应变量失败
    try:
        return _global_dict[key]
    except:
        print('读取'+key+'失败\r\n')

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource 捆绑资源
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)