
目录结构：

```
➜  app_sdr_tuya_beacon_node git:(master) ✗ tree
.
├── rf_alg
│   ├── alg_base.py    # 负责字符串转 MAC, MAC 转字符串等
│   └── __init__.py
├── rf_phy
│   ├── __init__.py
│   └── rf_hcp.py      # 基于管道设计的 python 与 node.exe 双向通信的通信协议管道
├── rf_sdr
│   ├── __init__.py
│   └── plutosdr_tx_rx.py # plutosdr_tx_rx 
├── node.exe           # 包含涂鸦 beacon mesh 协议栈和上层应用的 linux 端可执行程序（beacon 收发基于管道）
├── beacon_node.py     # 包装 node.exe，使用 python 启动，独立线程运行
├── main.py            # 主程序 
├── makefile
└── readme.md
```
