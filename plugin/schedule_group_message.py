#!/usr/local/python27/bin/python
# coding: utf-8

import os
import json
import datetime

plugin_key = u'schedule_group_message'
plugin_name = u'定时群发信息'
plugin_json ={
  "except":[],
  "toWeek":[0,1,2,3,4,5,6],
  "toTime":["1010","1011","1012"],
  "format":u"弟兄姊妹们平安！"
}

def run(wxBot):
    """
    消息群发给所有好友
    """
    plugin_config = os.path.join(wxBot.temp_pwd, 'plugin_config', 'schedule_group_message.json')
    if not os.path.isfile(plugin_config):
        if wxBot.DEBUG:
            print plugin_config, 'is not exists.'
        return False

    conf = {}
    try:
        with open(plugin_config, 'r') as f:
            fstr = f.read()
            conf = json.loads(fstr)

            now = datetime.datetime.now()
            weekD = now.weekday()
            send_date = now + datetime.timedelta(days=1)
            cron = now.strftime("%H%M")
            key = send_date.strftime("%Y-%m-%d")

            notSend = conf["except"]
            sendWD = conf["toWeek"]
            sendTM = conf["toTime"]
            sendstr = conf["format"]
            if (weekD in sendWD) and (cron in sendTM):
                for u in wxBot.contact_list:
                    if not u['NickName'] in notSend:
                        wxBot.send_wx_message(sendstr, u['UserName'])
    except:
        if wxBot.DEBUG:
            print(plugin_config + u'打开出错')
        pass