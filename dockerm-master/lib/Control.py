# -*- coding: utf-8 -*-
import time
import sys
import os
import ConfigParser
import MySQLdb

import simplejson
import pika

import lib.Tools as Tools


class MySQLControl(object):
	def __init__(self):
		config = ConfigParser.SafeConfigParser()
		config.read('dockerm-master.conf')
		MYSQL_HOST = config.get('mysql','MYSQL_HOST')
		MYSQL_USERNAME = config.get('mysql','MYSQL_USERNAME')
		MYSQL_PASSWORD = config.get('mysql','MYSQL_PASSWORD')
		MYSQL_PORT = config.getint('mysql','MYSQL_PORT')
		MYSQL_DATABASE =config.get('mysql','MYSQL_DATABASE')
		self.__db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USERNAME, passwd=MYSQL_PASSWORD, db=MYSQL_DATABASE, port=MYSQL_PORT)

	def insert(self, sql, data):
		cur = self.__db.cursor()
		cur.execute(sql % data)
		self.__db.commit()
		cur.close()
		self.__db.close()

	def select(self, sql):
		cur = self.__db.cursor(cursorclass=MySQLdb.cursors.DictCursor)
		result = cur.fetchmany(cur.execute(sql))
		cur.close()
		self.__db.close()
		return result


#操作容器后更新容器状态和JSON信息
def updateContainerInfo(container_id):
	info = DockerControl().getContainerInfo(container_id)
	json_Info = MySQLdb.escape_string(simplejson.dumps(Info))
	return info, json_Info
	# sql = "UPDATE containers SET status='%s',info='%s' WHERE container_id='%s';" % (Info['State']['Status'],json_Info,container_id)
	# MySQLControl().insert(sql)

#如果容器已被删除，则更新数据库状态
#界面添加重新创建功能
def ifDeletedUpdateBD(container_id):
	MySQLControl().insert("UPDATE containers SET status='%s' WHERE container_id='%s';" % ("deleted",container_id))

#从数据库删除
def deletedContainer(container_id):
	print "deleted!"
	MySQLControl().insert("DELETE FROM containers WHERE container_id = '%s'" % container_id)