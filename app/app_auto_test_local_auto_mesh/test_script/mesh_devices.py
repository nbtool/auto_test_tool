#!/usr/bin/env python3
# coding=utf-8
import subprocess
import threading
import os
import sys
import time
import serial
import termios

from glob import glob


class mesh_devices:
    __device=[]

    def __init__(self,device_exe_path,device_exe_kind,func_log,func_run):
        MAX_DEVICE_NUM = len(device_exe_path)
        device_usb,ret = self.__check_serial_enough(MAX_DEVICE_NUM)
        if ret == 0:
            exit(0)

        for i in range(MAX_DEVICE_NUM):
            print("++++++++++++++++++++++++++++++++++++++++++++++++++")
            print("INIT:",device_exe_path[i],"ttyUSB:",device_usb[i])
            dev=subprocess.Popen("cd "+device_exe_path[i]+"; ./app_main",shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE,env=None,universal_newlines=True,bufsize=1)
            #os.set_blocking(dev.stdout.fileno(), False)
            
            threading.Thread(target=func_log,args=(i,dev)).start()
            
            time.sleep(0.2)   
            dev.stdin.write(str(device_usb[i])+"\n")    # chose ttyUSB 
            dev.stdin.write(device_exe_kind[i]+"\n")    # chose device kind
            dev.stdin.write("i\n")                      # init
            time.sleep(1)

            self.__device.append(dev) 
        
        # start run func
        try:
            threads = [] 
            t1 = threading.Thread(target=func_run)
            threads.append(t1)
    
            for t in threads:
                t.setDaemon(True)
                t.start()
        except e:
            print("safe exit"+str(e))


    # get device
    def device(self):
        return self.__device

    # get pub_address
    def all_get(self):
        print("get all")
        for dev in self.__device:
            dev.stdin.write("g\n")                  
            dev.stdin.flush()
            time.sleep(0.3)
    
    # reset all
    def all_reset(self):
        print("reset all")
        for dev in self.__device:
            dev.stdin.write("r\n")                  
            dev.stdin.flush()
            time.sleep(0.3)

    def run(self):
        MAX_DEVICE_NUM = len(self.__device)
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

        
    def __check_serial_enough(self,device_num):
        ret=subprocess.Popen(['ls','-a']+glob('/dev/ttyUSB*'),shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,universal_newlines=True) 
        usb=ret.stdout.read().rstrip().replace("/dev/ttyUSB","").split('\n')
        num=len(usb)

        if(num == device_num):
            print("device enough: [",','.join(usb),"]")
            return usb,1
        else:
            print("device not enough: [",','.join(usb),"]")
            return usb,0

