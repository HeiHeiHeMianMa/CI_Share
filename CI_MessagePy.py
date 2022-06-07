#  -*- coding:utf-8 -*-
import json
import sys
import urllib.request
import os
import time
import requests

global address  # 目标地址
global args  # 打包参数

global config  # 配置

global logPath  # log地址
global svnVersion  # svn更新版本


def Init():
    global address  # 目标地址
    global args  # 打包参数

    sysArgv1 = sys.argv[1]
    sysArgv2 = sys.argv[2]
    # sysArgv1 = 'http://192.168.9.10:9011/'
    # sysArgv2 = 'false,true,true,true,None,None,false'

    address = sysArgv1
    args = sysArgv2


def LoadConfig():
    global config  # 配置

    configPath = '//127.0.0.1\CI\CI_Config.json'
    with open(configPath, "r", encoding='utf-8') as f:
        row_data = json.load(f)
    for i in row_data:
        if i["address"] == address:
            config = i
            return
    Log("没有匹配的address: " + address)


def Post():
    global logPath  # log地址
    global svnVersion  # svn更新版本

    dataDic = {'args': args}
    Log("Python request: " + str(dataDic))
    resp = http_post(address, dataDic).decode("utf-8")
    Log("Python response: " + str(resp))    

    foo = resp.split(",");
    logPath = foo[0]
    svnVersion = foo[1]
    
    ToWXWork(config["wxwStartMG"] + "\nsvn最新版本号: " + svnVersion)


def http_post(url, data_dic):
    data = urllib.parse.urlencode(data_dic).encode("utf-8")
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    return response.read()


def monitor_unity_log(target_log):
    pos = 0
    while True:
        if os.path.exists(logPath):
            break
        else:
            time.sleep(0.1)
    while True:
        fd = open(logPath, 'r', encoding='utf-8-sig', errors='ignore')
        if 0 != pos:
            fd.seek(pos, 0)
        while True:
            line = fd.readline()
            pos = pos + len(line)
            if not line:
                time.sleep(2)
            else:
                Log(line)
                if target_log in line:
                    Log("打包结束")
                    fd.close()
                    ToWXWork("自动打包完成")
                    return
        fd.close()


def ToWXWork(content):
    URL = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=" + config["wxwKey"]
    json = {
        "msgtype": "text",
        "text": {
            "content": content,
            # "mentioned_mobile_list": ["17610476767"]
        }
    }
    # 必须用json
    requests.post(url=URL, json=json)


def Log(str):
    print(str)
    sys.stdout.flush()


if __name__ == '__main__':
    Init()
    LoadConfig()
    Post()
    monitor_unity_log('自动打包完成')
    Log('done')
