import threading
import app_frame
import sys

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

def ser_receive():
    global ser1
    global frame

    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
            frame.insert_data(x)


total_num = 0
fail_times = 0
ser1 = bsp_serial.bsp_serial(9600)
frame = app_frame.FRAME(analysis_cmd)      


try:
    init()

    threads = [] 
    t1 = threading.Thread(target=ser_receive)
    t2 = threading.Thread(target=frame.run)

    threads.append(t1)
    threads.append(t2)   

    for t in threads:
        t.setDaemon(True)
        t.start()

    t.join()

except Exception, e:
    ser1.close()             # close port
    print("safe exit"+str(e))

