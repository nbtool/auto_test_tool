import threading
import app_frame
import sys
import time
import numpy as np

sys.path.append('../../bsp')
import bsp_serial
import bsp_system


def init():
    global ser1

    cmd_wifi_report_state = bytearray([0x55, 0xAA, 0x01, 0x03, 0x00, 0x01, 0x04, 0x08])
    ser1.write(cmd_wifi_report_state); 

def analysis_cmd(str):
    global total_num
    global fail_times

    i = 0
    str_len = len(str)
    cmd1 = ord(str[3])
    if cmd1 != 0x07:
        return;

    node1_id = ord(str[6])
    node2_id = ord(str[10])
    node1_on_off_line = ord(str[7])
    node2_on_off_line = ord(str[11])

    node_id_detect = 0x21
    node_if_detect = 'Y'
    node_on_off_line_detect = 0x00

    print bsp_system.get_time_stamp() ,
    while i<str_len:
        print "%02X" %(ord(str[i])), #ord  char2int
        i=i+1

    if node1_id == node_id_detect:
        node_on_off_line_detect = node1_on_off_line
    elif node2_id == node_id_detect:
        node_on_off_line_detect = node2_on_off_line
    else:
        node_if_detect = 'N'
        print " "
        return

    total_num = total_num + 1
    if node_on_off_line_detect == 0x00:
        fail_times = fail_times + 1
        print "\033[1;35m",
        print "[F],total_num = %05d,fail_times = %05d" %(total_num,fail_times) , 
        print "\33[0m"
    else:
        print " [T],total_num = %05d,fail_times = %05d" %(total_num,fail_times) 

def analysis_cmd2(str):
    global total_num
    global fail_times

    i = 0
    str_len = len(str)
    cmd1 = ord(str[3])
    if cmd1 != 0x07:
        return;

    node1_id = ord(str[6])
    node2_id = ord(str[10])
    node1_flag = ord(str[9])
    node2_flag = ord(str[13])
    node1_on_off_line = ord(str[7])
    node2_on_off_line = ord(str[11])
    
    have_off_line = 0

    if (node1_flag == 0xFF and node1_on_off_line == 0x00) or \
            (node2_flag == 0xFF and node2_on_off_line == 0x00):
        have_off_line = 1

    print bsp_system.get_time_stamp() ,
    while i<str_len:
        print "%02X" %(ord(str[i])), #ord  char2int
        i=i+1
   
    total_num = total_num + 1
    if have_off_line == 1:
        fail_times = fail_times + 1
        print "\033[1;35m",
        print "[F],total_num = %05d,fail_times = %05d" %(total_num,fail_times) , 
        print "\33[0m"
    else:
        print " [T],total_num = %05d,fail_times = %05d" %(total_num,fail_times) 


def ser_receive():
    global ser1
    global frame

    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
            frame.insert_data(x)

def auto_send():
    global ser1
    cmd_change_lum = bytearray([0x55, 0xAA, 0x01, 0x08, 0x00, 0x11, 0xF0, 0x0D, 0x37, 0x22, 0x00, 0xE2, 0x02, 0x01, 0x09, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x04, 0xE0])
    while 1<2:
        #print ">>>>"
        cmd_change_lum[6] = np.random.randint(0,0xFF)
        cmd_change_lum[7] = np.random.randint(0,0xFF) 
        cmd_change_lum[8] = np.random.randint(0,0xFF)
        cmd_change_lum[9] = 0x34
        cmd_change_lum[12] = 0x02
        cmd_change_lum[13] = 0x01
        #cmd_change_lum[20] = np.random.randint(1,100)  #L
        cmd_change_lum[18] = np.random.randint(0,0xff)  #W
        cmd_change_lum[19] = 0xFF - cmd_change_lum[18]  #C
        cmd_change_lum[22] = 0x18  #V
        cmd_change_lum[23] = 0x00
        rand = int(np.sum(cmd_change_lum))
        cmd_change_lum[23] = rand & 0xFF
        ser1.write(cmd_change_lum); 
        time.sleep(0.1)
   


total_num = 0
fail_times = 0
ser1 = bsp_serial.bsp_serial(9600)
frame = app_frame.FRAME(analysis_cmd2)      


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

except Exception, e:
    ser1.close()             # close port
    print("safe exit"+str(e))

