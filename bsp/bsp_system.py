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

version = '0.1'

