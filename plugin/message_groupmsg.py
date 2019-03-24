#!/usr/local/python27/bin/python
# coding: utf-8

import time

plugin_key = u'message_groupmsg'
plugin_name = u'群发用户消息'
plugin_json = None

def run(wxBot,msg):
    """
    消息群发给所有好友
    """
    if msg['msg_type_id'] != 1:#必须是自己发送
        return

    if msg['content']['data'].startswith(u'@所有好友'):
        sendstr = msg['content']['data'].replace(u'@所有好友','')
        sendstr = sendstr.replace(u'<br/>', u'\n')
        for u in wxBot.contact_list:
            msgStr = u['NickName'] + u'您好！\n' + sendstr
            wxBot.send_wx_message(msgStr, u['UserName'])
            time.sleep(1)