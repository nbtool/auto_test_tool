这是在上一个 DEMO：`app_sdr_ble_adv_tx_rx` 基础上叠加了应用层协议，最终实现从电磁波开始，到全双工蓝牙广播收发接入涂鸦智能，变成一个物联网 BeaconMesh 灯节点。

目前基于具备全双工两收两发的 PlutoSDR 实现的，代码目录：

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

</br>

**架构：**

![][p1]

其中：

- 基于 TuyaOS 的 Beacon Mesh Linux SDK，将蓝牙广播适配层改为一个基于管道的收发接口（方便与 GNU Radio 的实际 BLE PHY 通信，实现广播参数设置、启动与停止广播、接收广播扫描数据），并编译成可执行程序 `node.exe`
- `plutosdr_tx_rx.py` 和收发 DEMO 中的一样：负责 SDR 的收发，它与 `main.py` 之间采用 ZMQ 进行通信，这样方便今后更换其他硬件，而保持 `main.py` 不变。
- `main.py`：
    - 一方面通过 ZMQ 与实际的硬件（plutosdr）通信
    - 一方便调用前两节介绍的收发流程图，分别实现 GFSK 解析 -> LL 解析和 LL 合成 -> GFSK 调制
    - 采用独立线程运行 `node.exe`
    - 启动 HCP 管道协议接收线程，当 `node.exe` 下行命令通知 SDR 设置蓝牙参数时，通过 hcp_cb 回调函数调用相应 SDR 函数，实现蓝牙广播包的更新、蓝牙广播的开启与停止；当 SDR 收到蓝牙广播包时，会在其回调函数中调用 `hcp.send` 将数据上报到 `node.exe` 


</br>

**运行：**

- 下载涂鸦智能 APP
- 参考下面视频，在[涂鸦开发者平台][#1]创建一个 BeaconMesh 灯，并申请两个免费的授权码清单

  ![][p2]

- 修改 main.py 中的 key 和 mac 为你申请的授权码清单中的值：

    ```
	key = "hHbxxxxxxxxxxxxxxxxxxxxxxxxxxRcO" # authkey
    mac = "DC234FAFDC7A" # mac
    ```	

- 将 PlutoSDR 插入电脑（最好通过网口，这样速率快），保证 `sudo SoapySDRUtil --find` 可以发现设备，然后直接运行 `make`，可以在涂鸦智能 APP 中添加我们的设备，添加完之后可以进行控制。









[#1]:https://platform.tuya.com/pmg/solution    

[p1]:./doc/架构.drawio.png
[p2]:./doc/涂鸦智能创建一个BeaconMesh灯.gif