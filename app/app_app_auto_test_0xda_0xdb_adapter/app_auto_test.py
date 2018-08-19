#!/usr/bin/env python
# coding=utf-8
import sys
import termios
import subprocess
import time
import numpy as np

from glob import glob
from app_frame import FRAME


sys.path.append('../../bsp')
import bsp_system

'''
auto = 0   发送cmd 2 ble
auto = 1   等待ble回复（立即回复）
auto = 2   灯带ble回复2（mesh网络数据收集完毕再回复)
auto = other 一个测试周期完毕
'''
'''
55 AA 01 08 00 09 F0 0D 37 AE 00 DA 02 01 10 E0
55 AA 01 09 00 0F AE 00 DB 02 01 80 80 80 6A 95 22 00 1C 00 00 61

55 AA 01 08 00 09 F0 0D 38 AE 00 DA 02 01 10 E1
55 AA 01 09 00 0F AE 00 DB 02 01 80 80 80 6A 95 22 00 1C 00 00 61
'''
class AUTO_PROCESS:
    START=0
    PROCESS1=1
    PROCESS2=2
    FINISH=3

    auto = START

    def __init__(self,ser):
        self.auto = AUTO_PROCESS.START
        self.ser = ser

    '''
    print or analy frame
    '''
    def analysis_cmd(self,str):
        i = 0
        str_len = len(str)
        cmd1 = ord(str[FRAME.CMD])
       
        print bsp_system.get_time_stamp() ,

        if cmd1 == 0x08:
            print "\033[1;34m>> \033[0m",
            self.auto = self.PROCESS2

        if cmd1 == 0x09:
            print "\033[1;35m>< \033[0m",
            self.auto = self.FINISH

        while i<str_len:
            print "%02X" %(ord(str[i])), #ord  char2int
            i=i+1

        print " "


    '''
    auto test run thread
    '''
    def run(self):
        cmd_get_status_all = bytearray([0x55, 0xAA, 0x01, 0x08, 0x00, 0x09, 0xF0, 0x0D, 0x37, 0xAE, 0x00, 0xDA, 0x02, 0x01, 0x10, 0xE0])
        cmd_wifi_report_state = bytearray([0x55, 0xAA, 0x01, 0x03, 0x00, 0x01, 0x04, 0x08])

        #ser.write(cmd_wifi_report_state); 
       
        all_times = 0
        fail1_times = 0
        fail2_times = 0

        while 1<2:
            if self.auto == self.START:
                all_times = all_times + 1
                time.sleep(2)
                cmd_get_status_all[6] = np.random.randint(0, 0xFF) 
                cmd_get_status_all[7] = np.random.randint(0, 0xFF) 
                cmd_get_status_all[8] = np.random.randint(0, 0xFF) 
                cmd_get_status_all[9] = 0x21
                cmd_get_status_all[12] = 0x04
                cmd_get_status_all[13] = 0x01
                cmd_get_status_all[15] = 0x00 
                rand = int(np.sum(cmd_get_status_all))
                cmd_get_status_all[15] = rand & 0xFF
                #for i in cmd_get_status_all:
                #    print '%02X' %i ,
                #print " "
                #print "%02X %02X" %(rand,cmd_get_status_all[15])

                self.ser.write(cmd_get_status_all) 
                self.auto = AUTO_PROCESS.PROCESS1
                time.sleep(2)
            elif self.auto == self.PROCESS1:
                fail1_times = fail1_times + 1
                print "fail %d" %self.auto
                self.auto = self.START
            elif self.auto == self.PROCESS2:
                fail2_times = fail2_times + 1
                print "fail %d" %self.auto
                self.auto = self.START
            else:
                print "success %d total:%d fail1:%d fail2:%d" %(self.auto,all_times,fail1_times,fail2_times)
                self.auto = self.START


