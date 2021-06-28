# FordPass China

福特派的Home Assistant集成组件

如果你的福特汽车支持福特派手机App远程访问车辆，那么这个组件可以使你通过Home Assistant来显示车辆状态，并远程控制车辆。  
使用该组件，你需要一个福特派账号。如果你没有，可以下载官方的福特派App，并注册账号并且在其中绑定你的车辆。

**注意：该组件仅支持中国境内的福特汽车。**

# 支持的功能

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
- 车窗是否关闭
- 轮胎胎压
- 电瓶状态及电压

# 安装
可以使用HACS的自定义存储库方式安装，或者从[LatestRelease](https://github.com/georgezhao2010/fordpass_china/releases/latest)下载最新的发行版，解压并将`custom_components/fordpass_china`中所有内容复制到你的Home Assistant配置文件夹的`custom_components/fordpass_china`下，并重启Home Assistant。

# 配置
该集成组件采用图形化配置，在Home Assistant集成中添加"FordPass China"，并输入福特派的账户名及密码，如果组件发现了你的汽车，将会显示它。
