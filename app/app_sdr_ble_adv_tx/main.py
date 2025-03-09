import threading
import sys
import time
import numpy as np
import binascii
import signal
import zmq
import struct
from app_beacon_gen import app_beacon_gen

from grc_hackrf.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
#from grc_plutosdr.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
#from grc_zmq.gr_ble_adv_tx import gr_ble_adv_tx as gr_block

sys.path.append('../../bsp')
import bsp_zmq
import bsp_system

# Initialize Gnu Radio
gr_block = gr_block()
gr_block.start()

zmq1 = bsp_zmq.bsp_zmq("tcp://127.0.0.1:55556", "PUB")
try:
    start_time = time.time()
    interval = 1 #1S 
    count = 0
    
    packed_data = b''
    while 1<2:
        current_time = time.time()
        if count == 0 or current_time - start_time >= interval:
            mac = [1,2,3,4,5,6]
            adv_name = f"hello btfz's gnu-radio {count}"
            adv_datas = [len(adv_name) + 1, 0x09] + [ord(char) for char in adv_name]
            channel = 37
            ll_datas_normalization_sample = app_beacon_gen(mac, adv_datas, channel)

            packed_data = b''
            for data in ll_datas_normalization_sample:
                packed_data += struct.pack("f", data)


            start_time = current_time
            count = count + 1
        

        zmq1.send(packed_data)

except KeyboardInterrupt:
    gr_block.stop()
    gr_block.wait()
    print("safe exit")

