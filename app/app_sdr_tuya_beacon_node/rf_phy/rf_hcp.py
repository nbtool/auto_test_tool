#!/usr/bin/env python
# coding=utf-8
import os
import threading
import time

from rf_alg.alg_base import alg_base

class rf_hcp:

    def __init__(self, mac, hcp_cb):
        self.fifo_tx_path = ".log/device/"+alg_base.to_hexstr(mac,':')+"/my_fifo_tx" 
        self.fifo_rx_path = ".log/device/"+alg_base.to_hexstr(mac,':')+"/my_fifo_rx"
        self.frame = FRAME(hcp_cb)
        
        # 如果管道不存在
        def __create_pipe(pipe_path):
            if not os.path.exists(pipe_path):
                # 检查父文件夹是否存在，如果不存在则创建
                pipe_dir = os.path.dirname(pipe_path)
                if not os.path.exists(pipe_dir):
                    os.makedirs(pipe_dir)
                os.mkfifo(pipe_path)

        __create_pipe(self.fifo_tx_path)
        __create_pipe(self.fifo_rx_path)

        self.fifo_tx = None
        # 创建并启动发送线程(open函数会一直阻塞直到接收端打开，因此用线程维护它）
        sender = threading.Thread(target=self.__sender_thread)
        sender.start()

        # 创建并启动接收线程
        receiver = threading.Thread(target=self.__receiver_thread)
        receiver.start()

    def send(self, cmd, mac, payload):
        if self.fifo_tx != None:
            try:
                msg = self.frame.create(cmd,mac,payload)
                #print(type(msg))
                #for x in msg:
                #    print("%02X" %(x), end = " ")
                #print("\n")
                self.fifo_tx.write(msg)
                self.fifo_tx.flush()  # 立即刷新数据到管道
            except BrokenPipeError:
                # 接收端关闭 pipe 导致 flush 异常，需要关闭 pipe 然后打开
                os.unlink(self.fifo_tx_path)
                self.fifo_tx = open(self.fifo_tx_path, "wb") 

    def run(self):
        self.frame.run() 


    # 发送数据的线程函数
    def __sender_thread(self):
        self.fifo_tx = open(self.fifo_tx_path, "wb")

    # 接收数据的线程函数
    def __receiver_thread(self):
        num = 0
        fifo_rx = open(self.fifo_rx_path, "rb") # 二进制读取
        while True:
            message = fifo_rx.read()
            if len(message) != 0:
                num += 1
                self.frame.insert_data(message)
                # hex_message = ' '.join(['{:02X}'.format(byte) for byte in message])
                # print("R[%d]: %s" %(num, hex_message))
            time.sleep(0.1)  # 间隔1秒接收一次消息


class FRAME:
    P_HEAD=0
    P_MAC=2
    P_CMD=8
    P_LEN=9
    P_PAYLOAD=10
    P_MIN_LEN=12

    MAX_DATA_BUF_SIZE = 1000

    def __init__(self, fun_analysis):
        self.data_buf = b""
        self.fun_analysis = fun_analysis

    def create(self,cmd,mac,payload):
        msg = bytearray([0x55, 0xAA])
        msg.extend(mac)
        msg.append(cmd)
        msg.append(len(payload))
        # 添加 payload
        for item in payload:
            if isinstance(item, str):
                msg.append(ord(item))
            elif isinstance(item, int):
                msg.append(item)
            else:
                raise ValueError("Unsupported type in payload")
        msg.append(0x00) #crc8
      
        return msg #msg.decode('latin1')

    '''
    insert data to frame fifo
    '''
    def insert_data(self,data):
        self.data_buf+=data
        if len(self.data_buf) > self.MAX_DATA_BUF_SIZE:
            self.data_buf = b""

        #hex_message = ' '.join(['{:02X}'.format(byte) for byte in data])
        #print(hex_message)


    '''
    analysis frame and perform
    '''
    def run(self):
        start_pos = 0
        fram_len = 0
        end_pos = 0

        str_len = len(self.data_buf)
        if str_len < FRAME.P_MIN_LEN:
            return (-2,start_pos,end_pos)

        while start_pos<str_len:
            pos = start_pos
            if(self.data_buf[pos:].startswith(b'\x55\xAA')):
                break
            start_pos = start_pos+1

        if(start_pos == str_len):#no find
            return (-1,start_pos,end_pos)

        if start_pos + FRAME.P_MIN_LEN <= str_len: 
            head    = self.data_buf[start_pos+FRAME.P_HEAD:start_pos+FRAME.P_HEAD+2]
            mac     = self.data_buf[start_pos+FRAME.P_MAC:start_pos+FRAME.P_MAC+6]
            cmd     = self.data_buf[start_pos+FRAME.P_CMD:start_pos+FRAME.P_CMD+1][0]
            length   = self.data_buf[start_pos+FRAME.P_LEN:start_pos+FRAME.P_LEN+1][0]
            payload = self.data_buf[start_pos+FRAME.P_PAYLOAD:start_pos+FRAME.P_PAYLOAD+length]
            crc8    = self.data_buf[start_pos+FRAME.P_PAYLOAD+length:start_pos+FRAME.P_PAYLOAD+length+1][0]
            end_pos  = start_pos+FRAME.P_PAYLOAD+length 
            
            print("cmd=%02x mac=[%02X:%02X:%02X:%02X:%02X:%02X] datas[%d]={%s} crc8=%02X" 
                  %(cmd,mac[0],mac[1],mac[2],mac[3],mac[4],mac[5],length, ' '.join(['{:02X}'.format(byte) for byte in payload]), crc8))

            self.fun_analysis(cmd, mac, payload)

 
            #hex_message = ' '.join(['{:02X}'.format(byte) for byte in self.data_buf[start_pos:end_pos + 1]])
            #print("R: %s" % ( hex_message))
            self.data_buf = self.data_buf[end_pos:]



