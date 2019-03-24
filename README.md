# wxrobot 带WEB界面的微信机器人，插件可扩展深层次开发

## 鸣谢

微信机器人是根据web微信协议开发的，用于实现特定功能（比方自动回复，自动添加好友，自动发群信息）的产品。
该类产品轮子很多，大家可以自行搜索。

本项目是根据wxBot项目(https://github.com/liuwons/wxBot)深度开发，有关wxbot.py代码，也可以参考该项目。

## 效果演示


## 新增功能
1、多用户，多线程，后台运行

2、提供Web界面，方便用户使用

3、自动保存聊天历史图片和语音

4、可以长时间在线运行

## 文件结构

  - [部署目录] 
    - [data]      -- 系统配置，用户配置和用户数据目录
      - robot_config.json  -- 系统配置
    - [plugin]    -- 插件目录
    - [static]    -- Web程序，JS，CSS存放目录
    - [template]  -- Web程序，前端模板目录
    - daemon.py   -- 后台进程处理
    - icon.ico    -- web index icon
    - main.spec   -- 生成单个可执行文件配置
    - make.cmd    -- 生成单个可执行文件命令
    - myBot.py    -- 插件功能处理单元
    - requirements.txt -- 依赖库
    - robsSrv.py  -- 主服务程序
    - util.py     -- 通用功能程序
    - wxbot.py    -- Web微信APi核心单元

## 部署方法(下面说明部署在/home/wxrobot下)
  
  目前测试在python2.7.5以上版本，3.5以上版本都可以运行
  
  #cd /home
  
  #git clone https://github.com/codingtoworld/wxrobot.git
  
  或者直接下载Zip文件，解压缩到/home/wxrobot下
  
  安装扩展：
  #cd wxrobot
  #pip -r requirements.txt
  
  也可以使用虚拟环境安装。

## 配置
配置文件为data/robot_config.json，结构如下：
```
{
  "auth":{
    "json": {
      "codingtoworld": "586078aa040e495e437c2913e69064ef",
      "账户名称2": "MD5密码值"
    }
  }
}
```
上面文件中可以配置多个账户，登陆时使用对应的账户和密码登陆即可。


## 使用方法

运行程序：python /home/wxRobot/robsSrv.py start|stop|restart

start:启动程序，同时启动web服务，程序后台运行

stop：停止程序

restart：重启程序

访问方法：浏览器直接输入地址：http://ipaddress:port/


![码上看世界](https://avatars3.githubusercontent.com/u/48540915?s=460&v=4)

Facebook: https://facebook.com/codingtoworld

Twitter：https://twitter.com/codingtoworld

## How to donate?
![](https://resource.bnbstatic.com/images/20180806/1533543864307_s.png)BitCoin: 1K5apYN4k3UNdymo3qSfRWAehgri3skczQ

![](https://resource.bnbstatic.com/images/20180806/1533543997535_s.png)ETH:0x1eee99743dfddf6a4b6402047c1946ce9943c965

![](https://resource.bnbstatic.com/images/20180810/1533888627851_s.png)USDT:1KYvKoWDfoY8Xm2VNKoRWC9HgxtV3MbJRp
