#!/usr/bin/env python
#coding:utf-8

import sys
import inspect


# usage: in caller place
# frame = inspect.stack()[1][0]
# print(get_class_from_frame(frame))
def get_class_from_frame(fr):
  args, _, _, value_dict = inspect.getargvalues(fr)
  # we check the first parameter for the frame function is
  # named 'self'
  if len(args) and args[0] == 'self':
    # in that case, 'self' will be referenced in value_dict
    instance = value_dict.get('self', None)
    if instance:
      # return its class
      return getattr(instance, '__class__', None)
  # return None otherwise
  return None


def print_caller_by_sys():
    # 获取被调用函数所在模块文件名
    print(sys._getframe(1).f_code.co_filename)

    # 获取被调用函数名称
    print(sys._getframe(1).f_code.co_name)

    # 获取被调用函数在被调用时所处代码行数
    print(sys._getframe(1).f_lineno)

def print_caller_by_inspect():
    # 获取被调用函数所在模块文件名
    print(inspect.stack()[1][1])

    # 获取被调用函数名称
    print(inspect.stack()[1][3])

    # 获取被调用函数在被调用时所处代码行数
    print(inspect.stack()[1][2])

def print_caller_by_inspect_depth_2():
    #stack = inspect.stack()
    #frame = inspect.stack()[1][0]

    # 获取被调用函数所在模块文件名
    print(inspect.stack()[2][1])

    # 获取被调用函数名称
    print(inspect.stack()[2][3])

    # 获取被调用函数在被调用时所处代码行数
    print(inspect.stack()[2][2])

# 定义为注解，方便调试具体函数
def show_caller(level=1):
    def show(func):
        def wrapper(*args, **kwargs):
            func(*args, **kwargs)
            print('{0.f_code.co_filename}:{0.f_code.co_name}:{0.f_lineno}'.format(sys._getframe(level)))
        return wrapper
    return show

@show_caller(1)
def main():
    print_caller_by_sys()
    print_caller_by_inspect()

if __name__ == '__main__':
    main()