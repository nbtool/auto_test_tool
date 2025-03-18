#!/usr/bin/env python
# coding=utf-8
import subprocess
import atexit
import os
from rf_phy.rf_hcp import rf_hcp
from rf_alg.alg_base import alg_base

class beacon_node:
    def __init__(self, mac, key, hcp_cb):

        self.mac = alg_base.to_hexs(mac)
        # 提取 key 的前 16 字节
        key_prefix = key[:16]
        dir_path = ".log/device/"+alg_base.to_hexstr(self.mac,':')
        cmd_exe = os.path.join(os.getcwd(),'./node.exe')
        cmd_work_path = os.path.join(os.getcwd(),dir_path)
        # 调用可执行程序 `node`，非阻塞
        # print(mac, key_prefix)
        self.hcp = rf_hcp(self.mac, hcp_cb)

        self.proc = subprocess.Popen([cmd_exe, mac, key_prefix], cwd=cmd_work_path)

        # 注册清理函数，以确保在程序结束时调用
        atexit.register(self.cleanup_processes)

    def run(self):
        self.hcp.run()

    def cleanup_processes(self):
        self.proc.terminate()
        self.proc.wait()


