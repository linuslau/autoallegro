#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import time
import os
import winreg

from utility.kcaller import *

class KLogger(object):
    '''
封装后的logging
    '''
    cv_saved_log_name = ''
    cv_log_level = ''
    logger_level_dic = {'NOTSET':logging.NOTSET, 'DEBUG':logging.DEBUG, 'INFO':logging.INFO, 'WARN':logging.WARN, 'WARNING':logging.WARNING, 'ERROR':logging.ERROR, 'FATAL':logging.FATAL, 'CRITICAL':logging.CRITICAL}
    def __init__(self, logger_name='', log_level = '', logger_file_name = '', app_name = 'GenericSW',  log_cate='genericSw'):
        '''
            指定保存日志的文件路径，日志级别，以及调用文件
            将日志存入到指定的文件中
        '''
        self.app_name = app_name
        if log_level == '':
            self.logger_level = self.registry_check_logger_level()
        else:
            supported_logger_level = list(KLogger.logger_level_dic.keys())

            log_level_upper = log_level.upper()
            if log_level_upper in supported_logger_level:
                print('logger level set by user is supported: ' + log_level_upper)
                self.logger_level = KLogger.logger_level_dic[log_level_upper]
            else:
                print('logger level set by user is NOT supported: ' + log_level)
                self.logger_level = logging.INFO

        # 创建一个logger
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(self.logger_level)
        if logger_file_name == '':
            if KLogger.cv_saved_log_name == '':
                print('KLogger.cv_saved_log_name NOT set')
                # e.g 2023-01-16_10_07_39
                self.log_time = time.strftime("%Y-%m-%d_%H_%M_%S")
                # data_pat e.g: c:\Users\kliu59\AppData\Roaming\
                data_pat = os.getenv('APPDATA')
                file_dir = os.path.join(data_pat, self.app_name + '\Log')
                if not os.path.exists(file_dir):
                    os.makedirs(file_dir)
                self.log_path = file_dir
                self.saved_log_name = self.log_path + "\\" + log_cate + "_" + self.log_time + '.log'
                KLogger.cv_saved_log_name = self.saved_log_name
                print('set global KLogger.cv_saved_log_name')
                print(KLogger.cv_saved_log_name)
            else:
                print('KLogger.cv_saved_log_name is set, use it')
                print(KLogger.cv_saved_log_name)
                self.saved_log_name = KLogger.cv_saved_log_name
        else:
            print('set filename if requested by caller')
            print('logger_file_name: ' + logger_file_name)
            self.saved_log_name = logger_file_name

        print('====================================================================================>')
        print_caller_by_inspect_depth_2()
        print('logger saved_log_name: ' + self.saved_log_name)
        print('<==================================================================================== \n')

        # 创建一个handler，用于写入日志文件
        # fh = logging.FileHandler(self.saved_log_name, 'a')  # 追加模式  这个是python2的
        fh = logging.FileHandler(self.saved_log_name, 'a', encoding='utf-8')  # 这个是python3的
        fh.setLevel(self.logger_level)

        if not self.logger.handlers:
        #或者使用如下语句判断
        #if not self.logger.hasHandlers():

            # 再创建一个handler，用于输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(self.logger_level)

            # 定义handler的输出格式
            formatter = logging.Formatter(
                '[%(asctime)s][%(name)s][%(module)s][%(levelname)s][%(filename)s(%(lineno)d)->%(funcName)s]%(message)s')
            fh.setFormatter(formatter)
            #ch.setFormatter(formatter)

            # 给logger添加handler
            self.logger.addHandler(fh)
            self.logger.addHandler(ch)

            #  添加下面一句，在记录日志之后移除句柄
            # self.logger.removeHandler(ch)
            # self.logger.removeHandler(fh)
            # 关闭打开的文件
            # fh.close()
            # ch.close()

    def registry_check_logger_level(self):
        print('registry_get_logger_level')
        self.logger_level = logging.INFO

        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 'Software\\' + self.app_name)
            value, type = winreg.QueryValueEx(key, "Logger_Level")
        except Exception as ex:
            print('ex: ' + str(ex))
            value = 'INFO'
            type = 1

        # make sure registry type is string not int
        if type == 1:

            logger_level_registry = value

            supported_logger_level = list(KLogger.logger_level_dic.keys())

            logger_level_registry_upper = logger_level_registry.upper()
            if logger_level_registry_upper in supported_logger_level:
                print('logger level read from registry is supported: ' + logger_level_registry_upper)
                self.logger_level = KLogger.logger_level_dic[logger_level_registry_upper]
            else:
                print('logger level read from registry is NOT supported: ' + logger_level_registry)
                self.logger_level = logging.INFO
                pass
        else:
            self.logger_level = logging.INFO

        return self.logger_level

    def getlog(self):
        return self.logger