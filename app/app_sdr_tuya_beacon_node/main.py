#!/usr/bin/env python
# coding=utf-8
import time
import sys
import time
from beacon_node import beacon_node

def hcp_cb(cmd, mac, payload):
    mac = list(mac)
    payload = list(payload)
    if cmd == 0x04:
        if beacon_node.mac == mac:
            channel_num = payload[0]
            tx_configs = []
            for i in range(channel_num):
                index = 1+4*i
                channel_id = payload[index]
                tx_time = (payload[index+1]<<8) | payload[index+2]
                tx_time_srand = payload[index+3]

                tx_window = (channel_id,tx_time,tx_time_srand)
                tx_configs.append(tx_window)

            if len(tx_configs)!= 0:
                datas_len = payload[1+channel_num*4]
                datas = payload[2+channel_num*4:]
                print("> 广播配置: tx_configs =", tx_configs, "datas=", datas)
                # self.tx_config(tx_configs, datas)
                app_beacon_tx.update_datas(beacon_node.mac, datas[8:], 37)

    elif cmd == 0x05:
        if beacon_node.mac == mac:
            op = payload[0]
            timeout = 0
            if op == 2:
                timeout = payload[1]<<8 | payload[2]
            print("> 开启与关闭广播:op=%d, timeout=%d" %(op,timeout))
            if op == 0:
                #app_beacon_tx.stop()
                print("stop")
            else:
                app_beacon_tx.start(1,0xFFFFFFFF)



from rf_sdr.plutosdr_tx_rx import sdr_tx_rx_start

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
    if len(str) == 39:
        if str[8] == 0x02 and str[9] == 0x01 and str[11] == 0x1B and str[12] == 0x03:
            beacon_node.hcp.send(0x06,beacon_node.mac,str)

    return
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
mac = [1,2,3,4,5,6]
channel = 37
app_beacon_tx = app_beacon_tx(zmq_ble_tx.send)
###############################################################
# SDR 收发器启动
sdr_tx_rx_start()

###############################################################
# beacon node 上层应用协议栈
key = "hHbY88bCnLomv3N6A3dVGxntj2u6LRcO"
mac = "DC234FAFDC7A"

beacon_node = beacon_node(mac, key, hcp_cb)

    
###############################################################
# 主循环相关
try:
    while 1<2:
        adv_receive_loop()
        app_beacon_tx.loop()
        beacon_node.run()    

except KeyboardInterrupt:
    zmq_ble_rx.close()             # close port
    gr_ble_rx_block.stop()
    gr_ble_rx_block.wait()

    gr_blt_tx_block.stop()
    gr_blt_tx_block.wait()
    print("main safe exit")
