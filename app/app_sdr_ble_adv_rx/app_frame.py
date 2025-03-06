#!/usr/bin/env python
# coding=utf-8

import sys
import termios

sys.path.append('../../bsp')
from bsp_algorithm import bsp_algorithm

# Bluetooth LE constants and definitions
BLE_PREAMBLE = '\xAA'
BLE_ACCESS_ADDR = 0x8e89bed6

BLE_PREAMBLE_LEN = 1
BLE_ADDR_LEN = 4
BLE_PDU_HDR_LEN = 2
BLE_CRC_LEN = 3

BLE_PDU_TYPE = {}
BLE_PDU_TYPE['ADV_IND'] = 0b0000
BLE_PDU_TYPE['ADV_DIRECT_IND'] = 0b0001
BLE_PDU_TYPE['ADV_NONCONN_IND'] = 0b0010
BLE_PDU_TYPE['SCAN_REQ'] = 0b0011
BLE_PDU_TYPE['SCAN_RSP'] = 0b0100
BLE_PDU_TYPE['CONNECT_REQ'] = 0b0101
BLE_PDU_TYPE['ADV_SCAN_IND'] = 0b0110

BLE_CHANS = {37: 0, 0: 1, 1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 
             9: 10, 10: 11, 38: 12, 11: 13, 12: 14, 13: 15, 14: 16, 15: 17, 16: 18, 17: 19, 
             18: 20, 19: 21, 20: 22, 21: 23, 22: 24, 23: 25, 24: 26, 25: 27, 26: 28, 27: 29, 
             28: 30, 29: 31, 30: 32, 31: 33, 32: 34, 33: 35, 34: 36, 35: 37, 36: 38, 39: 39}

class FRAME:

    # REF <BT.xlsx> LL 数据格式
    P_PREAMBLE=0       # 广播固定为 0xAA
    P_ACCESS_ADDRESS=1 # 广播固定为 0x8E89BED6
    P_PDU=5
    P_PDU_HEADER=5
    P_PDU_PAYLOAD=7
    P_PDU_PAYLOAD_ADVA=7
    P_PDU_PAYLOAD_ADVDATA=13
    P_MIN_LEN=16       # 0xAA+0x8E89BED6+HEADER(2)+ADVA(6)+CRC(3)

    MAX_DATA_BUF_SIZE = 300

    def __init__(self,fun_analysis):
        self.data_buf = ""
        self.fun_analysis = fun_analysis


    '''
    judge frame is ok
    '''
    def frame_ok(self,str):
        start_pos = 0
        fram_len = 0
        end_pos = 0

        str_len = len(str)
        if str_len < FRAME.P_MIN_LEN:
            return (-2,start_pos,end_pos)
        
        while start_pos<str_len:
            pos = start_pos
            if(str[pos:].startswith('\xAA\xD6\xBE\x89\x8E')):
                break
            start_pos = start_pos+1

        if(start_pos == str_len):#no find
            return (-1,start_pos,end_pos)
       
        if start_pos + FRAME.P_MIN_LEN < str_len: 
            # Dewhitening received BLE Header
            ble_header      = bsp_algorithm.bt_dewhitening(str[start_pos+FRAME.P_PDU_HEADER:start_pos+FRAME.P_PDU_HEADER+BLE_PDU_HDR_LEN],37)

            ll_pdu_header   = (ble_header[0] << 8) | ble_header[1]
            ll_pdu_type     = ble_header[0] & 0x0f    
            ll_pdu_txadd    = (ble_header[0] >> 6) & 0x01
            ll_pdu_rxadd    = (ble_header[0] >> 7) & 0x01
            ll_pdu_lenght   = ble_header[1] & 0x3f 
          
            head_pos        = start_pos+FRAME.P_PDU_HEADER
            adva_pos        = start_pos+FRAME.P_PDU_PAYLOAD_ADVA
            advdata_pos     = start_pos+FRAME.P_PDU_PAYLOAD_ADVDATA
            crc_pos         = start_pos+FRAME.P_PDU_PAYLOAD_ADVA+ll_pdu_lenght
            end_pos         = start_pos+FRAME.P_PDU_PAYLOAD_ADVA+ll_pdu_lenght+BLE_CRC_LEN

            # Check BLE PDU type
            if ll_pdu_type not in BLE_PDU_TYPE.values():
                # print("Invalid ll_pdu_type: {:x}".format(ll_pdu_type))
                return (-1,start_pos,end_pos)

            if(end_pos < str_len):
                #ll_pdu_payload_adva     = str[head_pos:advdata_pos]
                #ll_pdu_payload_advdata  = str[advdata_pos:crc_pos]
                #ll_pdu_payload_crc      = str[crc_pos:end_pos]
        
                # Dewhitening BLE packet
                self.ble_data      = bsp_algorithm.bt_dewhitening(str[head_pos:crc_pos],37)
                if self.ble_data[-3:] != bsp_algorithm.bt_crc(self.ble_data, 2 + ll_pdu_lenght):
                    if ll_pdu_type == 0:
                        '''
                        print("->head:%04x [T:%02x T:%d R:%d L:%d] adva_pos:%d advdata_pos:%d crc_pos:%d end_pos:%d str_len:%d" \
                                %(ll_pdu_header,ll_pdu_type,ll_pdu_txadd,ll_pdu_rxadd,ll_pdu_lenght, \
                                adva_pos,advdata_pos,crc_pos,end_pos,str_len))
                        for x in self.ble_data:
                            print('%02X ' %x, end = '')
                        print('\n')
                        '''
                        return (0,start_pos,end_pos)
                return (-3,start_pos,end_pos)

        return (-2,start_pos,end_pos)



    '''
    insert data to frame fifo
    '''
    def insert_data(self,data):
        self.data_buf+=data
        if len(self.data_buf) > self.MAX_DATA_BUF_SIZE:
            self.data_buf = ""
        #for x in data:
        #    print('%02X ' %ord(x), end = '')



    '''
    analysis frame and perform  
    '''
    def run(self):
        #while 1<2:
        (ret,start_pos,end_pos) = self.frame_ok(self.data_buf)
        #print (ret,start_pos,end_pos)
        if(ret == 0):
            #self.fun_analysis(self.data_buf[start_pos:end_pos+1])
            self.fun_analysis(self.ble_data)
            self.data_buf = self.data_buf[end_pos:]
        elif(ret == -3):
            self.data_buf = self.data_buf[start_pos+FRAME.P_PDU:]


