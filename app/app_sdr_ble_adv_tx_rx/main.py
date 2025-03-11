#!/usr/bin/env python
# coding=utf-8
import threading
import sys
import time
import numpy as np
import binascii
import signal
import zmq
import struct

from plutosdr_tx_rx import sdr_tx_rx_start

sys.path.append('../app_sdr_ble_adv_rx')
import app_frame
from grc_zmq.gr_ble import gr_ble as gr_ble_rx_block

sys.path.append('../app_sdr_ble_adv_tx')
from app_beacon_tx import app_beacon_tx
from grc_zmq.gr_ble_adv_tx import gr_ble_adv_tx as gr_blt_tx_block

sys.path.append('../../bsp')
import bsp_zmq

###############################################################
# 接收相关
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
gr_ble_rx_block = gr_ble_rx_block()
gr_ble_rx_block.start()
gr_ble_rx_block.set_ble_channel(app_frame.BLE_CHANS[37])
zmq_ble_rx = bsp_zmq.bsp_zmq("tcp://127.0.0.1:55555")
frame = app_frame.FRAME(analysis_cmd)      

def adv_receive_loop():
    if zmq_ble_rx.iswaiting() != 0:
        x = zmq_ble_rx.read()
        frame.insert_data(x)
    frame.run()

###############################################################
# 发送相关
gr_blt_tx_block = gr_blt_tx_block()
gr_blt_tx_block.start()
zmq_ble_tx = bsp_zmq.bsp_zmq("tcp://127.0.0.1:55556", "PUB")
count = 0
mac = [1,2,3,4,5,6]
channel = 37
def gen_adv_datas(count):
    adv_name = f"hello btfz's gnu-radio {count}"
    adv_datas = [len(adv_name) + 1, 0x09] + [ord(char) for char in adv_name]
    return adv_datas

app_beacon_tx = app_beacon_tx(zmq_ble_tx.send)
adv_datas = gen_adv_datas(count)
app_beacon_tx.update_datas(mac, adv_datas, channel)
app_beacon_tx.start(1,0xFFFFFFFF)

adv_change_start_time = time.time()
def adv_datas_change():
    global adv_change_start_time, count
    current_time = time.time()
    if current_time - adv_change_start_time >= 1: #1S
        count = count + 1
        adv_datas = gen_adv_datas(count)           
        app_beacon_tx.update_datas(mac, adv_datas, channel)
        adv_change_start_time = current_time

###############################################################
# SDR 收发器启动
sdr_tx_rx_start()

###############################################################
# 主循环相关
try:
    while 1<2:
        adv_receive_loop()
        app_beacon_tx.loop()
        adv_datas_change()

except KeyboardInterrupt:
    zmq_ble_rx.close()             # close port
    gr_ble_rx_block.stop()
    gr_ble_rx_block.wait()

    gr_blt_tx_block.stop()
    gr_blt_tx_block.wait()
    print("main safe exit")

