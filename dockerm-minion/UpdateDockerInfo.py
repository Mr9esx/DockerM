#!/usr/bin/env python
# -*- coding: utf-8 -*-
#author:Mr9esx
#email: mr9esx1138099359@gmail.com

import json
import sys
import os
import fcntl
import time
import threading
import commands
from time import sleep

import simplejson
import pika
import ConfigParser
import salt.config

import lib.Control as Control
from lib.Daemon import Daemon  


def sendMsg2MQ(stats):
	try:
		credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
		connection = pika.BlockingConnection(
			pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, RABBIT_VHOST, credentials))
		channel = connection.channel()
		channel.queue_declare(queue='saveData')
		channel.basic_publish(exchange='', routing_key='saveData', body=json.dumps(stats))
		connection.close()
	except:
		print 'RabbitMQ Conneciton FAIL'
		sys.exit()

#更新全部容器信息
def updateAllContainersInfo():
	start = time.clock()
	DockerContainersList = Control.DockerControl().getAllContainerInfo()
	for x in DockerContainersList:
		container_id = x['Id']
		Info = Control.DockerControl().getContainerInfo(container_id)
		json_Info = simplejson.dumps(Info)
		stats = {'control_type':'container_info','container_id':Info['Id'],'container_name':Info['Name'][1::],'image_id':Info['Image'][7::],'saltstack_id':SALTSTACK_ID,'created_at':Info['Created'],'status':Info['State']['Status'],'info':json_Info}
		sendMsg2MQ(stats)
	end = time.clock()
	print "read: %f s" % (end - start)

#更新全部镜像信息
def updateAllImagesInfo():
	ImagesList = Control.DockerControl().getAllImageInfo()
	for x in ImagesList:
		image_id = x['Id']
		Info = Control.DockerControl().getImageInfo(image_id)
		json_History = simplejson.dumps(Control.DockerControl().getImageHistory(image_id))
		json_Info = simplejson.dumps(Info)
		json_RepoTags = simplejson.dumps(Info['RepoTags'])
		stats = {'control_type':'image_info','image_id':Info['Id'][7:None],'image_name':json_RepoTags,'saltstack_id':SALTSTACK_ID,'created_at':Info['Created'],'info':json_Info,'history':json_History}
		sendMsg2MQ(stats)

#更新全部网络信息
def updateAllNetworksInfo():
	NetworksList = Control.DockerControl().getAllNetworkInfo()
	for x in NetworksList:
		network_id = x['Id']
		Info = Control.DockerControl().getNetworkInfo(network_id)
		json_Info = simplejson.dumps(Info)
		stats = {'control_type':'network_info','network_id':Info['Id'],'network_name':Info['Name'],'saltstack_id':SALTSTACK_ID,'network_info':json_Info}
		sendMsg2MQ(stats)

def runupdateAllImagesInfo():
	while True:
		updateAllImagesInfo()
		time.sleep(180)

def runupdateAllNetworksInfo():
	while True:
		updateAllNetworksInfo()
		time.sleep(180)

class MyDaemon(Daemon):
	def run(self):
		t1 = threading.Thread(target=runupdateAllImagesInfo)
		t2 = threading.Thread(target=runupdateAllNetworksInfo)
		t1.setDaemon(True)
		t2.setDaemon(True)
		t1.start()
		t2.start()
		while True:
			updateAllContainersInfo()
			time.sleep(10)

if __name__ == "__main__":
	daemon = MyDaemon('/tmp/UpdateDockerInfo-daemon.pid')
	config = ConfigParser.SafeConfigParser()
	config.read('dockerm-minion.conf')
	SALTSTACK_ID = salt.config.minion_config('/etc/salt/minion')['id']
	RABBIT_USERNAME = config.get('rabbitmq', 'RABBIT_USERNAME')
	RABBIT_PASSWORD = config.get('rabbitmq', 'RABBIT_PASSWORD')
	RABBIT_HOST = config.get('rabbitmq', 'RABBIT_HOST')
	RABBIT_PORT = config.getint('rabbitmq', 'RABBIT_PORT')
	RABBIT_VHOST = config.get('rabbitmq', 'RABBIT_VHOST')
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