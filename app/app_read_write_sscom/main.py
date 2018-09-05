import threading
import sys
import time
import numpy as np

sys.path.append('../../bsp')
import bsp_serial
import bsp_system


def buf_print(buf):
    buf_len = len(buf)
    i = 0

    print bsp_system.get_time_stamp() ,
    while i < buf_len:
        print "%02X" %(ord(buf[i])), #ord  char2int
        i=i+1   
    print " "

    
def ser_receive():
    global ser1

    timestamp_pre = 0
    buf = ""

    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
       
            timestamp_curr = bsp_system.get_time_stamp_us()
            if timestamp_pre == 0:
                timestamp_pre = timestamp_curr
            elif timestamp_curr - timestamp_pre > 2000:
#print " "
                buf_print(buf)
                buf = ""
                timestamp_pre = 0
            else:
#print "%d" %(timestamp_curr-timestamp_pre),
                timestamp_pre = timestamp_curr
     
            buf+=x


ser1 = bsp_serial.bsp_serial(9600)

try:
    threads = [] 
    t1 = threading.Thread(target=ser_receive)
    threads.append(t1)

    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()

except Exception, e:
    ser1.close()             # close port
    print("safe exit"+str(e))

