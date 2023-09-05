#!/usr/bin/env python3
# coding=utf-8
import zmq
import numpy as np



class bsp_zmq:
    
    def __init__(self,address="tcp://127.0.0.1:55555"):
        # ZMQ
        context = zmq.Context()
        self.socket = context.socket(zmq.SUB)
        self.socket.connect(address) # connect, not bind, the PUB will bind, only 1 can bind
        self.socket.setsockopt(zmq.SUBSCRIBE, b'') # subscribe to topic of all (needed or else it won't work)
    
    def iswaiting(self):
        return self.socket.poll(10) # check if there is a message on the socket

    def read(self):
        # https://www.cnblogs.com/zhuminghui/p/11359858.html
        return self.socket.recv().decode('latin-1') # grab the message(bytes->str)

    def close(self):
        self.socket.close()
