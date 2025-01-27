#!/usr/bin/env python3
# coding=utf-8
import zmq
import numpy as np



class bsp_zmq:
    
    def __init__(self, address="tcp://127.0.0.1:55555", kind="SUB"):
        # ZMQ
        context = zmq.Context()

        if kind == "SUB":
            self.socket = context.socket(zmq.SUB)
            self.socket.connect(address) # connect, not bind, the PUB will bind, only 1 can bind
            self.socket.setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
        else:
            self.socket = context.socket(zmq.PUB)
            # 绑定地址，与 SUB 的连接地址对应
            self.socket.bind(address)
        
    def iswaiting(self):
        return self.socket.poll(10) # check if there is a message on the socket

    def read(self):
        # https://www.cnblogs.com/zhuminghui/p/11359858.html
        return self.socket.recv().decode('latin-1') # grab the message(bytes->str)

    def send(self, message):
        # 将消息编码为字节并发送
        # self.socket.send(message.encode('latin-1'))
        self.socket.send(message)

    def close(self):
        self.socket.close()

