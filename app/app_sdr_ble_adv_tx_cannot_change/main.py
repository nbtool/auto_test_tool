import threading
import sys
import time
import numpy as np
import binascii
import signal
import zmq

#from grc_hackrf.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
#from grc_plutosdr.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
from grc_zmq.gr_ble_adv_tx import gr_ble_adv_tx as gr_block


# Initialize Gnu Radio
gr_block = gr_block()
gr_block.start()
   
try:
    while 1<2:
        time.sleep(1)


except KeyboardInterrupt:
    gr_block.stop()
    gr_block.wait()
    print("safe exit")

