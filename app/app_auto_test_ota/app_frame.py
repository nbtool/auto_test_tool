#!/usr/bin/env python
# coding=utf-8

import sys
import termios

class FRAME:
    HEAD1=0
    HEAD2=1
    VERSION=2
    CMD=3
    LEN1=4
    LEN2=5
    LEN_HEAD=6

    MAX_DATA_BUF_SIZE = 1000

    def __init__(self,fun_analysis):
        self.data_buf = ""
        self.fun_analysis = fun_analysis


    '''
    judge frame is ok
    '''
    def frame_ok(self,str):
        start_pos = 0
        fram_len = 0
        end_pos = 0
        str_len = len(str)
        while start_pos<str_len:
            pos = start_pos
            if((ord(str[pos]) == 0xA5) and (pos!=str_len-1) and (ord(str[pos+1]) == 0x5A)):
                break
            start_pos = start_pos+1
        
        if(start_pos == str_len):#no find
            return (-1,start_pos,end_pos)

        if(start_pos + FRAME.LEN_HEAD < str_len):
            #print str_len,start_pos,FRAME.LEN2
            fram_len = (ord(str[start_pos+FRAME.LEN1])<<8) | ord(str[start_pos+FRAME.LEN2])
            end_pos = start_pos + FRAME.LEN_HEAD +fram_len # [) <---
            #print fram_len,end_pos
            if(end_pos <= str_len):
                return (0,start_pos,end_pos)

        return (-2,start_pos,end_pos)



    '''
    insert data to frame fifo
    '''
    def insert_data(self,data):
        self.data_buf+=data
        if len(self.data_buf) > self.MAX_DATA_BUF_SIZE:
            self.data_buf = ""


    '''
    analysis frame and perform  
    '''
    def run(self):
        while 1<2:
            (ret,start_pos,end_pos) = self.frame_ok(self.data_buf)
            #print (ret,start_pos,end_pos)
            if(ret == 0):
                self.fun_analysis(self.data_buf[start_pos:end_pos])
                self.data_buf = self.data_buf[end_pos:]


