#!/usr/bin/env python
#coding=utf8
import sys,os,signal,json,threading,sys
import ConfigParser
from time import sleep

import pika
import simplejson
import salt.config

from lib.Control import DockerControl

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


def sendMsg2MQ(stats):
    try:
        credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, RABBIT_VHOST, credentials))
        channel = connection.channel()
        channel.queue_declare(queue='saveData')
        channel.basic_publish(exchange='', routing_key='saveData', body=json.dumps(stats))
    except:
        print 'RabbitMQ Conneciton FAIL'
        sys.exit()
    connection.close()


def formatLogsStats(logs_type, result, container_id , saltstack_id, username):
    return {'control_type': 'operation_log', 'logs_type': logs_type, 'container_id': container_id, 'username': username, 'saltstack_id': saltstack_id, 'result': result}


def formatUpdateStats(info, container_id):
    json_info = simplejson.dumps(info)
    return {'control_type': 'update_container', 'status': info['State']['Status'], 'info': json_info,
			'container_id': container_id}


def main():
    try:
        credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, RABBIT_VHOST, credentials))
        channel = connection.channel()
        channel.queue_declare(queue=HOST_ID)
    except:
        print 'RabbitMQ Conneciton FAIL'
        sys.exit()

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        conn = DockerControl()
        if msg['control_type'] == 'start':
            info, result = conn.start_container(msg['body']['container_id'])
            print result
            if result == 'notfound':
                info = {'State': {'Status': 'deleted', 'Type': 'notfound'}}
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            else:
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            sendMsg2MQ(
                    formatLogsStats(msg['control_type'], result, msg['body']['container_id'], HOST_ID, msg['username']))

        elif msg['control_type'] == 'stop':
            info, result = conn.stop_container(msg['body']['container_id'])
            if result == 'notfound':
                info = {'State': {'Status': 'deleted', 'Type': 'notfound'}}
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            else:
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            sendMsg2MQ(
                    formatLogsStats(msg['control_type'], result, msg['body']['container_id'], HOST_ID, msg['username']))

        elif msg['control_type'] == 'del':
            info, result = conn.create_container(msg['body']['container_id'])
            if result == 'notfound':
                info = {'State': {'Status': 'deleted', 'Type': 'notfound'}}
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            else:
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            sendMsg2MQ(
                    formatLogsStats(msg['control_type'], result, msg['body']['container_id'], HOST_ID, msg['username']))

        elif msg['control_type'] == 'create':
            info, result = conn.create_container(msg['body']['container_name'], msg['body']['hostname'], msg['body']['image'], msg['body']['port'], msg['body']['link'], msg['body']['command'])
            if result != 'error':
                sendMsg2MQ(formatUpdateStats(info, msg['body']['container_id']))
            sendMsg2MQ(
                formatLogsStats(msg['control_type'], result, msg['body']['container_id'], HOST_ID, msg['username']))
        elif msg['control_type'] == 'system_info':
            pass
        ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_consume(callback, queue=HOST_ID,no_ack=False)
    channel.start_consuming()
    connection.close()


def get_queue_size():
    credentials = pika.PlainCredentials(RABBIT_USERNAME,RABBIT_PASSWORD)
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBIT_HOST,RABBIT_PORT,RABBIT_VHOST,credentials))
    channel = connection.channel()
    result = channel.queue_declare(queue=HOST_ID)
    return result.method.message_count


if __name__ == "__main__":
    Watcher()
    config = ConfigParser.SafeConfigParser()
    config.read('dockerm-minion.conf')
    HOST_ID = salt.config.minion_config('/etc/salt/minion')['id']
    RABBIT_USERNAME = config.get('rabbitmq', 'RABBIT_USERNAME')
    RABBIT_PASSWORD = config.get('rabbitmq', 'RABBIT_PASSWORD')
    RABBIT_HOST = config.get('rabbitmq', 'RABBIT_HOST')
    RABBIT_PORT = config.getint('rabbitmq', 'RABBIT_PORT')
    RABBIT_VHOST = config.get('rabbitmq', 'RABBIT_VHOST')
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
        sleep(1)