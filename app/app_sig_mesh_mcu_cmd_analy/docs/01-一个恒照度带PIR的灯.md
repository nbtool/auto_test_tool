## 分析一

开启自动感应模式，设备会间隔 3S 上报 dp 1：

```
2024-03-21 16:13:30.838]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:13:30.939]  55 AA 00 00 00 01 01 01 heart
[2024-03-21 16:13:31.860]  55 AA 00 B3 00 00 B2 get pub address
[2024-03-21 16:13:34.843]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:13:37.946]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:13:40.838]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:13:40.939]  55 AA 00 00 00 01 01 01 heart
[2024-03-21 16:13:41.040]  55 AA 00 B3 00 00 B2 get pub address
[2024-03-21 16:13:44.476]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:13:47.459]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:13:50.624]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:13:50.838]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:13:50.939]  55 AA 00 00 00 01 01 01 heart
[2024-03-21 16:13:53.606]  55 AA 00 B3 00 00 B2 get pub address
[2024-03-21 16:13:57.245]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:14:00.227]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:14:00.840]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:14:00.940]  55 AA 00 00 00 01 01 01 heart
[2024-03-21 16:14:03.771]  55 AA 00 B3 00 00 B2 get pub address
[2024-03-21 16:14:06.752]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:14:09.869]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:14:10.840]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
```

</br>

## 分析二

设备开启 Engineering mode 后：

当开启  Engineering mode 后：
1）3S 一次的 dpid = 0x01 的上报仍然存在
2）高频（间隔小于 1S），持续几十·秒轮番发送：（dp 0x75, dp 0x6b, 组内互传 dp 0x03)，当亮度达到某阈值后该过程会停止，之后怎么都不会触发，除非关闭重新开启下  Engineering mode


```
[2024-03-21 16:16:11.580]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:16:11.681]  55 AA 00 07 00 08 75 02 00 04 00 00 01 D5 5F dp upload->dpid=75, dptype=value, dplen=4 00 00 01 D5  
[2024-03-21 16:16:11.783]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:13.021]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 01 D5 23 mesh send
[2024-03-21 16:16:13.122]  55 AA 00 07 00 08 75 02 00 04 00 00 01 E9 73 dp upload->dpid=75, dptype=value, dplen=4 00 00 01 E9  
[2024-03-21 16:16:13.224]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:14.363]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 01 E9 37 mesh send
[2024-03-21 16:16:14.465]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:16:14.566]  55 AA 00 07 00 08 75 02 00 04 00 00 01 FD 87 dp upload->dpid=75, dptype=value, dplen=4 00 00 01 FD  
[2024-03-21 16:16:14.668]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:15.904]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 01 FD 4B mesh send
[2024-03-21 16:16:16.005]  55 AA 00 07 00 08 75 02 00 04 00 00 02 11 9C dp upload->dpid=75, dptype=value, dplen=4 00 00 02 11  
[2024-03-21 16:16:16.107]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:17.344]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 02 11 60 mesh send
[2024-03-21 16:16:17.447]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:16:17.548]  55 AA 00 07 00 08 75 02 00 04 00 00 02 25 B0 dp upload->dpid=75, dptype=value, dplen=4 00 00 02 25  
[2024-03-21 16:16:17.650]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:18.786]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 02 25 74 mesh send
[2024-03-21 16:16:18.887]  55 AA 00 07 00 08 75 02 00 04 00 00 02 39 C4 dp upload->dpid=75, dptype=value, dplen=4 00 00 02 39  
[2024-03-21 16:16:18.989]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:20.227]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 02 39 88 mesh send
[2024-03-21 16:16:20.328]  55 AA 00 07 00 08 75 02 00 04 00 00 02 4D D8 dp upload->dpid=75, dptype=value, dplen=4 00 00 02 4D  
[2024-03-21 16:16:20.430]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:20.846]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 02 4D 9C mesh send
[2024-03-21 16:16:20.946]  55 AA 00 00 00 01 01 01 heart
[2024-03-21 16:16:21.271]  55 AA 00 B3 00 00 B2 get pub address
[2024-03-21 16:16:21.372]  55 AA 00 07 00 08 75 02 00 04 00 00 02 59 E4 dp upload->dpid=75, dptype=value, dplen=4 00 00 02 59  
[2024-03-21 16:16:21.473]  55 AA 00 07 00 05 6B 01 00 01 01 79 dp upload->dpid=6b, dptype=bool, dplen=1 01  
[2024-03-21 16:16:22.425]  55 AA 00 B2 00 0A C1 C8 03 02 00 04 00 00 02 59 A8 mesh send
[2024-03-21 16:16:25.407]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=1, dptype=enum, dplen=1 00  
[2024-03-21 16:16:30.846]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=1, dptype=enum, dplen=1 01  
[2024-03-21 16:16:30.946]  55 AA 00 00 00 01 01 01 heart
```