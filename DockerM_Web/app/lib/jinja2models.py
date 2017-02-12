# -*- coding:utf-8 -*-
import json
import time
import datetime
import re


# 格式化显示在JSON信息页面的json信息
def showJsonPage(jsonstr):
    return json.dumps(jsonstr, indent=4);


# 格式化网络json信息
def formatNetwrokJson(jsonstr):
    tmp = []
    for (d, x) in jsonstr.items():
        ip = jsonstr[d]['IPAddress']
        gateway = jsonstr[d]['Gateway']
        mac = jsonstr[d]['MacAddress']
        if jsonstr[d]['IPAddress'] == '':
            ip = 'None'
        if jsonstr[d]['Gateway'] == '':
            gateway = 'None'
        if jsonstr[d]['MacAddress'] == '':
            mac = 'None'
        tmp.append({"Network_name": d, "IPAddress": ip, "Gateway": gateway, "MacAddress": mac,
                    "IPPrefixLen": jsonstr[d]['IPPrefixLen']})
    return tmp


"""验证 IP 地址合法性"""
def validataipaddress(ipaddress):
    validata = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')
    if validata.match(ipaddress):
        return True
    else:
        return False


    # 格式化端口json信息
def formatPortsJson(jsonstr, host_id):
    from dbController import getHostInfo
    tmp = []
    link = 'javascript:;'
    outside_port = None
    if jsonstr == {} or jsonstr == None:
        tmp.append({"inside_port": u'内部无端口开放', "outside_port": u'外部无端口开放', "link": link})
    else:
        for (d, x) in jsonstr.items():
            inside_port = d
            if x == None or x == 'None':
                outside_port = u'外部无端口开放'
            else:
                link = "http://" + getHostInfo(host_id).host_ip + ":" + jsonstr[d][0][
                    'HostPort']
                outside_port = jsonstr[d][0]['HostIp'] + ":" + jsonstr[d][0]['HostPort']
            tmp.append({"inside_port": inside_port, "outside_port": outside_port, "link": link})
    return tmp


# 裁剪字符串
def cutStr(str, start, end=None):
    return str[start:end]


# 计算开始到结束的时间
def stopRunTime(start, finish):
    start = time.strptime(start, "%Y-%m-%d %H:%M:%S")
    finish = time.strptime(finish, "%Y-%m-%d %H:%M:%S")
    date1 = datetime.datetime(start[0], start[1], start[2], start[3], start[4], start[5])
    date2 = datetime.datetime(finish[0], finish[1], finish[2], finish[3], finish[4], finish[5])
    return date1 - date2


# 计算开始到现在的时间
def nowRunTime(start):
    start = time.strptime(start, "%Y-%m-%d %H:%M:%S")
    finish = time.localtime()
    date1 = datetime.datetime(start[0], start[1], start[2], start[3], start[4], start[5])
    date2 = datetime.datetime(finish[0], finish[1], finish[2], finish[3], finish[4], finish[5])
    return date2 - date1


# 转换镜像大小
def imageSize(size):
    if size >= 1000 and size < 1048576:
        return str(float('%.2f' % (size / 1000.0))) + " =KB"
    elif size >= 1048576 and size < 1073741824:
        return str(float('%.2f' % (size / 1000000.0))) + " MB"
    elif size > 1073741824:
        return str(float('%.2f' % (size / 1000000000.0))) + " GB"
    else:
        return str(size) + " B"


# 获取镜像名称
def getImageName(image_name):
    return json.loads(image_name)[0]
    # tmp = image_name.rfind(':')
    # return image_name[:tmp]


# 获取镜像版本
def getImageVer(image_name):
    # tmp = image_name.rfind(':')
    # return image_name[tmp + 1:]
    tmp = json.loads(image_name)[0]
    return tmp[tmp.rfind(':') + 1:]

#时间戳转标准时间
def strptime2time(strptime):
    x = time.localtime(strptime)
    return time.strftime('%Y-%m-%d %H:%M:%S', x)
