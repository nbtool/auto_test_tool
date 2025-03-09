
这是一个从零实现 ble 广播包合成，并利用 SDR 将其发出的工程。

目前支持：

- grc(hackrf)
- grc_limesdr
- grc_plutosdr
- grc_zmq

</br>

**如何切换不同平台?**

编辑 `main.py` 通过注释和取消注释来选定特定的硬件：

```
from grc_hackrf.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
#from grc_limesdr.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
#from grc_plutosdr.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
#from grc_zmq.gr_ble_adv_tx import gr_ble_adv_tx as gr_block
```

</br>

**架构：**

![][p1]

在 main.py 中每隔 1S 更换 ble 广播包内容，并在其他时间高频通过 ZMQ PUB 向 55556 端口发送合成的数据，这个数据通过 SDR 即可实现 BLE 广播包的发送。

```python
zmq1 = bsp_zmq.bsp_zmq("tcp://127.0.0.1:55556", "PUB")
try:
    start_time = time.time()
    interval = 1 #1S 
    count = 0
    
    packed_data = b''
    while 1<2:
        current_time = time.time()
        if count == 0 or current_time - start_time >= interval:
            mac = [1,2,3,4,5,6]
            adv_name = f"hello btfz's gnu-radio {count}"
            adv_datas = [len(adv_name) + 1, 0x09] + [ord(char) for char in adv_name]
            channel = 37
            ll_datas_normalization_sample = app_beacon_gen(mac, adv_datas, channel)

            packed_data = b''
            for data in ll_datas_normalization_sample:
                packed_data += struct.pack("f", data)


            start_time = current_time
            count = count + 1
        

        zmq1.send(packed_data)
```

</br>

**运行：**

- 当选择实体 SDR 时，将实体对应的 SDR 插入电脑，然后直接 make 即可执行。

- 当选择 ZMQ 时，需要在其他地方运行程序，需要 ZMQ SUB `tcp://127.0.0.1:5557`，将收到的数据合理地送入 SDR 进行发送；然后 make 当前程序，将数据流 PUB 到 5557 端口。


[p1]:./doc/架构.drawio.png