#!/usr/bin/env python3
# coding=utf-8

# Dongle + light
import os, sys, errno
import time

from glob import glob

sys.path.append('../../bsp')
from bsp_file import *
from bsp_string import *

from mesh_devices import *


# get max test case num
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
json_files = bsp_file_search(dirname+'/output/dongle/app_debug/app_debug_local_auto_dongle/test_json/','.json')
MAX_TEST_CASE = len(json_files)

class test_add_cut:
    __device = []

    def __run(self):
        index = 0
        while 1<2:
            time.sleep(2)

            case_num = int((index+1)/2)
            print("xxx->test_add_cut, case[%d]" %case_num)

            if index == 0:
                print("delete all")
                # input d
                self.__device[0].stdin.write("d\n")
                self.__device[0].stdin.flush()
                time.sleep(0.2)   
        
                # input params
                self.__device[0].stdin.write("65535\n") # all autoid
                time.sleep(0.2)   
                self.__device[0].stdin.flush()
                self.__device[0].stdin.write("ffff\n")  # all device
                self.__device[0].stdin.flush()
          
            else:
                if index % 2 == 1:
                    # input c
                    self.__device[0].stdin.write("c\n")
                    self.__device[0].stdin.flush()
                    time.sleep(0.2)   
            
                    # input case num
                    self.__device[0].stdin.write(str(case_num)+"\n")
                    self.__device[0].stdin.flush()
                else:
                    # input d
                    self.__device[0].stdin.write("d\n")
                    self.__device[0].stdin.flush()
                    time.sleep(0.2)   
                     
                    # input params
                    self.__device[0].stdin.write(str(case_num)+"\n") # delete autoid
                    time.sleep(0.2)   
                    self.__device[0].stdin.flush()
                    self.__device[0].stdin.write("ffff\n")  # all device
                    self.__device[0].stdin.flush()

            # case num++
            index = index + 1
            if index > MAX_TEST_CASE:
                index = 0


    def __init__(self):
        device_exe_path=["./output/dongle/bin/","./output/5light/bin/"]
        device_exe_kind=["D","5"]
        self.__device = mesh_devices(device_exe_path,device_exe_kind,self.__log,self.__run).device()
    
    def __log(self,index,dev):
        black_list = ["[dbg]auc_heart","[dbg]hal_uart_send"]
        white_list = ["cmd=a0","cmd=a1","xxx->test_add_cut"]

        print("start read [",index,"] device info")
        while True:
            line = dev.stdout.readline()

            if len(line) == 0:
                continue
            if bsp_string_check_in_str(line,black_list) == 1:
                continue

            if bsp_string_check_in_str(line,white_list) == 1:
                print("device[",index,"]", line, end="")

