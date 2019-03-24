#!/usr/local/bin/python
#  -*- encoding: utf-8 -*-
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.websocket
import os,sys
import threading
import time
import json
import importlib
from hashlib import md5
from tornado.options import define, options, parse_command_line
from util import *
from daemon import Daemon

define("port", default=SRV_LISTEN_PORT, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")
deploy_dir = 'D:\\WePlus\\wxRobot' if sys.platform.startswith('win') else '/home/wxRobot'

class RobotsHandler(tornado.web.RequestHandler):
    def get_user_plugs(self,wxBot):
        plugin_cfg = os.path.join(wxBot.temp_pwd, 'plugin_config', 'load_plugins.json')
        try:
            with open(plugin_cfg) as f:
                return json.loads(f.read())
        except:
            return {"message":[],"schedule":[]}

    def get_userId(self):
        user = self.get_secure_cookie("robot_user")
        if user:
            return user
        else:
            return False

    def is_wechat_login(self):
        userId = self.get_secure_cookie("robot_user")
        if userId:
            code, ts = threadLists(userId)
            if code == 1 and BOTS[userId].status == 'loginsuccess':
                return True
            else:
                return False
        else:
            return False

class startHandler(RobotsHandler):
    def post(self):
        userId = self.get_userId()
        code, ts = threadLists(userId)
        if userId:
            if code == 0:
                runWxThread(userId)
                self.write({'ret': 0, 'msg': 'code:0, server is run.'})  # 输出空页面
            else:
                if BOTS[userId].status == 'wait4login':
                    self.write({'ret': 1, 'msg': 'pyweixin is running, but not logined.'})  # ret = 1 正常
                elif BOTS[userId].status == 'loginsuccess':
                    self.write({'ret': 0, 'msg': 'server is still run.'})  # 输出空页面
                else:
                    runWxThread(userId)
                    self.write({'ret': 0, 'msg': 'code:1, server is run.'})  # 输出空页面
        else:
            self.write({'ret': -1, 'msg': 'please login user first!'})  # 输出空页面

class indexHandler(RobotsHandler):
    def get(self):
        userId = self.get_userId()
        if userId:
            self.render("index.html",username=userId)
        else:
            self.redirect("login")

class loginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        incorrect = self.get_secure_cookie("incorrect") or 0
        if incorrect and int(incorrect) > 20:
            self.write('<center>blocked</center>')
            return

        increased = str(int(incorrect) + 1)
        self.set_secure_cookie("incorrect", increased)

        getusername = tornado.escape.xhtml_escape(self.get_argument("username"))
        getpassword = tornado.escape.xhtml_escape(self.get_argument("password"))
        auth_action = 'json' #weplus  json

        for k,v in self.request.arguments.items():
            if k == 'authaction':   #验证方式
                auth_action = v[0]
                break

        cnf = jsonconf.load(os.path.join(os.getcwd(), 'data', 'robot_config.json'))
        for key in cnf:
            BOT_CONFIG[key] = cnf[key]
        if BOT_CONFIG == {}:
            print("load Error robot_config.json!")
            return False

        #auths = {}
        try:
            is_authed = False
            if hasattr(self, 'auth_by_%s' % auth_action):
                is_authed = getattr(self, 'auth_by_%s' % auth_action)(getusername,getpassword)

            #####################################
            if is_authed:#认证通过
                self.set_secure_cookie("robot_user", getusername, expires_days=None)
                self.set_secure_cookie("robot_log",getpassword, expires_days=None)
                self.set_secure_cookie("incorrect", "0")
                if auth_action == 'weplus':
                    self.write({"ret": 0, "msg": "success"})
                else:
                    self.redirect("./")
            else:
                if auth_action == 'weplus':
                    self.write({"ret": -1, "msg": "failure"})
                else:
                    self.redirect("./login")
        except:
            self.redirect("./login")
            return

    def auth_by_json(self,username,password):
        auths = BOT_CONFIG["auth"]
        if auths["json"].get(username, '') == md5(password).hexdigest():
            return True
        return False

    def auth_by_weplus(self,username,password):
        return wepcrm_login(username,password)

class logoutHandler(RobotsHandler):
    def get(self):
        self.clear_cookie("robot_user")
        self.clear_cookie("incorrect")
        self.redirect("./login")

class pluginHandler(RobotsHandler):
    def get(self):
        if self.is_wechat_login():
            userId = self.get_userId()
            self.render("plugin.html", username=userId)
        else:
            self.redirect("./")

class plugindataHandler(RobotsHandler):
    def get(self):
        if not self.is_wechat_login():
            return

        userId = self.get_userId()
        plugin_list = [{
            "text":u"消息触发插件",
            "nodes":[]
        },{
            "text": u"定时轮询插件",
            "nodes": []
        }]

        user_plugins = self.get_user_plugs(BOTS[userId])
        plugins = os.listdir(os.path.join(os.getcwd(), 'plugin'))
        print(plugins)
        for plugin in plugins:
            if plugin.endswith('.py') and (plugin.startswith('message') or plugin.startswith('schedule')):
                plugin = plugin.replace('.py', '')
                plugin_mod = 'plugin.' + plugin
                print(plugin_mod)
                sch_mod = importlib.import_module(plugin_mod)
                p = {
                    "data": sch_mod.plugin_key,
                    "text": sch_mod.plugin_name,
                    "state": {}
                }
                if plugin.startswith('message'):
                    if(sch_mod.plugin_key in user_plugins['message']):
                        p['state']['checked'] = True
                    plugin_list[0]['nodes'].append(p)
                if plugin.startswith('schedule'):
                    if (sch_mod.plugin_key in user_plugins['schedule']):
                        p['state']['checked'] = True
                    plugin_list[1]['nodes'].append(p)

        self.write(json.dumps(plugin_list))

class pluginuserHandler(RobotsHandler):
    def get(self):
        if not self.is_wechat_login():
            return

        userId = self.get_userId()
        plugin = self.get_argument("plugin")
        wxBot = BOTS[userId]

        plugin_mod = 'plugin.' + plugin
        load_mod = importlib.import_module(plugin_mod)
        if not(load_mod.plugin_json is None):
            plugin_config = os.path.join(wxBot.temp_pwd, 'plugin_config', plugin+'.json')
            if os.path.isfile(plugin_config):
                with open(plugin_config, 'r') as f:
                    tpl_cfg = json.loads(f.read())
                    self.write(tpl_cfg)
            else:
                self.write(json.dumps(load_mod.plugin_json))
        else:
            self.write({"info":u"该插件不需要配置"})

    def post(self): #保存用户配置
        if not self.is_wechat_login():
            return

        userId = self.get_userId()
        user_plugins = self.get_user_plugs(BOTS[userId]) #删除历史配置

        for item in user_plugins["message"]:
            pf = os.path.join(BOTS[userId].temp_pwd, 'plugin_config', item + '.json')
            if os.path.isfile(pf):
                os.unlink(pf)
        for item in user_plugins["schedule"]:
            pf = os.path.join(BOTS[userId].temp_pwd, 'plugin_config', item + '.json')
            if os.path.isfile(pf):
                os.unlink(pf)

        plugin_config = {"message": [], "schedule": []}
        if self.request.arguments:
            filters = self.request.arguments
            for k, v in filters.items():
                #print k,v
                if k.startswith("message") and (not k in plugin_config['message']):
                    plugin_config['message'].append(k)
                if k.startswith("schedule") and (not k in plugin_config['schedule']):
                    plugin_config['schedule'].append(k)
                if k.startswith("schedule") or k.startswith("message"):
                    plugin_cfg = os.path.join(BOTS[userId].temp_pwd, 'plugin_config', k + '.json')
                    plugin_json=v[0]
                    #print plugin_json
                    jsonconf.save(json.loads(plugin_json), plugin_cfg)
                #print "----------------------------"

        plugin_cfg = os.path.join(BOTS[userId].temp_pwd, 'plugin_config', 'load_plugins.json')
        jsonconf.save(plugin_config, plugin_cfg)

        self.write(u"保存成功")

class contactsHandler(RobotsHandler):
    def post(self):
        if not self.is_wechat_login():
            self.write({"ret": -1, "data": "User is not logined."})
            return

        userId = self.get_userId()
        self.write(json.dumps(BOTS[userId].contact_list))


class threadsHandler(RobotsHandler):
    def get(self):
        code, ts = threadLists("")
        self.write({'ret': 0, 'msg': ','.join(ts)})  # 输出空页面


class checkHandler(RobotsHandler):
    def post(self):
        userId = self.get_userId()
        if not userId:
            self.write({'ret': -2, 'msg': 'wechat user is not login!'})  # ret = -1 异常、
            return
        if not self.get_secure_cookie("robot_log"):
            self.write({'ret': -2, 'msg': 'wechat user is not login!'})  # ret = -1 异常、
            return

        flag, ts = threadLists(userId)

        if flag == 0:
            self.write({'ret': -1, 'msg': 'Close weixin connection.'})  # ret = -1 异常
        else:
            if BOTS[userId].status == 'wait4login':
                self.write({'ret': 1, 'msg': 'pyweixin is running, but not logined.'})  # ret = 1 正常
            elif BOTS[userId].status == 'loginsuccess':
                # 重新刷新联系人
                BOTS[userId].get_contact()
                self.write({'ret': 0, 'msg': 'pyweixin is logined running.'})  # ret = 1 正常
            else:
                self.write({'ret': -1, 'msg': 'lost weixin connection.'})  # ret = -1 异常、

class wechatHandler(RobotsHandler):
    def get(self):
        if not self.is_wechat_login():
            self.write({"ret": -1, "data": "User is not logined."})
            return
        self.render("chat.html")

class wechattreeHandler(RobotsHandler):
    def get(self):
        if not self.is_wechat_login():
            self.write({"ret": -1, "data": "User is not logined."})
            return

        userId = self.get_userId()

        contacts = BOTS[userId].contact_list
        friends = []
        for user in contacts:
            friend = {
                "value":user["UserName"],
                "text":user["RemarkName"] if user["RemarkName"]!="" else user["NickName"],
                "sex": user["Sex"]
            }
            if friend['text'] != '':
                friends.append(friend)
        self.write(json.dumps(friends))

    def post(self):
        if not self.is_wechat_login():
            self.write({"ret": -1, "data": "User is not logined."})
            return

        userId = self.get_userId()

        contacts = BOTS[userId].contact_list
        search =  self.get_argument("search")
        user_list = [{
            "text": u"我的好友",
            "nodes": []
        }, {
            "text": u"我的群聊",
            "nodes": []
        }]

        for user in contacts:
            node = {
                "data":user["UserName"],
                "text":user["RemarkName"] if user["RemarkName"]!="" else user["NickName"],
                #"state": {"checked":False},
                "icon":"glyphicon-user",
                "sex": user["Sex"]
                #"selectedIcon":"glyphicon-chat"
            }
            if search != '':
                if node['text'].find(search)>=0:
                    user_list[0]['nodes'].append(node)
            else:
                user_list[0]['nodes'].append(node)
        self.write(json.dumps(user_list))

class wechaticonHandler(RobotsHandler):
    def get(self):
        if not self.is_wechat_login():
            self.write("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".decode('base64'))
            return
        weUser = self.get_argument("username")
        userId = self.get_userId()
        seq=time.time()
        url = BOTS[userId].self.base_uri+'/webwxgeticon?seq=%s&username=%s&skey=%s'%(seq, weUser, BOTS[userId].skey)
        r = BOTS[userId].session.get(url)
        data = r.content
        self.write(data)

class websocketMessageHandler(tornado.websocket.WebSocketHandler):
    waiters = set()
    cache = []
    cache_size = 200

    def get_compression_options(self):
        # Non-None enables compression with default options.
        return {}

    def open(self):
        websocketMessageHandler.waiters.add(self)
        # 推送缓存
        client_user = self.get_secure_cookie("robot_user")
        if not(client_user is None) :
            for chat in websocketMessageHandler.cache:
                try:
                    # chat_json = json.loads(chat)
                    if chat['who_weplus'] == client_user:
                        self.write_message(chat)
                except:
                    pass

    def on_close(self):
        websocketMessageHandler.waiters.remove(self)

    @classmethod
    def update_cache(cls, chat):
        cls.cache.append(chat)
        if len(cls.cache) > cls.cache_size:
            cls.cache = cls.cache[-cls.cache_size:]

    @classmethod
    def send_updates(cls, chat):
        #logging.info("sending message to %d waiters", len(cls.waiters))
        for waiter in cls.waiters:
            client_user = waiter.get_secure_cookie("robot_user")
            if client_user is None:
                continue
            try:
                #chat_json = json.loads(chat)
                if chat['who_weplus'] == client_user:
                    waiter.write_message(chat)
            except:
                logging.error("Error sending message", exc_info=True)

    def on_message(self, message):
        #logging.info("%s got message %r", (self.get_userId(),message))
        ws_user = self.get_cookie("heartbit") #内部消息转发ws客户端
        bs_user = self.get_secure_cookie("robot_user") #浏览器WebSocket
        if bs_user is None: #来自内部client的推送
            if (ws_user is not None) and (message !='6865617274626974'):
                parsed = tornado.escape.json_decode(message)
                websocketMessageHandler.update_cache(parsed)
                websocketMessageHandler.send_updates(parsed)
        elif message == '6469616e6e616f3531': #浏览器心跳
            self.write_message({"heartcheck":message})
        else:
            pass

class weixinSendHandler(RobotsHandler):
    def post(self):
        if not self.is_wechat_login():
            self.write({'ret': -1, 'msg': 'wechat is not login.'})  # ret = -1 异常
            return

        userId = self.get_userId()
        to_user = self.get_argument("to_user")
        msg_body = self.get_argument("body")
        if (BOTS[userId].send_wx_message(msg_body, to_user)):
            self.write({'ret': 0, 'msg': 'success.'})  # ret = 0 正常
        else:
            self.write({'ret': -1, 'msg': 'send fault.'})  # ret = -1 异常

            # global_message_buffer.new_messages([message])


class qrcodeHandler(RobotsHandler):
    def post(self):
        userId = self.get_userId()
        if not userId:
            return
        try:
            fname = './data/' + userId + '/wxqr.png'
            i = 0
            while not os.path.isfile(fname):
                i = i + 1
                if i > 30:
                    self.write('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')
                    break
                time.sleep(0.2)
            time.sleep(0.1)
            with open(fname, 'rb') as f:
                data = f.read()
                # print data.encode("base64")
                # self.set_header("Content-type", "image/png")
                self.write(data.encode("base64").replace("\n", ''))
                self.flush()
            self.finish()
        except:
            pass

class robot_daemon(Daemon):
    def run(self):
        main()

def stop_thread(tid):
    """raises the exception, performs cleanup if needed"""
    import inspect,ctypes
    exctype = None
    if not inspect.isclass(SystemExit):
        exctype = type(SystemExit)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
        pass
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def threadLists(userId):
    ts = []
    for t in threading.enumerate():
        ts.append(t.getName())

    wxThread = "WXThread_" + userId  # 1
    flag = 1 if wxThread in ts else 0
    return flag, ts


def runWX(threadId = "0"):
    from myBot import WXRobot
    BOTS[threadId] = WXRobot(threadId)
    BOTS[threadId].DEBUG = True
    BOTS[threadId].run()


def runWxThread(threadId):
    """
    :param 当前要启动的用户进程UserID:
    :return: 启动新进程，并且后台运行
    """
    for t in threading.enumerate():
        if "WXThread_" + threadId == t.getName():
            stop_thread(t.ident)
    time.sleep(0.2)
    if BOTS.get(threadId,None) is not None:
        BOTS.pop(threadId)
    cnf = jsonconf.load(os.path.join(os.getcwd(), 'data', 'robot_config.json'))
    for key in cnf:
        BOT_CONFIG[key] = cnf[key]
    if BOT_CONFIG == {}:
        print("load Error robot_config.json!")
        return False

    wxThread = threading.Thread(target=runWX, args=(threadId,), name="WXThread_" + threadId)
    wxThread.setDaemon(True)
    wxThread.start()

def main():
    parse_command_line()
    app = tornado.web.Application(
        [
            (r"/", indexHandler),
            (r"/login",loginHandler),
            (r"/logout", logoutHandler),
            (r"/plugin", pluginHandler),
            (r"/plugin/data", plugindataHandler),
            (r"/plugin/user", pluginuserHandler),
            (r"/weixin/threads", threadsHandler),
            (r"/weixin/contacts", contactsHandler),
            (r"/weixin/start", startHandler),
            (r"/weixin/qrcode", qrcodeHandler),
            (r"/weixin/check", checkHandler),
            (r"/weixin/sendmsg", weixinSendHandler),
            (r"/wechat", wechatHandler),
            (r"/wechat/treedata", wechattreeHandler),
            (r"/wechat/usericon", wechaticonHandler),
            (r"/wsmessage", websocketMessageHandler)
        ],
        cookie_secret="gSU0n7KIlXruWGiZQs@e",
        template_path=os.path.join(os.path.dirname(__file__), "template"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=False,
        debug=options.debug,
    )
    # runWxThread()
    app.listen(options.port, address=SRV_BIND_IP)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    os.chdir(deploy_dir)
    if sys.platform.startswith('win'):
        main()
    else:
        daemon = robot_daemon(work_dir=deploy_dir)
        if len(sys.argv) == 1:  #直接运行启动
            daemon.start()
        elif len(sys.argv) == 2:
            if 'start' == sys.argv[1]:
                daemon.start()
            elif 'stop' == sys.argv[1]:
                daemon.stop()
            elif 'restart' == sys.argv[1]:
                daemon.restart()
            else:
                print "Unknown command"
                sys.exit(2)
            sys.exit(0)
        else:
            print "usage: %s start|stop|restart" % sys.argv[0]
            sys.exit(2)