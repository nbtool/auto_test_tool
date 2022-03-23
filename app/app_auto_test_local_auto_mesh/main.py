#!/usr/bin/env python3
# coding=utf-8

# https://docs.python.org/3/library/subprocess.html#replacing-os-popen-os-popen2-os-popen3
# https://www.cnblogs.com/yyds/p/7288916.html   Python之系统交互（subprocess）
# https://blog.csdn.net/qq_34355232/article/details/87709418  python中的subprocess.Popen()使用
# https://www.cnblogs.com/monogem/p/11362496.html  python 利用python的subprocess模块执行外部命令，获取返回值
# https://www.cnblogs.com/hardfood/p/15080182.html python subprocess模块调用外部exe控制台程序
# python 利用管道获取可执行交互程序的输出，发现有延时，是由于 c 语言的程序需要将输出缓冲关了：https://www.jianshu.com/p/7639342adbb8

import subprocess
import threading
import os
import sys
import time
import serial
import termios

from glob import glob

# python 报错 TypeError: 'module' object is not callable
# https://blog.csdn.net/qq_36853469/article/details/88020901
sys.path.append('./test_script/')
from test_add_max import *  
from test_add_cut import *

sys.path.append('../../bsp/')
from bsp_string import *


cur_path=os.getcwd()


MAX_DEVICE_NUM=5
device=[]
device_usb=[]
device_exe_path=["./output/dongle/bin/","./output/5light/bin/","./output/pir/bin/","./output/door/bin/","./output/lum/bin/"]
device_exe_kind=["D","5","p","d","l"]

# test
t_add_max=test_add_max([],0)
t_add_cut=test_add_cut([],0)


def check_serial_enough():
    ret=subprocess.Popen(['ls','-a']+glob('/dev/ttyUSB*'),shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True) 
    usb=ret.stdout.read().rstrip().replace("/dev/ttyUSB","").split('\n')
    num=len(usb)

    if(num == MAX_DEVICE_NUM):
        print("device enough: [",','.join(usb),"]")
        return usb,1
    else:
        print("device not enough: [",','.join(usb),"]")
        return usb,0
    

def rrun(index,dev):
    global device
    global t_add_max, t_add_cut
    
    print("start read [",index,"] device info")
    while True:
        line = dev.stdout.readline()
        
        if t_add_max.print_log(index,line) == 1:
            print("device[",index,"]", line, end="")

        if t_add_cut.print_log(index,line) == 1:
            print("device[",index,"]", line, end="")

def run():
    global device
    global t_add_max, t_add_cut

    device_usb,ret=check_serial_enough()
    if ret == 0:
        exit(0)

    for i in range(MAX_DEVICE_NUM):
        print("++++++++++++++++++++++++++++++++++++++++++++++++++")
        print("INIT:",device_exe_path[i],"ttyUSB:",device_usb[i])
        dev=subprocess.Popen("cd "+device_exe_path[i]+"; ./app_main",shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,env=None,universal_newlines=True,bufsize=1)
        #os.set_blocking(dev.stdout.fileno(), False)
        

        threading.Thread(target=rrun,args=(i,dev)).start()
        
        time.sleep(0.2)   
        dev.stdin.write(str(device_usb[i])+"\n")    # chose ttyUSB 
        dev.stdin.write(device_exe_kind[i]+"\n")    # chose device kind
        dev.stdin.write("i\n")                      # init
        #dev.stdin.write("r\n")                      # reset
        dev.stdin.write("g\n")                      # get pub_address
        dev.stdin.flush()

        device.append(dev)
        
        time.sleep(1)

    t_add_max = test_add_max([device[0],device[1]],0)
    t_add_cut = test_add_cut([device[0],device[1]],1)

    cur_dev_index = MAX_DEVICE_NUM
    while True:
        xi=input("")
        
        if len(xi) == 1:       
            if cur_dev_index != MAX_DEVICE_NUM:
                device[cur_dev_index].stdin.write(xi+"\n")
                device[cur_dev_index].stdin.flush()
            else:
                index = int(xi)
                if index < MAX_DEVICE_NUM:
                    cur_dev_index = index
                    print("input chose the device[%d], info: %s" %(index,device_exe_path[index]))
                else:
                    print("input index %d should < %d !" %(index,MAX_DEVICE_NUM))
        
        if xi=='chose':    #重新选择一个设备，进行接下来的交互
            cur_dev_index = MAX_DEVICE_NUM
            print("input to chose new device to control...")

        elif xi=='exit':     #设定的结束子进程的条件
            for i in range(MAX_DEVICE_NUM):
                os.kill(device[i].pid,1)
            print("input to exit...")
            break       

if __name__=='__main__':
    run()
