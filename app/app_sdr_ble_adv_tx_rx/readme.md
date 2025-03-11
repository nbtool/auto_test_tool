
这是基于前两个 demo：`app_sdr_ble_adv_rx` 和 `app_sdr_ble_adv_tx` 实现的 BLE 广播收发一体的 DEMO。

目前基于具备全双工两收两发的 PlutoSDR 实现的，代码目录：

```
├── main.py            # 负责广播包数据解调、解析 + 广播数据合成、调制
├── plutosdr_tx_rx.py  # 负责 plutosdr 收发
├── makefile
└── readme.md
```

</br>

**架构：**

![][p1]

- 其中 `plutosdr_tx_rx.py` 负责 SDR 的收发，它与 `main.py` 之间采用 ZMQ 进行通信，这样方便今后更换其他硬件，而保持 `main.py` 不变。
- `main.py` 一方面通过 ZMQ 与实际的硬件（plutosdr）通信，一方便调用前两节介绍的收发流程图，分别实现 GFSK 解析 -> LL 解析和 LL 合成 -> GFSK 调制。

</br>

```python
###############################################################
# 接收相关
def analysis_cmd(str):
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
count = 0
mac = [1,2,3,4,5,6]
channel = 37
def gen_adv_datas(count):
    adv_name = f"hello btfz's gnu-radio {count}"
    adv_datas = [len(adv_name) + 1, 0x09] + [ord(char) for char in adv_name]
    return adv_datas

app_beacon_tx = app_beacon_tx(zmq_ble_tx.send)
adv_datas = gen_adv_datas(count)
app_beacon_tx.update_datas(mac, adv_datas, channel)
app_beacon_tx.start(1,0xFFFFFFFF)

###############################################################
# SDR 收发器启动
sdr_tx_rx_start()

###############################################################
# 主循环相关
try:
    while 1<2:
        adv_receive_loop()
        app_beacon_tx.loop()
```

</br>

**运行：**

- 将 PlutoSDR 插入电脑（最好通过网口，这样速率快），保证 `sudo SoapySDRUtil --find` 可以发现设备，然后直接运行 `make`，可以在手机的 nrf connect 上看到广播包，并且可以在终端中看到其扫描到的其他设备的广播包，从而验证收发一体。


[p1]:./doc/架构.drawio.png