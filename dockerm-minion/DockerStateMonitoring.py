#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import threading
import sys
import time
import os
import json
import ConfigParser
import logging
from time import sleep

import docker
import pika

from lib.Control import DockerControl
from lib.Daemon import Daemon
from lib.Tools import formatXMLtime


def sendMsg2MQ(stats):
	try:
		credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
		connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST,RABBIT_PORT,RABBIT_VHOST,credentials))
		channel = connection.channel()
		channel.queue_declare(queue='saveData')
		channel.basic_publish(exchange='', routing_key='saveData', body=json.dumps(stats))
	except:
		logging.error('RabbitMQ Conneciton FAIL')
		sys.exit()
	connection.close()


#容器监控函数
def containerStateMonitoring(container_id):

	container_stats  = conn.getStatus(container_id)
	Flag             = False
	total_usage      = None
	system_cpu_usage = None
	percpu_usage     = None
	rx_bytes         = None
	tx_bytes         = None
	count = 0
	network_rx_packets = 0
	network_tx_packets = 0
	network_rx_bytes   = 0
	network_tx_bytes   = 0
	network_rx_dropped = 0
	network_tx_dropped = 0
	network_rx_errors  = 0
	network_tx_errors  = 0
	network_rx_speed   = 0
	network_tx_speed   = 0
	try:
		for stats in container_stats:
			if stats.has_key('networks'):
				network_name = stats['networks'].keys()[0]
			if Flag:
				#计算CPU使用率
				cpu_total_usage    = stats['cpu_stats']['cpu_usage']['total_usage'] - total_usage
				cpu_system_uasge   = stats['cpu_stats']['system_cpu_usage'] - system_cpu_usage
				cpu_num            = len(percpu_usage)
				cpu_percent        = round((float(cpu_total_usage)/float(cpu_system_uasge))*cpu_num*100.0,2)
				#计算内存使用率
				mem_usage          = stats['memory_stats']['usage']
				mem_limit          = stats['memory_stats']['limit']
				mem_percent        = round(float(mem_usage)/float(mem_limit)*100.0,2)
				#计算网络相关数据
				#目前仅能计算 bridge 网络模式的网络数据
				if stats.has_key('networks'):
					network_rx_packets = stats['networks'][network_name]['rx_packets']
					network_tx_packets = stats['networks'][network_name]['tx_packets']
					network_rx_bytes   = stats['networks'][network_name]['rx_bytes']
					network_tx_bytes   = stats['networks'][network_name]['tx_bytes']
					network_rx_dropped = stats['networks'][network_name]['rx_dropped']
					network_tx_dropped = stats['networks'][network_name]['tx_dropped']
					network_rx_errors  = stats['networks'][network_name]['rx_errors']
					network_tx_errors  = stats['networks'][network_name]['tx_errors']
					network_rx_speed   = stats['networks'][network_name]['rx_bytes']-rx_bytes
					network_tx_speed   = stats['networks'][network_name]['tx_bytes']-tx_bytes
					rx_bytes           = stats['networks'][network_name]['rx_bytes']
					tx_bytes           = stats['networks'][network_name]['tx_bytes']
				#下次计算数据保存
				total_usage        = stats['cpu_stats']['cpu_usage']['total_usage']
				system_cpu_usage   = stats['cpu_stats']['system_cpu_usage']
				percpu_usage       = stats['cpu_stats']['cpu_usage']['percpu_usage']
				if count == 10:
					stats = {'control_type':'container_state','container_id':container_id,'Cpu_percent':cpu_percent,'Memory_usage':mem_usage,'Memory_limit':mem_limit,'Memory_percent':mem_percent,'Collect_time':formatXMLtime(stats['read']),'rx_packets':network_rx_packets,'tx_packets':network_tx_packets,'rx_bytes':network_rx_bytes,'tx_bytes':network_tx_bytes,'rx_dropped':network_rx_dropped,'tx_dropped':network_tx_dropped,'rx_errors':network_rx_errors,'tx_errors':network_tx_errors,'rx_speed':network_rx_speed,'tx_speed':network_tx_speed}
					threading.Thread(target=sendMsg2MQ, args=(stats,)).start()
					count = 0
				else:
					count += 1
			else:
				total_usage        = stats['cpu_stats']['cpu_usage']['total_usage']
				system_cpu_usage   = stats['cpu_stats']['system_cpu_usage']
				percpu_usage       = stats['cpu_stats']['cpu_usage']['percpu_usage']
				if stats.has_key('networks'):
					rx_bytes           = stats['networks'][network_name]['rx_bytes']
					tx_bytes           = stats['networks'][network_name]['tx_bytes']
				Flag = True
	except Exception,ReadTimeoutError:
		# print container_id+' is OFF!'
		exit()


class MyDaemon(Daemon):
	def run(self):
		t = {}
		while True:
			for value in conn.getAllContainerInfo():
				if re.match('Up', value['Status']):
					print value['Id']
					'''
						状态为 Up 的容器
					'''
					if not t.has_key(value['Id']):
						'''
							如果线程不存在，则开启新的监控线程
						'''
						t[value['Id']] = threading.Thread(target=containerStateMonitoring, args=(value['Id'],))
						t[value['Id']].setDaemon(True)
						t[value['Id']].start()
				elif re.match('Exited', value['Status']) or re.match('Error', value['Status']):
					'''
						状态不为 Up 的容器
					'''
					if t.has_key(value['Id']):
						'''
							如果线程存在，删除 key
						'''
						t.pop(value['Id'])
			sleep(1)


if __name__ == "__main__":
	daemon = MyDaemon('/tmp/DockerStateMonitoring-daemon.pid')
	logging.basicConfig(level=logging.DEBUG,
						format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
						datefmt='%a, %d %b %Y %H:%M:%S',
						filename='/tmp/test.log',
						filemode='w')
	config = ConfigParser.ConfigParser()
	config.read('dockerm-minion.conf')
	RABBIT_USERNAME = config.get('rabbitmq', 'RABBIT_USERNAME')
	RABBIT_PASSWORD = config.get('rabbitmq', 'RABBIT_PASSWORD')
	RABBIT_HOST = config.get('rabbitmq', 'RABBIT_HOST')
	RABBIT_PORT = config.getint('rabbitmq', 'RABBIT_PORT')
	RABBIT_VHOST = config.get('rabbitmq', 'RABBIT_VHOST')
	conn = DockerControl()
	if len(sys.argv) == 2:
		if 'start' == sys.argv[1]:
			daemon.start()
		elif 'stop' == sys.argv[1]:
			daemon.stop()
		elif 'restart' == sys.argv[1]:
			daemon.restart()
		else:
			print "Unknown command"
			sys.exit(0)
	else:
		print "usage: %s start|stop|restart" % sys.argv[0]
		sys.exit(2)


