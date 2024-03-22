## 分析一

普通情况，设备会间隔 3S 上报 dp 1：

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

设备开启横照度后：

1）3S 一次的 dpid = 0x01 的上报仍然存在（dp1有人无人）
2）高频（间隔小于 1S），持续几十·秒轮番发送：（dp 0x75, dp 0x6b, 组内互传 dp 0x03)，当亮度达到某阈值后该过程会停止（亮度改变会重复该过程）

</br>

询问客户，其描述的逻辑为：

0x6b=107 -> ON/OFF	
0x75=117 -> 当前亮度
0x1C=28 -> Intelligent Linkage	

1）DP01的上报逻辑，感应到有人上报一次有人，间隔2S后上报一次无人。间隔2S后如果再次检测到有人，重复前面的动作。如果间隔2S后一直无人，一直无上报
2）DP117（0X75）实时亮度上报，如果亮度变化，马上上报。恒照度模式下，亮度只要变化，亮度一直实时上报，无封锁。
3）DP107（0x6b) 开关状态有变化时会上报

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

</br>

## 分析三

点击 Intelligent linkage 使能 switchlink 后，这样页面中的雷达按钮可以做到开启与关闭PIR感应

这样每次有 PIR 变化就会向外 mesh send 0x1C

```
[2024-03-22 09:42:59.774]  55 AA 00 B2 00 07 C1 E0 1C 04 00 01 01 7B mesh send->group_address=0xc1e0 dpid=0x1c, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:00.683]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=0x1, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:00.784]  55 AA 00 00 00 01 01 01 heart
[2024-03-22 09:43:03.306]  55 AA 00 B3 00 00 B2 get pub address
[2024-03-22 09:43:03.407]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=0x1, dptype=enum, dplen=1, value=[ 00 ]
[2024-03-22 09:43:03.509]  55 AA 00 B2 00 07 C1 D0 1C 04 00 01 01 6B mesh send->group_address=0xc1d0 dpid=0x1c, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:06.286]  55 AA 00 B2 00 07 C1 E0 1C 04 00 01 01 7B mesh send->group_address=0xc1e0 dpid=0x1c, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:09.995]  55 AA 00 07 00 05 01 04 00 01 01 12 dp upload->dpid=0x1, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:10.096]  55 AA 00 07 00 05 01 04 00 01 00 11 dp upload->dpid=0x1, dptype=enum, dplen=1, value=[ 00 ]
[2024-03-22 09:43:10.198]  55 AA 00 B2 00 07 C1 D0 1C 04 00 01 01 6B mesh send->group_address=0xc1d0 dpid=0x1c, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:10.684]  55 AA 00 B2 00 07 C1 E0 1C 04 00 01 01 7B mesh send->group_address=0xc1e0 dpid=0x1c, dptype=enum, dplen=1, value=[ 01 ]
[2024-03-22 09:43:10.784]  55 AA 00 00 00 01 01 01 heart
[2024-03-22 09:43:12.975]  55 AA 00 B3 00 00 B2 get pub address
```
