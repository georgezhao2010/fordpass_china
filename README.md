# FordPass China

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

福特派的Home Assistant集成组件，同时支持林肯之道。

如果你的福特汽车支持福特派/林肯之道手机App远程访问车辆，那么这个组件可以使你通过Home Assistant来显示车辆状态，并远程控制车辆。  
使用该组件，你需要在福特派或者林肯之道中激活绑定你的车辆，如果还没有这么做，请下载福特派/林肯之道，然后注册账号并且在其中激活你的车辆。

福特派和林肯之道账户通用，但车辆数据不互通，因此配置集成时要选择是福特派还是林肯之道。

**注意：该组件仅支持中国大陆使用的福特/林肯汽车。**

**Note: This component is only used for Ford/Lincoln vehicles in China main-land**

![lovelace](https://user-images.githubusercontent.com/27534713/175824781-0ae85a3f-4238-4841-8681-ca9fe6e30bec.png)

# 支持的功能
该组件比官方的福特派App提供了更多可以监控的信息，以后还可以方便地进行扩展。

## 远程控制
- 远程发动机启动
- 远程解锁/锁定车辆

## 远程监控
- 车辆位置
- 邮箱油量
- 总里程
- 剩余里程
- 机油寿命
- 发动机是否运转中
- 车门是否关闭
- 车窗开启程度
- 轮胎胎压
- 电瓶状态及电压

## 电动汽车相关
其实福特派的数据中还有电动汽车相关的数据，但福特中国目前在中国电动车业务极少，所以未予采集。如果有需要，请提issue，我再考虑提取电动汽车数据。

## 传感器及开关列表

|entity_id|entity类型|说明|
| -- | -- | -- |
|switch.{vin}_remote_start|switch|远程启动开关|
|lock.{vin}_lock |lock|车辆中控锁|
|device_tracker.{vin}|device_tracker|车辆位置跟踪 |
|sensor.{vin}_fuel|sensor|剩余燃油|
|sensor.{vin}_alarm|sensor|汽车报警状态|
|sensor.{vin}_odometer|sensor|里程表读数|
|sensor.{vin}_range|sensor|剩余里程|
|sensor.{vin}_oil_life|sensor|机油寿命|
|sensor.{vin}_driver_window_position|sensor|左前车窗开启位置|
|sensor.{vin}_pass_window_position|sensor|右前车窗开启位置|
|sensor.{vin}_rear_driver_window_pos|sensor|左后车窗开启位置|
|sensor.{vin}_rear_pass_window_pos|sensor|右后车窗开启位置|
|sensor.{vin}_left_front_tire_pressure|sensor|左前轮胎胎压|
|sensor.{vin}_right_front_tire_pressure|sensor|右前轮胎胎压|
|sensor.{vin}_left_rear_tire_pressure|sensor|左后轮胎胎压|
|sensor.{vin}_right_rear_tire_pressure|sensor|右后轮胎胎压|
|sensor.{vin}_battery_health|sensor|电瓶健康状态|
|sensor.{vin}_battery_voltage|sensor|电瓶电压|
|binary_sensor.{vin}_ignition_status|binary_sensor|发动机运转状态|
|binary_sensor.{vin}_driver_door|binary_sensor|左前车门状态|
|binary_sensor.{vin}_passenger_door|binary_sensor|右前车门状态|
|binary_sensor.{vin}_left_rear_door|binary_sensor|左后车门状态|
|binary_sensor.{vin}_right_rear_door|binary_sensor|右后车门状态|
|binary_sensor.{vin}_tail_gate_door|binary_sensor|车尾门状态|
|binary_sensor.{vin}_hood_door|binary_sensor|发动机舱盖状态|
|binary_sensor.{vin}_inner_tail_gate_oor|binary_sensor|这个我不太确定是个啥门|

# 安装
可以使用HACS的自定义存储库方式安装，或者从[Latest Release](https://github.com/georgezhao2010/fordpass_china/releases/latest)下载最新的发行版，解压并将`custom_components/fordpass_china`中所有内容复制到你的Home Assistant配置文件夹的`custom_components/fordpass_china`下，并重启Home Assistant。

# 配置
在Home Assistant集成中添加"FordPass China"，~~并输入福特派的账户名及密码~~(由于福特中国更改了API认证方式，因此账户密码认证方式暂不可用)，请选择使用refresh_token认证方式。如果组件发现了你的汽车，将会显示它。

# refresh_token
这->[#5](https://github.com/georgezhao2010/fordpass_china/issues/5#issue-1284972197)

# Debug
要打开调试日志输出，在configuration.yaml中做如下配置
```
logger:
  default: warn
  logs:
    custom_components.fordpass_china: debug
```

