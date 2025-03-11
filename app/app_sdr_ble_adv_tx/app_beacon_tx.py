import threading
import time
import struct

from app_beacon_gen import app_beacon_gen

class app_beacon_tx:
    def __init__(self, send_func):
        self.packed_iq_datas = b''
        self.tx_interval_ms = 0
        self.tx_repet_times = 0
        self.tx_start_time = 0
        self.tx_send_func = send_func
        self.lock = threading.Lock()  # 定义线程锁

    def update_datas(self, mac, adv_datas, channel):
        with self.lock:  # 加锁
            ll_datas_normalization_sample = app_beacon_gen(mac, adv_datas, channel)
            packed_iq_datas = b''
            for data in ll_datas_normalization_sample:
                packed_iq_datas += struct.pack("f", data)
            self.packed_iq_datas = packed_iq_datas

    def start(self, interval_5xms, repet_times):
        with self.lock:  # 加锁
            self.tx_interval_ms = interval_5xms * 5
            self.tx_repet_times = repet_times
            self.tx_start_time = time.time()

    def stop(self):
        with self.lock:  # 加锁
            self.tx_repet_times = 0

    def loop(self):
        with self.lock:  # 加锁
            current_time = time.time()
            time_diff_ms = (current_time - self.tx_start_time) * 1000
            if self.tx_repet_times > 0 and time_diff_ms >= self.tx_interval_ms:
                if len(self.packed_iq_datas) != 0:
                    self.tx_send_func(self.packed_iq_datas)

                # if repet_times == 0xFFFFFFFF -> forever
                if self.tx_repet_times != 0xFFFFFFFF:
                    self.tx_repet_times -= 1

                self.tx_start_time = current_time
