#!/usr/bin/env python3
# coding=utf-8

# https://docs.python.org/3/library/subprocess.html#replacing-os-popen-os-popen2-os-popen3
# https://www.cnblogs.com/yyds/p/7288916.html   Python之系统交互（subprocess）
# https://blog.csdn.net/qq_34355232/article/details/87709418  python中的subprocess.Popen()使用
# https://www.cnblogs.com/monogem/p/11362496.html  python 利用python的subprocess模块执行外部命令，获取返回值
# https://www.cnblogs.com/hardfood/p/15080182.html python subprocess模块调用外部exe控制台程序
# python 利用管道获取可执行交互程序的输出，发现有延时，是由于 c 语言的程序需要将输出缓冲关了：https://www.jianshu.com/p/7639342adbb8

import sys

sys.path.append('./test_script/')
from test_add_max import *  
from test_add_cut import *

# device_exe_path=["./output/dongle/bin/","./output/5light/bin/","./output/pir/bin/","./output/door/bin/","./output/lum/bin/"]
# device_exe_kind=["D","5","p","d","l"]


if __name__=='__main__':
#    t_add_max = test_add_max()
    t_add_cut = test_add_cut()

