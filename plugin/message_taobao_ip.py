#!/usr/local/python27/bin/python
# coding: utf-8
import requests

plugin_key = u'message_taobao_ip'
plugin_name = u'IP地址查询'
plugin_json = None

def run(wxBot,msg):
    """
    :param wxBot 机器人实例:
    :param msg 当前消息:
    :return: 根据消息中的ip地址，返回IP地址信息
    """
    if msg['msg_type_id'] != 4 or msg['content']['data']:
        return

    if msg['content']['data'].startswith(u'@IP'):
        IP = msg['content']['data'].replace(u'@IP:','')
        ip_taobao_api_url = "http://ip.taobao.com/service/getIpInfo.php?ip="+IP
        res = requests.get(ip_taobao_api_url).json()
        if res['code'] == 0:
            area = res["data"]["area"]
            city = res["data"]["city"]
            country = res["data"]["country"]
            isp = res["data"]["isp"]
            region = res["data"]["region"]
            info = u"%s %s %s\n%s %s" % (country, region, city,area, isp)
            wxBot.send_wx_message(info, msg['from_user']['id'])