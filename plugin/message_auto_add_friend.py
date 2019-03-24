#!/usr/local/python27/bin/python
# coding: utf-8
import os
import json

plugin_key = u'message_auto_add_friend'
plugin_name = u'自动添加好友'
plugin_json = {
  "hello":u"欢迎加我好友!"
}

def run(wxBot,msg):
    if  msg['msg_type_id'] == 37:
        plugin_config = os.path.join(wxBot.temp_pwd, 'plugin_config', 'message_auto_add_friend.json')
        if not os.path.isfile(plugin_config):
            if wxBot.DEBUG:
                print plugin_config, 'is not exists.'
            return False

        conf = {}
        try:
            with open(plugin_config, 'r') as f:
                fstr = f.read()
                conf = json.loads(fstr)
        except:
            if wxBot.DEBUG:
                print(plugin_config + '打开出错')
            pass
        #自动通过好友请求

        wxBot.apply_useradd_requests(msg['content']['data'])
        #更新下通讯录，然后就可以username，不然只能用uid。发发发消息了。
        wxBot.get_contact()
        wxBot.send_msg_by_uid(conf['hello'],msg['content']['data']['UserName'])   #主动发送文本消息