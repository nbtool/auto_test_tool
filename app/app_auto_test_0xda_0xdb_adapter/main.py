import threading
import app_auto_test 
import app_frame
import sys

sys.path.append('../../bsp')
import bsp_serial

ser1 = bsp_serial.bsp_serial(9600)
auto_test = app_auto_test.AUTO_PROCESS(ser1.ser)
frame = app_frame.FRAME(auto_test.analysis_cmd)

def ser_receive():
    global ser1
    global frame
    while 1<2:
        if ser1.iswaiting() > 0:
            x = ser1.read()
            frame.insert_data(x)

try:
    threads = [] 
    t1 = threading.Thread(target=ser_receive)
    t2 = threading.Thread(target=frame.run)
    t3 = threading.Thread(target=auto_test.run)

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

