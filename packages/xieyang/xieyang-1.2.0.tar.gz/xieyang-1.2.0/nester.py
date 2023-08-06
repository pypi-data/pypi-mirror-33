#!/usr/bin/env python-3
# -*- coding:utf-8 -*-
"""这是一个测试模块
   此模块提供了一个print_lol()函数
   这个函数的作用是打印出多重嵌套列表中的每一个基本元素"""
def print_lol(the_list,indent=False,level=0):
    """这个函数需要一个位置参数，可以是简单或复杂的列表
        列表及嵌套列表中的每一个数据项都会输出到屏幕上
        各数据项各占一行,
        第二个参数,表名需要显示的开启缩进功能
        第三个参数用来在遇到嵌套列表时插入制表符，它是可选参数，缺省值为0"""
    for each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_num in range(level):
                    print('\t',end='')    #输出制表符，不换行
            print(each_item)