#!/usr/local/python27/bin/python
# coding: utf-8

import datetime

plugin_key = u'message_status'
plugin_name = u'机器人状态查询'
plugin_json = None

def run(wxBot, msg):
    """
    根据当前系统运行情况，发送状态信息给微信。
    """
    if msg['msg_type_id'] != 4:
        return

    if msg['content']['data'] == '@status':
        import psutil
        process = psutil.Process()
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(process.create_time())
        memory_usage = process.memory_info().rss
        sysmem = psutil.virtual_memory()
        msg_nr = '[系统CPU] {cpu}核心\n{sysmemory}\n[当前时间] {now:%H:%M:%S}\n[运行时间] {uptime}\n[内存占用] {memory}'.format(
            cpu=psutil.cpu_count(),
            sysmemory='[总内存] ' + '{:.2f} MB'.format(sysmem.total / 1024 ** 2) + '\n[空闲内存] ' + '{:.2f} MB'.format(
                sysmem.free / 1024 ** 2),
            now=datetime.datetime.now(),
            uptime=str(uptime).split('.')[0],
            memory='{:.2f} MB'.format(memory_usage / 1024 ** 2)
        )
        return wxBot.send_wx_message(msg_nr, msg['from_user']['id'])