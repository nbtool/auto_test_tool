
这是一个利用 SDR 接收数据，并解析出蓝牙广播包的代码。

目前支持：

- grc(hackrf)
- grc_limesdr
- grc_plutosdr
- grc_zmq

</br>

**如何切换不同平台?**

编辑 `main.py` 通过注释和取消注释来选定特定的硬件：

```
#from grc.gr_ble import gr_ble as gr_block
#from grc_limesdr.gr_ble import gr_ble as gr_block
#from grc_plutosdr.gr_ble import gr_ble as gr_block
from grc_zmq.gr_ble import gr_ble as gr_block
```

</br>

**架构：**

![][p1]

</br>

**运行：**

- 当选择实体 SDR 时，将实体对应的 SDR 插入电脑，然后直接 make 即可执行。

- 当选择 ZMQ 时，需要在其他地方运行程序，将 SDR 获取到的数据利用 ZMQ PUB SINK 送入到 `tcp://127.0.0.1:5556`，然后 make 当前程序，并且还要运行 ZMQ PUB 程序。


[p1]:./doc/架构.drawio.png