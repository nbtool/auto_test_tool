#!/usr/bin/env python 3
# coding=utf-8
import threading
import app_frame
import sys
import os
import time
import numpy as np

sys.path.append('../../bsp')
import bsp_serial
import bsp_system

CMD = {'WRITE':0x01,'READ':0x02}

# A5 A5 00 CMD LEN1 LEN2 PAYLOAD(OFFSET 4BYTES + SIZE 2BYTES(MAX4K) + DATAS)
def cmd_send(cmd,offset,size,datas):
    global ser1
    global flag_send_ok
    flag_send_ok = 0  
    
    if datas == None:
        data_len = 0
    else:
        data_len = len(datas)
    payload_len = data_len + 6
    buff_len = payload_len + 6
    buff = bytearray(buff_len)
    
    buff[0] = 0xA5
    buff[1] = 0xA5
    buff[2] = 0x00
    buff[3] = cmd
    buff[4] = (payload_len >> 8) & 0xFF
    buff[5] = payload_len & 0xFF
    
    buff[6] = (offset >> 24) & 0xFF
    buff[7] = (offset >> 16) & 0xFF
    buff[8] = (offset >> 8) & 0xFF
    buff[9] = offset & 0xFF
    buff[10] = (size >> 8) & 0xFF
    buff[11] = size & 0xFF
   
    if data_len != 0:
        buff[12:data_len] = datas

    ser1.write(buff) 



def init():
    print("init")

pre_offset = 0x00
def analysis_cmd(str):
    global flag_send_ok
    global pre_offset

    str_len = len(str)
    cmd = ord(str[3])
    if cmd == CMD['WRITE']:
        offset = ord(str[6])<<24 | ord(str[7])<<16 | ord(str[8])<<8 | ord(str[9]) 
        print("%d %d" %(offset,pre_offset))
        if offset - pre_offset != 32:
            if pre_offset != 0:
                print("ERROR!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

        pre_offset = offset
            
        print("WRITE:%d" %(offset))
        flag_send_ok = 1
    elif cmd == CMD['READ']:
        offset = ord(str[6])<<24 | ord(str[7])<<16 | ord(str[8])<<8 | ord(str[9]) 
        size = ord(str[10])<<8 | ord(str[11]) 
        print("READ:[%x-%d]" %(offset,size))
        num = 0
        for i in range(size):
            if num % 16 == 0:
                print(" ")
            print(" %02x" %(ord(str[12+i]))),
            num = num + 1
        print(" ")
    else:
        print("CMD ERROR")

def ser_receive():
    global ser1
    global frame

    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
            frame.insert_data(x)


def write_file(offset = 0x11009000, filepath = 'x.bin'):
    binfile = open(filepath,'rb')
    size = os.path.getsize(filepath)

    #for i in range(72):
    #    data = binfile.read(1)
    #    print("%02x" %ord(data)),

    ba = bytearray(binfile.read())
    #for i in range(72):
    #    print("%02x" %ba[i]),

    #print("\n")
    binfile.close()

    index = 0
    left = size
    data_len = 32
    buff = bytearray(data_len)

    while left > 0:
        if flag_send_ok == 1:
            if left <= 32: # last one 
                data_len = left
            else:
                data_len = 32

            buff[0:data_len] = ba[index*32:data_len]
            offset = 0x11009000 + index*32

            cmd_send(CMD['WRITE'],offset,data_len,buff)
            #print("index:%04d left:%05d" %(index, left))

            left = left - data_len
            index = index + 1
        else:
            cmd_send(CMD['WRITE'],offset,data_len,buff)
            #print("index:%04d left:%05d" %(index, left))

        time.sleep(0.03)

def auto_send():
    global ser1
    global sn
    global flag_send_ok

    while 1<2:
        print("\n> input:([W]:write,[R]:read,[WF]:write file,[Q]:quit)")
        x = raw_input(">")   
        if x == "W":
            print("write")
        elif x == "R":
            offset = int(raw_input("|- input offset(hex):"), 0)
            size = int(raw_input("|- input size(int <= 256):"), 0)
            cmd_send(CMD['READ'],offset,size,None)
        elif x == "WF":
            write_file(0x11009000,"x.bin")
        elif x == "Q":
            exit(1)
        else:
            print("input error")

        time.sleep(0.1)
   


ser1 = bsp_serial.bsp_serial(115200)
frame = app_frame.FRAME(analysis_cmd)      
sn = 1

flag_send_ok = 1
flag_read_ok = 1


try:
    init()

    threads = [] 
    t1 = threading.Thread(target=ser_receive)
    t2 = threading.Thread(target=frame.run)
    t3 = threading.Thread(target=auto_send)

    threads.append(t1)
    threads.append(t2)   
    threads.append(t3)   

    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()

except e:
    ser1.close()             # close port
    print("safe exit"+str(e))

