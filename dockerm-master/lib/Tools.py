# -*- coding: utf-8 -*-
#格式化XML时间格式为JavaScript十一位时间戳
import time
#格式化XML时间格式为标准时间格式
def formatXMLtime(XML):
    if 'T' in XML:
        XML = XML.replace('T', ' ')
    if 'Z' in XML:
        XML = XML.replace('Z', ' ')
    XML = XML.strip(' ')
    XML = XML[0:19]
    timeArray = time.mktime(time.strptime(XML, '%Y-%m-%d %H:%M:%S'))
    timeArray += 28800
    timeArray = time.localtime(timeArray)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)