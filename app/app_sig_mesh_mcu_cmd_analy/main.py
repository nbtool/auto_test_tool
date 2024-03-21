#!/usr/bin/env python
# coding=utf-8

import threading
import sys
import time
import numpy as np

sys.path.append('../../bsp')
import bsp_serial
import bsp_system

# ANSI 转义码定义
COLOR_RED = '\033[91m'
COLOR_GREEN = '\033[92m'
COLOR_YELLOW = '\033[93m'
COLOR_BLUE = '\033[94m'
COLOR_PURPLE = '\033[95m'
COLOR_CYAN = '\033[96m'
COLOR_WHITE = '\033[97m'
COLOR_RESET = '\033[0m'

dp_type_map = {
    0x00:"raw",
    0x01:"bool",
    0x02:"value",
    0x03:"string",
    0x04:"enum",
    0x05:"bitmap"
}

sig_mesh_mcu_cmd_map = {
    0x00:"heart",
    0x01:"get mcu info",
    0x03:"status",
    0x04:"reset",
    0x06:"dp download",
    0x07:"dp upload",
    0x08:"query",
    0x09:"dp upload with ack",
    0x0B:"dp upload ack",
    0x0E:"rf test",
    0xE5:"enable low power",
    0xA1:"enable pre control",
    0xB0:"remoter data notify",
    0xA2:"pre control data notify",
    0xB1:"enable mesh",
    0xB2:"mesh send",
    0xB3:"get pub address",
    0xB4:"get group address",
    0xB5:"local pair",
    0xB6:"open pair window",
    0xB7:"set favorite",
    0xB8:"be setted favorite notify",
    0xBC:"sig model send",
    0xBD:"sig model receive",
    0xBE:"vendor model send",
    0xBF:"vendor model reveive",
    0xD1:"get time"
}

# 带颜色的打印函数
def print_color(color, message, end=1):
    if end == 1:
        print color + message + COLOR_RESET
    else:
        print color + message + COLOR_RESET ,

def print_hexarray(buf,pos,len):
    i = 0
    while i < len:
        print "%02X" %(ord(buf[i+pos])), #ord  char2int
        i=i+1   

def cmd_analy(buf):
    cmd = ord(buf[3])
    len = ord(buf[5])
    if sig_mesh_mcu_cmd_map[cmd] == "dp upload":
        dpid = ord(buf[6])
        dptype = ord(buf[7])
        dplen = ord(buf[9])
    
        detail = "dpid=%x, dptype=%s, dplen=%d, value=[" % (dpid, dp_type_map[dptype], dplen)
        print_color(COLOR_BLUE,sig_mesh_mcu_cmd_map[cmd] + "->" + detail,0)

        print_hexarray(buf,10,dplen)
        print("]")
    else:
        print_color(COLOR_BLUE,sig_mesh_mcu_cmd_map[cmd])      

def buf_print(buf):
    buf_len = len(buf)
    i = 0

    print bsp_system.get_time_stamp() ,
    print_hexarray(buf,0,buf_len)
    
    cmd_analy(buf)
    
def ser_receive():
    global ser1

    timestamp_pre = 0
    buf = ""

    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
       
            timestamp_curr = bsp_system.get_time_stamp_us()
            if timestamp_pre == 0:
                timestamp_pre = timestamp_curr
            elif timestamp_curr - timestamp_pre > 2000:
#print " "
                buf_print(buf)
                buf = ""
                timestamp_pre = 0
            else:
#print "%d" %(timestamp_curr-timestamp_pre),
                timestamp_pre = timestamp_curr
     
            buf+=x


ser1 = bsp_serial.bsp_serial(115200)

try:
    threads = [] 
    t1 = threading.Thread(target=ser_receive)
    threads.append(t1)

    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()

except Exception, e:
    ser1.close()             # close port
    print("safe exit"+str(e))

