# -*- coding: utf-8 -*-
import docker
import time
import sys
import os
import ConfigParser

import simplejson
import pika

import lib.Tools as Tools


class DockerControl(object):


	def __init__(self):
		self.__conn = docker.APIClient(base_url='unix:///var/run/docker.sock', timeout=10)


	"""删除容器"""
	def delete_container(self,container_id):
		try:
			self.__conn.remove_container(container_id)
			return self.getContainerInfo(container_id), 'success'
		except Exception, NotFound:
			return self.getContainerInfo(container_id), 'notfound'


	"""启动容器"""
	def start_container(self,container_id):
		try:
			self.__conn.start(container_id)
			return self.getContainerInfo(container_id), 'success'
		except Exception,NotFound:
			return self.getContainerInfo(container_id), 'notfound'


	"""停止容器"""
	def stop_container(self,container_id):
		try:
			self.__conn.stop(container_id)
			return self.getContainerInfo(container_id), 'success'
		except Exception,NotFound:
			return self.getContainerInfo(container_id), 'notfound'


	"""暂停容器"""
	def pause_container(self,container_id):
		try:
			self.__conn.pause(container_id)
			return self.getContainerInfo(container_id), 'success'
		except Exception, NotFound:
			return self.getContainerInfo(container_id), 'notfound'


	"""恢复容器"""
	def unpause_container(self,container_id):
		try:
			self.__conn.unpause(container_id)
			return self.getContainerInfo(container_id), 'success'
		except Exception, NotFound:
			return self.getContainerInfo(container_id), 'notfound'


	"""创建"""
	def create_container(self, container_name, hostname, image, link, port, command):
		try:
			container = self.__conn.create_container(name=container_name, hostname=hostname, image=image, ports=port, links=link, command=command)
			status = container['Warnings']
			container_id = container['Id']
			if status == None:
				return self.getContainerInfo(container_id), 'success'
			else:
				return status, 'error'
		except Exception, NotFound:
			updateContainerInfo(container_id)


	"""删除镜像"""
	def delete_image(self,image_id):
		try:
			pass
		except Exception,NotFound:
			pass


	"""十五条日志"""
	def logs(self,container_id):
		top_ten_log = ''
		try:
			top_ten_log = self.__conn.logs(containerID,tail=15)
			sql = "UPDATE containers SET top_ten_logs='"+top_ten_log+"' WHERE container_id='"+container_id+"';"
			MySQLControl().insert(sql)
		except Exception,e:
			print e


	"""获取全部容器基础信息"""
	def getAllContainerInfo(self):
		try:
			return self.__conn.containers(all=True)
		except Exception,e:
			print e


	"""获取单个容器详细信息"""
	def getContainerInfo(self,container_id):
		try:
			ContainerInfo = self.__conn.inspect_container(container_id)
			ContainerInfo['State']['FinishedAt'] = Tools.formatXMLtime(ContainerInfo['State']['FinishedAt'])
			ContainerInfo['State']['StartedAt'] = Tools.formatXMLtime(ContainerInfo['State']['StartedAt'])
			ContainerInfo['Created'] = Tools.formatXMLtime(ContainerInfo['Created'])
			return ContainerInfo
		except Exception,e:
			print e


	"""获取全部镜像基础信息"""
	def getAllImageInfo(self):
		try:
			return self.__conn.images()
		except Exception,e:
			print e


	"""获取单个镜像详细信息"""
	def getImageInfo(self,image_id):
		try:
			ImageInfo = self.__conn.inspect_image(image_id)
			ImageInfo['Created'] = Tools.formatXMLtime(ImageInfo['Created'])
			return ImageInfo
		except Exception,e:
			print e


	"""获取镜像构建历史信息"""
	def getImageHistory(self,image_id):
		try:
			ImageHistoryInfo = self.__conn.history(image_id)
			return ImageHistoryInfo
		except Exception,e:
			print e


	"""获取全部网络信息"""
	def getAllNetworkInfo(self):
		try:
			return self.__conn.networks()
		except Exception,e:
			print e

	#获取指定网络详细信息
	def getNetworkInfo(self,network_id):
		try:
			return self.__conn.inspect_network(network_id)
		except Exception,e:
			print e

	def getStatus(self,container_id):
		try:
			State = self.__conn.stats(container_id,decode=True)
		except Exception,ReadTimeoutError:
			print container_id+'is OFF!'
		return State

	def getAllContainerInfo(self):
		return self.__conn.containers(all=True)


#如果容器已被删除，则更新数据库状态
#界面添加重新创建功能
def ifDeletedUpdateBD(container_id):
	MySQLControl().insert("UPDATE containers SET status='%s' WHERE container_id='%s';" % ("deleted",container_id))

#从数据库删除
def deletedContainer(container_id):
	print "deleted!"
	MySQLControl().insert("DELETE FROM containers WHERE container_id = '%s'" % container_id)