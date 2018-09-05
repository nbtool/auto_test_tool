#!/usr/bin/env python
# coding=utf-8

import time


def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
    data_secs = (ct - long(ct)) * 1000
    time_stamp = "[%s.%03d] " % (data_head, data_secs)
    return time_stamp

def get_time_stamp_ms():
    t = time.time()
    return (int(round(t * 1000)))    #毫秒级时间戳

def get_time_stamp_us():
    t = time.time()
    return (int(round(t * 1000000)))    #微秒级时间戳


version = '0.1'

