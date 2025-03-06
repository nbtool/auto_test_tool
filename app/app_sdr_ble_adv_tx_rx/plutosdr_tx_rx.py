#!/usr/bin/env python
# coding=utf-8
#!/usr/bin/env python
# coding=utf-8
import SoapySDR
from SoapySDR import *  # SOAPY_SDR_ constants
import numpy as np
import time
import threading
import signal
import zmq
import logging
import sys

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 定义配置类
class Config:
    FREQUENCY = 2402e6  # 2.402 GHz
    SAMPLE_RATE = 10e6  # 10 MHz(AD9363 最高20M, AD9361 最高61.44M), 越高扫到的东西越多[发送线程函数端使用 4->10 重采样]
    TX_GAIN = 70  # 发射增益(这个大会对接收造成影响https://chatgpt.com/c/67974ac6-932c-8009-bdaa-d8775b0e0ce6)
    RX_GAIN = 40  # 接收增益
    ZMQ_PUB_PORT = "5556"
    ZMQ_SUB_PORT = "5557"
    DEVICE_DRIVER = "plutosdr"
    DEVICE_ADDRESS = "ip:pluto.local"

# 初始化 PlutoSDR 设备
def setup_sdr():
    try:
        # sdr = SoapySDR.Device({"driver": Config.DEVICE_DRIVER, "device": Config.DEVICE_ADDRESS})
        # devices = SoapySDR.Device.enumerate()
        # for result in devices:
        #    print(dict(result))

        sdr = SoapySDR.Device()
        print("> tx channels num:",sdr.getNumChannels(SOAPY_SDR_TX))
        print("> rx channels num:",sdr.getNumChannels(SOAPY_SDR_RX))

        # 配置发射通道
        sdr.setSampleRate(SOAPY_SDR_TX, 0, Config.SAMPLE_RATE) # 采样率似乎要保持一致
        sdr.setFrequency(SOAPY_SDR_TX, 0, Config.FREQUENCY)
        sdr.setGain(SOAPY_SDR_TX, 0, Config.TX_GAIN)
        # sdr.setAGC(SOAPY_SDR_TX, 0, True)  # 启用 AGC
        # sdr.setGainMode(SOAPY_SDR_TX, 0, True)

        # 配置接收通道
        sdr.setSampleRate(SOAPY_SDR_RX, 0, Config.SAMPLE_RATE)
        sdr.setFrequency(SOAPY_SDR_RX, 0, Config.FREQUENCY)
        sdr.setGain(SOAPY_SDR_RX, 0, Config.RX_GAIN)
        return sdr
    except Exception as e:
        logging.error(f"Failed to setup SDR: {e}")
        return None

# 封装 ZeroMQ 上下文管理
class ZMQContextManager:
    def __init__(self):
        self.context = zmq.Context()

    def create_pub_socket(self, port):
        socket = self.context.socket(zmq.PUB)
        socket.bind(f"tcp://*:{port}")
        print(f"pub->tcp://*:{port}")
        return socket

    def create_sub_socket(self, port):
        socket = self.context.socket(zmq.SUB)
        socket.connect(f"tcp://localhost:{port}")
        socket.setsockopt_string(zmq.SUBSCRIBE, "")
        print(f"sub->tcp://localhost:{port}")
        return socket

    def close(self):
        self.context.term()

# 接收线程函数
def receive_signal(sdr, zmq_manager):
    socket_pub = zmq_manager.create_pub_socket(Config.ZMQ_PUB_PORT)
    rx_stream = sdr.setupStream(SOAPY_SDR_RX, SOAPY_SDR_CF32)
    sdr.activateStream(rx_stream)
    num_samples = 1024
    buff = np.array([0] * num_samples, np.complex64)
    try:
        while not stop_event.is_set():
            sr = sdr.readStream(rx_stream, [buff], num_samples)
            if sr.ret > 0:
                # 将接收到的数据转换为字节流并发布
                data_bytes = buff.tobytes()
                socket_pub.send(data_bytes)
    except Exception as e:
        logging.error(f"Error in receive_signal: {e}")
    finally:
        sdr.deactivateStream(rx_stream)
        sdr.closeStream(rx_stream)
        socket_pub.close()
        logging.info("rx stream stop...")

# 发送线程函数
def transmit_signal(sdr, zmq_manager):
    socket_sub = zmq_manager.create_sub_socket(Config.ZMQ_SUB_PORT)
#    https://pothosware.github.io/SoapySDR/doxygen/latest/classSoapySDR_1_1Device.html#a8a64e7fef972e9c24bbc2f1b4811a38f
#    plutosdr 看似全双工，但是似乎只要同时开启，接收会严重受到影响
    tx_stream = sdr.setupStream(SOAPY_SDR_TX, SOAPY_SDR_CF32)
    sdr.activateStream(tx_stream)
    poller = zmq.Poller()
    poller.register(socket_sub, zmq.POLLIN)
    flag = 0
    try:
        while not stop_event.is_set():
            socks = dict(poller.poll(timeout=100))  # 超时时间设置为 100 毫秒
            if socket_sub in socks and socks[socket_sub] == zmq.POLLIN:
                # print("tx")
                message = socket_sub.recv()

                # 将接收到的字节流转换为 numpy 数组
                buff = np.frombuffer(message, dtype=np.complex64)

                if flag == 0:
                    flag = 1
                    print("Raw bytes:", " ".join(f"{b:02x}" for b in message[:128]))  # 先打印前
                    print("buff:",buff[:16])

                logging.debug(buff)
                #sdr.setGain(SOAPY_SDR_TX, 0, 70)
                sdr.writeStream(tx_stream, [buff], len(buff))
                #sdr.setGain(SOAPY_SDR_TX, 0, 0)
                
    except Exception as e:
        logging.error(f"Error in transmit_signal: {e}")
    finally:
        sdr.deactivateStream(tx_stream)
        sdr.closeStream(tx_stream)
        socket_sub.close()
        logging.info("tx stream stop...")

# 定义一个事件对象，用于通知子线程停止运行
stop_event = threading.Event()

def safe_exit(sdr, zmq_manager, threads):
    stop_event.set()  # 设置事件对象，通知子线程停止运行
    # 等待子线程结束
    for t in threads:
        t.join()
    del sdr
    zmq_manager.close()
    logging.info("Safe exit")

# 信号处理函数，用于捕获 SIGINT 信号
def signal_handler(sig, frame):
    logging.info("Received interrupt signal. Stopping threads...")
    safe_exit(sdr, zmq_manager, threads)
    sys.exit(0)

if __name__ == "__main__":
    try:
        sdr = setup_sdr()
        if sdr is None:
            sys.exit(1)
        zmq_manager = ZMQContextManager()
        threads = []
        t1 = threading.Thread(target=receive_signal, args=(sdr, zmq_manager))
        t2 = threading.Thread(target=transmit_signal, args=(sdr, zmq_manager))
        threads.append(t1)
        threads.append(t2)
        for t in threads:
            t.daemon = True
            t.start()
        # 注册信号处理函数
        signal.signal(signal.SIGINT, signal_handler)
        # 主线程保持运行
        while True:
            time.sleep(1)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'sdr' in locals() and sdr is not None:
            safe_exit(sdr, zmq_manager, threads)
