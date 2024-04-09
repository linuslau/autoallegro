
import sys
import os
import time
import inspect

from utility.klogger import *

current_milli_time =lambda: int(round(time.time()* 1000))

klogger = KLogger()
logger = klogger.getlog()

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):  # 是否Bundle Resource 捆绑资源
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def function_enter():
    logger.info('--> Enter function: ' + inspect.stack()[1][3])

def function_exit():
    logger.info('<-- Exit function: ' + inspect.stack()[1][3])
    print('')

def function_enter_w_time():
    global function_enter_time
    function_enter_time = current_milli_time()
    logger.info('enter function: ' + inspect.stack()[1][3] + ' @ ' + str(function_enter_time) + 'ms')

def function_exit_w_time():
    global function_enter_time
    function_exit_time = current_milli_time()
    function_enter_exit_time = function_exit_time - function_enter_time
    logger.info('exit function: ' + inspect.stack()[1][3] + ' @ ' + str(function_exit_time) + 'ms' +
          ' (delta: ' + str(function_enter_exit_time) + 'ms)')

def time_checking_start():
    global function_enter_time
    function_enter_time = current_milli_time()
    logger.info('start checking time: ' + str(function_enter_time) + 'ms')

def time_checking_stop():
    global function_enter_time
    function_exit_time = current_milli_time()
    function_enter_exit_time = function_exit_time - function_enter_time
    logger.info('stop checking time: ' + str(function_exit_time) + 'ms' +
          ' (delta: ' + str(function_enter_exit_time) + 'ms)')
