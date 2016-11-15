#!/usr/bin/env python
#coding=utf8
import sys,os,signal,json,threading,sys
import pika,simplejson
import Config
from lib.Control import MySQLControl
from time import sleep


class Watcher():
    def __init__(self):
        self.child = os.fork()
        if self.child == 0:
            return
        else:
            self.watch()
    def watch(self):
        try:
            os.wait()
        except KeyboardInterrupt:
            self.kill()
        sys.exit()

    def kill(self):
        try:
            os.kill(self.child, signal.SIGKILL)
        except OSError:
            pass

def main():
    try:
        credentials = pika.PlainCredentials(Config.RABBIT_USER, Config.RABBIT_PASSWD)
    	connection = pika.BlockingConnection(pika.ConnectionParameters(Config.RABBIT_HOST,Config.RABBIT_PORT,Config.RABBIT_VHOST,credentials))
        channel = connection.channel()
        channel.queue_declare(queue='saveData')
    except:
        print 'RabbitMQ Conneciton FAIL'
        sys.exit()

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        if msg.has_key('host_id'):
            host_name = MySQLControl().select(("SELECT host_name FROM hosts WHERE host_id='{}';").format(msg['host_id']))[0]['host_name']
        if msg['control_type'] == 'containerState':
        	sql = "INSERT INTO container_state(container_id,Cpu_percent,Memory_usage,Memory_limit,Memory_percent,Collect_time,rx_packets,tx_packets,rx_bytes,tx_bytes,rx_dropped,tx_dropped,rx_errors,tx_errors,rx_speed,tx_speed) VALUES('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}','{}');".format(msg['container_id'],msg['Cpu_percent'],msg['Memory_usage'],msg['Memory_limit'],msg['Memory_percent'],msg['Collect_time'],msg['rx_packets'],msg['tx_packets'],msg['rx_bytes'],msg['tx_bytes'],msg['rx_dropped'],msg['tx_dropped'],msg['rx_errors'],msg['tx_errors'],msg['rx_speed'],msg['tx_speed'])
        elif msg['control_type'] == 'containerInfo':
            sql = "INSERT INTO containers(container_id,container_name,image_id,host_name,host_id,create_time,status,info) VALUES('{}','{}','{}','{}','{}','{}','{}','{}') ON DUPLICATE KEY UPDATE status='{}',info='{}';".format(msg['container_id'],msg['container_name'],msg['image_id'],host_name,msg['host_id'],msg['create_time'],msg['status'],msg['info'],msg['status'],msg['info'])
        elif msg['control_type'] == 'imageInfo':
            sql = "INSERT INTO images(image_id,image_name,host_name,host_id,create_time,info,history) VALUES('{}','{}','{}','{}','{}','{}','{}') ON DUPLICATE KEY UPDATE info='{}';".format(msg['image_id'],msg['image_name'],host_name,msg['host_id'],msg['create_time'],msg['info'],msg['history'],msg['info'])
        elif msg['control_type'] == 'networkInfo':
            sql = "INSERT INTO networks(network_id,network_name,host_name,host_id,network_info) VALUES('{}','{}','{}','{}','{}') ON DUPLICATE KEY UPDATE network_info='{}',network_id='{}';".format(msg['network_id'],msg['network_name'],host_name,msg['host_id'],msg['network_info'],msg['network_info'],msg['network_id'])
        elif msg['control_type'] == 'system_info':
            sql = "INSERT INTO system_info(host_id,system_release,docker_version,cpu_info,mem_info,disk_info) VALUES('{}','{}','{}','{}','{}','{}') ON DUPLICATE KEY UPDATE system_release='{}',docker_version='{}',cpu_info='{}',mem_info='{}',disk_info='{}';".format(msg['host_id'],'Ubuntu 15.10 amd64',msg['docker_version'],msg['cpu_info'],msg['mem_total'],'None','Ubuntu 15.10 amd64',msg['docker_version'],msg['cpu_info'],msg['mem_total'],'None')
        MySQLControl().insert(sql)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_consume(callback, queue='saveData',no_ack=False)
    channel.start_consuming()
    connection.close()

def get_queue_size():
    credentials = pika.PlainCredentials(Config.RABBIT_USER, Config.RABBIT_PASSWD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(Config.RABBIT_HOST,Config.RABBIT_PORT,Config.RABBIT_VHOST,credentials))
    channel = connection.channel()
    result = channel.queue_declare(queue='saveData')
    return result.method.message_count

if __name__ == "__main__":
    Watcher()
    while 1:
        queue_size = get_queue_size()
        if queue_size > 10:
            thread_num = 5
        else:
            thread_num = 2
        if queue_size > 0:
            t = []
            for i in range(thread_num):
                t.append(threading.Thread(target=main, args=()))
                t[i].setDaemon(True)
                t[i].start()
            for x in t:
                x.join()