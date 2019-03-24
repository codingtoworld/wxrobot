#!/usr/local/python27/bin/python
# coding: utf-8
import os
import json
import requests

BOTS={}
BOTS_SESSION={} #每一个进程对应的SafeSession
BOT_CONFIG={} #机器人通用配置
SRV_BIND_IP='192.168.0.1'
SRV_LISTEN_PORT=8000

class jsonconf():

    @staticmethod
    def load(config_file):
        if not os.path.isfile(config_file):
            return None
        try:
            with open(config_file) as f:
                config = json.loads(f.read())
                return config
        except:
            return None

    @staticmethod
    def save(json_conf,config_file):
        with open(config_file, 'w') as f:
            f.write(json.dumps(json_conf))

def wepcrm_login(email,password):
    if BOT_CONFIG == {}:
        cnf = jsonconf.load(os.path.join(os.getcwd(), 'data', 'robot_config.json'))
        for key in cnf:
            BOT_CONFIG[key] = cnf[key]

    if BOTS_SESSION.get(email,None) is None:
        BOTS_SESSION[email] = requests.session()

    domain = BOT_CONFIG['weplus_host'].replace('https://', '').replace('http://', '')
    login_url = BOT_CONFIG['weplus_host']+'/sessions/login'
    BOTS_SESSION[email].get(login_url)
    cookies = BOTS_SESSION[email].cookies.get_dict(domain)

    if cookies.get('ip_csrf_cookie',None) is None:
        BOTS_SESSION.pop(email)
        return False

    data = {"_ip_csrf":cookies['ip_csrf_cookie'],'email':email,'password':password,'btn_login':'true',"from_robot":'true'}
    r = BOTS_SESSION[email].post(login_url, data)
    try:
        res = r.json()
        if res['ret'] == 0 and res['msg'] == 'login success':
            return True
        else:
            BOTS_SESSION.pop(email)
            return False
    except:
        BOTS_SESSION.pop(email)
        return False