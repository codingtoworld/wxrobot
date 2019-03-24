#!/usr/local/python27/bin/python
# coding: utf-8
#
import datetime, importlib
import websocket
from hashlib import md5
from util import *
from wxbot import *

class WXRobot(WXBot):
    wsClient = None
    wsCheckTime = 0 #上次检测心跳时间

    def get_plugs(self):
        plugin_cfg = os.path.join(self.temp_pwd,'plugin_config', 'load_plugins.json')
        try:
            with open(plugin_cfg) as f:
                return json.loads(f.read())
        except:
            if self.DEBUG:
                print(plugin_cfg + u'打开出错')
            return False

    @classmethod
    def send_to_ws(cls,threadId,msg):
        t=time.time()
        ws_url = "ws://" + SRV_BIND_IP + ":"+str(SRV_LISTEN_PORT)+"/wsmessage"
        cookie="heartbit=" + md5(threadId).hexdigest()
        if cls.wsClient is None:
            cls.wsClient = websocket.WebSocket()
            cls.wsClient.connect(ws_url,cookie=cookie)
        if (t - cls.wsCheckTime) >= 60: #1分钟检测一次心跳，如果失败，则重新建立链接
            try:
                cls.wsClient.send("6865617274626974")
            except:
                cls.wsClient.connect(ws_url,cookie=cookie) #重新连接

        cls.wsCheckTime = t
        chat = msg.copy()
        chat["who_weplus"]=threadId

        if msg['content']['type'] == 0:#文字
            cls.wsClient.send(json.dumps(chat))
            pass
        elif msg['content']['type'] == 3: # 图片
            cls.wsClient.send(json.dumps(chat))
            pass
        elif msg['content']['type'] == 4: # 语音
            cls.wsClient.send(json.dumps(chat))
            pass
        else:
            pass

    def send_wx_message(self, msgNr, toUser=None):
        toName = 'filehelper'  # 默认发送到文件
        # if len(self.my_account['UserName'])<36:
        #    toName = self.my_account['UserName']
        if not toUser is None:
            if len(toUser) > 32:
                return self.send_msg_by_uid(msgNr, toUser)
            else:
                return self.send_msg(toUser, msgNr)
        else:
            return self.send_msg_by_uid(msgNr, toName)

    def handle_msg_all(self, msg):
        '''

        :param 消息队列:
        :return: 根据消息类型，对消息进行处理
        '''
        if (msg['msg_type_id'] == 1 or msg['msg_type_id'] == 4) and msg['content']['type']<10: #将自己的和联系人的消息发送到 127.0.0.1:8000/wsmessage
            WXRobot.send_to_ws(self.threadId,msg)

        user_plugs = self.get_plugs()
        if not user_plugs:
            return False

        plugins = os.listdir(os.path.join(os.getcwd(), 'plugin'))
        for plugin in plugins:
            if plugin.endswith('.py') and plugin.startswith('message'):
                plugin = plugin.replace('.py', '')
                if plugin in user_plugs["message"]:
                    plugin_mod = 'plugin.' + plugin
                    if self.DEBUG:
                        sch_mod = importlib.import_module(plugin_mod)
                        reload(sch_mod)
                        sch_mod.run(BOTS[self.threadId], msg)
                    else:
                        try:
                            sch_mod = importlib.import_module(plugin_mod)
                            reload(sch_mod)
                            sch_mod.run(BOTS[self.threadId], msg)
                        except:
                            print('load plugin: %s Error' % plugin_mod)

    def schedule(self):
        user_plugs = self.get_plugs()
        if not user_plugs:
            return False
        cron = int(datetime.datetime.now().strftime("%M"))
        if self.schedule_time == cron:
            return False
        # 程序开始
        plugins = os.listdir(os.path.join(os.getcwd(), 'plugin'))
        for plugin in plugins:
            if plugin.endswith('.py') and plugin.startswith('schedule'):
                plugin = plugin.replace('.py', '')
                if plugin in user_plugs["schedule"]:
                    plugin_mod = 'plugin.'+plugin
                    if self.DEBUG:
                        sch_mod = importlib.import_module(plugin_mod)
                        reload(sch_mod)
                        sch_mod.run(BOTS[self.threadId])
                    else:
                        try:
                            sch_mod = importlib.import_module(plugin_mod)
                            reload(sch_mod)
                            sch_mod.run(BOTS[self.threadId])
                        except:
                            print('load plugin: %s Error' % plugin_mod)
        self.schedule_time = cron
        # 程序结束