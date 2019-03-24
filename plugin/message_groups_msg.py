#!/usr/local/python27/bin/python
# coding: utf-8

import time

plugin_key = u'message_groups_msg'
plugin_name = u'群发群消息'
plugin_json = None

def run(wxBot,msg):
    """
    向所有的群发送消息，群必须是在通讯录里面
    """
    if msg['msg_type_id'] != 1:
        return

    if msg['content']['data'].startswith(u'@所有群友'):
        sendstr = msg['content']['data'].replace(u'@所有群友','')
        sendstr = sendstr.replace(u'<br/>', u'\n')
        for u in wxBot.group_list:
            msgStr = sendstr
            wxBot.send_wx_message(msgStr, u['UserName'])
            time.sleep(1)