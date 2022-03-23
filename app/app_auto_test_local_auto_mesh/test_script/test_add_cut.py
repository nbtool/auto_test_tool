#!/usr/bin/env python3
# coding=utf-8

# Dongle + light
import threading
import subprocess
import os, sys, errno
import time

from glob import glob

sys.path.append('../../bsp')
from bsp_file import *
from bsp_string import *


# get max test case num
dirname, filename = os.path.split(os.path.abspath(sys.argv[0]))
json_files = bsp_file_search(dirname+'/output/dongle/app_debug/app_debug_local_auto_dongle/test_json/','.json')
MAX_TEST_CASE = len(json_files)


class test_add_cut:
    device = []
    en = 0

    def run(self):
        index = 0
        while 1<2:
            time.sleep(2)

            case_num = int((index+1)/2)
            print("xxx->test_add_cut, case[%d]" %case_num)

            if index == 0:
                print("delete all")
                # input d
                self.device[0].stdin.write("d\n")
                self.device[0].stdin.flush()
                time.sleep(0.2)   
        
                # input params
                self.device[0].stdin.write("65535\n") # all autoid
                time.sleep(0.2)   
                self.device[0].stdin.flush()
                self.device[0].stdin.write("ffff\n")  # all device
                self.device[0].stdin.flush()
          
            else:
                if index % 2 == 1:
                    # input c
                    self.device[0].stdin.write("c\n")
                    self.device[0].stdin.flush()
                    time.sleep(0.2)   
            
                    # input case num
                    self.device[0].stdin.write(str(case_num)+"\n")
                    self.device[0].stdin.flush()
                else:
                    # input d
                    self.device[0].stdin.write("d\n")
                    self.device[0].stdin.flush()
                    time.sleep(0.2)   
                     
                    # input params
                    self.device[0].stdin.write(str(case_num)+"\n") # delete autoid
                    time.sleep(0.2)   
                    self.device[0].stdin.flush()
                    self.device[0].stdin.write("ffff\n")  # all device
                    self.device[0].stdin.flush()

            # case num++
            index = index + 1
            if index > MAX_TEST_CASE:
                index = 0


    def __init__(self,dev,en):
        if len(dev) == 0 or en == 0:
            return 

        self.device = dev
        self.en = 1

        try:
            threads = [] 
            t1 = threading.Thread(target=self.run)

            threads.append(t1)
    
            for t in threads:
                t.setDaemon(True)
                t.start()

        except e:
            print("safe exit"+str(e))

    
    def print_log(self,index,line):
        black_list = ["[dbg]auc_heart","[dbg]hal_uart_send"]
        white_list = ["cmd=a0","cmd=a1","xxx->test_add_cut"]

        if len(line) == 0 or self.en == 0:
            return 0
        
        if bsp_string_check_in_str(line,black_list) == 1:
            return 0

        if bsp_string_check_in_str(line,white_list) == 1:
            return 1
        
