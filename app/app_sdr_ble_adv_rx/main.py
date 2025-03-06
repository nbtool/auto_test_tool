import threading
import app_frame
import sys
import time
import numpy as np
import binascii
import signal
import zmq

#from grc.gr_ble import gr_ble as gr_block
#from grc_limesdr.gr_ble import gr_ble as gr_block
#from grc_plutosdr.gr_ble import gr_ble as gr_block
from grc_zmq.gr_ble import gr_ble as gr_block

sys.path.append('../../bsp')
import bsp_zmq
import bsp_system


def analysis_cmd(str):
    print("analysis_cmd:[%02X][%02X]" %(str[0],str[1]),end=' ')
    print("mac:",end = '')
    for d in reversed(str[2:8]):
        print('%02X' %(d), end='')
    print(" data:",end = '')
    for d in str[8:]:
        print('%02X' %(d), end=' ')
    print(' ')


# Initialize Gnu Radio
gr_block = gr_block()
gr_block.start()
gr_block.set_ble_channel(app_frame.BLE_CHANS[37])
zmq1 = bsp_zmq.bsp_zmq("tcp://127.0.0.1:55555")
frame = app_frame.FRAME(analysis_cmd)      

try:
    while 1<2:
        if zmq1.iswaiting() != 0:
            x = zmq1.read()
            frame.insert_data(x)
        frame.run()


except KeyboardInterrupt:
    zmq1.close()             # close port
    gr_block.stop()
    gr_block.wait()
    print("safe exit")

