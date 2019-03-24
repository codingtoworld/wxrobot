#!/usr/local/python27/bin/python
# coding: utf-8
import requests
import random

plugin_key = u'message_kuaidi100'
plugin_name = u'快递查询'
plugin_json = None

def run(wxBot,msg):
    """
    :param wxBot 机器人实例:
    :param msg 当前消息:
    :return: 根据消息中的单号，查询快递当前信息，发送给对应微信用户
    """
    if (msg['msg_type_id'] != 4) or (msg['content']['type'] != 0):
        return

    if isinstance(msg['content']['data'],unicode) and msg['content']['data'].startswith(u'@快递查询'):
        ex_number = msg['content']['data'].replace(u'@快递查询：','')
        if ex_number.startswith(u'@快递查询'):
            ex_number = msg['content']['data'].replace(u'@快递查询:', '')
        info = get_exinfo(ex_number)
        wxBot.send_wx_message(info, msg['from_user']['id'])

def get_com_code(ex_number):
    """
    :param ex_number: 快递单号
    :return: 快递公司编码
    查询接口：http://www.kuaidi100.com/autonumber/autoComNum?text=ex_number
    """
    COM_CODE={
        'zhongtong': u'中通快递',
        'yuantong': u'圆通速递',
        'shentong': u'申通快递',
        'yunda': u'韵达快递',
        'shunfeng': u'顺丰速运',
        'tiantian': u'天天快递',
        'ems': u'EMS',
        'zhaijisong': u'宅急送',
        'suer': u'速尔快递',
        'rufengda': u'如风达',
        'quanfengkuaidi': u'全峰快递',
        'debangwuliu': u'德邦',
        'aae': u'AAE全球专递',
        'aramex': u'Aramex',
        'huitongkuaidi': u'百世汇通',
        'youzhengguonei': u'包裹信件',
        'bpost': u'比利时邮政',
        'dhl': u'DHL中国件',
        'fedex': u'FedEx国际件',
        'vancl': u'凡客配送',
        'fanyukuaidi': u'凡宇快递',
        'fedexcn': u'Fedex',
        'fedexus': u'FedEx美国件',
        'guotongkuaidi': u'国通快递',
        'koreapost': u'韩国邮政',
        'jiajiwuliu': u'佳吉快运',
        'jd': u'京东快递',
        'canpost': u'加拿大邮政',
        'jiayunmeiwuliu': u'加运美',
        'jialidatong': u'嘉里大通',
        'jinguangsudikuaijian': u'京广速递',
        'kuayue': u'跨越速递',
        'kuaijiesudi': u'快捷速递',
        'minbangsudi': u'民邦速递',
        'minghangkuaidi': u'民航快递',
        'ocs': u'OCS',
        'quanyikuaidi': u'全一快递',
        'quanchenkuaidi': u'全晨快递',
        'japanposten': u'日本邮政',
        'shenganwuliu': u'圣安物流',
        'shenghuiwuliu': u'盛辉物流',
        'tnt': u'TNT',
        'ups': u'UPS',
        'usps': u'USPS',
        'wanxiangwuliu': u'万象物流',
        'xinbangwuliu': u'新邦物流',
        'xinfengwuliu': u'信丰物流',
        'youshuwuliu': u'优速物流',
        'yuanchengwuliu': u'远成物流',
        'ytkd': u'运通中港快递',
        'ztky': u'中铁物流',
        'zengyisudi': u'增益速递'
    }
    GUESS = 'http://m.kuaidi100.com/autonumber/auto?num={0}'
    guess_url = GUESS.format(ex_number)
    content = requests.get(guess_url).json()
    if len(content) > 0:
        return content[0]['comCode'],COM_CODE[content[0]['comCode']]
    else:
        return False

def get_exinfo(ex_number):
    """
    :param ex_number: 根据快递单号，查询快递当前状态
    :return: 当前状态
    """
    QUERY = 'http://m.kuaidi100.com/query'
    com_code,company_name = get_com_code(ex_number)
    if com_code != False:
        params = {
            'type': com_code,
            'postid': ex_number,
            'id': 1,
            'valicode': '',
            'temp': random.random()
        }
        res = requests.get(QUERY,params = params).json()
        if res['status'] == '200':
            table = format_info(res,company_name)
            return table
        else:
            return u"Error:"+res['message']
    else:
        return "Wrong Express Number!"

def format_info(data,company_name):
    res = u'单号：'+data["nu"]+u'\n公司: '+company_name+u'\n快件路由：\n'.format()
    for item in data['data']:
        res += '-' * 30 + '\n'
        res += u'{time: ^21}\n {context}\n'.format(**item)
    res += '=' * 20 + '\n'
    return res

if __name__ == '__main__':
    print get_exinfo('11707179564548')
