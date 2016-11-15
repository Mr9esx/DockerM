#!/usr/bin/env python
# -*- coding: utf-8 -*-
#author:Mr9esx
#email: mr9esx1138099359@gmail.com

import json,sys,os,fcntl,time,threading,commands
import simplejson,pika,MySQLdb,psutil
import Config
import lib.Control as Control
from lib.Daemon import Daemon  
from time import sleep

def sendMsg2MQ(stats):
	try:
		credentials = pika.PlainCredentials(Config.RABBIT_USER, Config.RABBIT_PASSWD)
		connection = pika.BlockingConnection(pika.ConnectionParameters(Config.RABBIT_HOST,Config.RABBIT_PORT,Config.RABBIT_VHOST,credentials))
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
		json_Info = MySQLdb.escape_string(simplejson.dumps(Info))
		stats = {'control_type':'containerInfo','container_id':Info['Id'],'container_name':Info['Name'][1::],'image_id':Info['Image'][7::],'host_id':Config.Host_Id,'create_time':Info['Created'],'status':Info['State']['Status'],'info':json_Info}
		sendMsg2MQ(stats)
	end = time.clock()
	print "read: %f s" % (end - start)

#更新全部镜像信息
def updateAllImagesInfo():
	ImagesList = Control.DockerControl().getAllImageInfo()
	for x in ImagesList:
		image_id = x['Id']
		Info = Control.DockerControl().getImageInfo(image_id)
		json_History = MySQLdb.escape_string(simplejson.dumps(Control.DockerControl().getImageHistory(image_id)))
		json_Info = MySQLdb.escape_string(simplejson.dumps(Info))
		json_RepoTags = simplejson.dumps(Info['RepoTags'])
		stats = {'control_type':'imageInfo','image_id':Info['Id'][7:None],'image_name':json_RepoTags,'host_id':Config.Host_Id,'create_time':Info['Created'],'info':json_Info,'history':json_History}
		sendMsg2MQ(stats)

#更新全部网络信息
def updateAllNetworksInfo():
	NetworksList = Control.DockerControl().getAllNetworkInfo()
	for x in NetworksList:
		network_id = x['Id']
		Info = Control.DockerControl().getNetworkInfo(network_id)
		json_Info = MySQLdb.escape_string(simplejson.dumps(Info))
		stats = {'control_type':'networkInfo','network_id':Info['Id'],'network_name':Info['Name'],'host_id':Config.Host_Id,'network_info':json_Info}
		sendMsg2MQ(stats)

def memSize(size):
    if size >= 1000 and size < 1048576:
        return str(float('%.2f' % (size / 1024.0))) + " =KB"
    elif size >= 1048576 and size < 1073741824:
        return str(float('%.2f' % (size / 1048576.0))) + " MB"
    elif size > 1073741824:
        return str(float('%.2f' % (size / 1073741824.0))) + " GB"
    else:
        return str(size) + " B"

def updateSystemInfo():
	mem = psutil.virtual_memory()
	mem_total = memSize(mem.total)
	docker_version = commands.getstatusoutput('docker version | grep Version:')[1].split(':')[1].split('Version')[0].strip()  
	with open('/proc/cpuinfo') as f:
	    for line in f:
	    	if line.split(':')[0].strip() == 'model name':
	    		cpu_info = line.split(':')[1].strip()
	    		break
	stats = {'control_type':'system_info','host_id':Config.Host_Id,'mem_total':mem_total,'cpu_info':cpu_info,'docker_version':docker_version}
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
	updateSystemInfo()
	daemon = MyDaemon('/tmp/UpdateDockerInfo-daemon.pid')  
	if len(sys.argv) == 2:  
		if 'start' == sys.argv[1]:  
			daemon.start()  
		elif 'stop' == sys.argv[1]:  
			daemon.stop()  
		elif 'restart' == sys.argv[1]:  
			daemon.restart()  
		else:  
			print "Unknown command"  
			sys.exit(2)  
			sys.exit(0)  
	else:  
		print "usage: %s start|stop|restart" % sys.argv[0]  
		sys.exit(2)