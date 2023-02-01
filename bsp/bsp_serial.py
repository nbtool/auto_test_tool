#!/usr/bin/env python 2.7
# coding=utf-8
import sys
import serial
import subprocess
import termios
import threading

from glob import glob

class bsp_serial:

    def __init__(self,baud_rate):
        #com_num = subprocess.call(['ls','-a']+glob('/dev/ttyUSB*')) 
        ret=subprocess.Popen(['ls','-a']+glob('/dev/ttyUSB*'),shell=False,stdout=subprocess.PIPE,stderr=subprocess.STDOUT) 
        com=ret.stdout.read().rstrip().split('\n')
        #com=ret.args[2:]
        num=len(com)
        
        if(num == 0):
            return 0
        
        com_use = com[0];
        if(num>1):
            print(com)
            index = int(raw_input("enter the num: "))
            if(index >= num):
                return 0
            com_use = com[index]

        print(com_use)

        self.ser = serial.Serial(com_use,
                baud_rate,
                timeout = 0,
                parity = serial.PARITY_NONE,
                rtscts = 0
                )   # open first serial port  
    
    def iswaiting(self):
        return self.ser.inWaiting()

    def read(self):  
        return self.ser.read()

    def write(self,byte_array):
        self.ser.write(byte_array)

    def close(self):
        self.ser.close()

