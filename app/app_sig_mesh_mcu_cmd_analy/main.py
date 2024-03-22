#!/usr/bin/env python
# coding=utf-8

import threading
import app_frame
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
0xD1:"get time",
    0xFF:"bt's log"
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
    len2 = ord(buf[5])
    if cmd not in sig_mesh_mcu_cmd_map:
        print "cmd -> 0x%x" %(cmd)       
    elif sig_mesh_mcu_cmd_map[cmd] == "dp upload":
        if len(buf) > 9:
            dpid = ord(buf[6])
            dptype = ord(buf[7])
            dplen = ord(buf[9])
        
            detail = "dpid=0x%x, dptype=%s, dplen=%d, value=[" % (dpid, dp_type_map[dptype], dplen)
            print_color(COLOR_BLUE,sig_mesh_mcu_cmd_map[cmd] + "->" + detail,0)

            print_hexarray(buf,10,dplen)
            print("]")
        else:
            print("ack")  
    elif sig_mesh_mcu_cmd_map[cmd] == "mesh send":
        if len(buf) > 11:
            group_address = ord(buf[6])<<8 | ord(buf[7])
            dpid = ord(buf[8])
            dptype = ord(buf[9])
            dplen = ord(buf[11])
        
            detail = "group_address=0x%x dpid=0x%x, dptype=%s, dplen=%d, value=[" % (group_address, dpid, dp_type_map[dptype], dplen)
            print_color(COLOR_BLUE,sig_mesh_mcu_cmd_map[cmd] + "->" + detail,0)

            print_hexarray(buf,12,dplen)
            print("]")
        else:
            print("ack")
    else:
        print_color(COLOR_BLUE,sig_mesh_mcu_cmd_map[cmd])      

def analysis_cmd2(buf):
    global total_num
    global fail_times

    buf_len = len(buf)

    print bsp_system.get_time_stamp() ,
    if ord(buf[3]) == 0xFF:
        print_color(COLOR_BLUE,"bt's log" + "->", 0)
        print "%s" %(buf[6:-3]) 
    else:
        print_hexarray(buf,0,buf_len)
        cmd_analy(buf)
    
def ser_receive():
    global ser1
    global frame

    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
            frame.insert_data(x)     

ser1 = bsp_serial.bsp_serial(115200)
frame = app_frame.FRAME(analysis_cmd2)      

try:
    threads = [] 
    t1 = threading.Thread(target=ser_receive)
    t2 = threading.Thread(target=frame.run)
    
    threads.append(t1)
    threads.append(t2)   

    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()

except Exception, e:
    ser1.close()             # close port
    print("safe exit"+str(e))

