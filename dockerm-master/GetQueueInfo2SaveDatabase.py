# !/usr/bin/env python
# coding=utf8
# author:Mr9esx
# email: mr9esx1138099359@gmail.com

import sys
import os
import signal
import json
import threading
import time
import ConfigParser
from datetime import datetime

import pika
import simplejson
import MySQLdb

from lib.Control import MySQLControl
from lib.Daemon import Daemon


class Watcher:
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
        credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, RABBIT_VHOST, credentials))
        channel = connection.channel()
        channel.queue_declare(queue='saveData')
    except:
        print 'RabbitMQ Conneciton FAIL'
        sys.exit()

    def callback(ch, method, properties, body):
        msg = json.loads(body)
        print msg['control_type']
        if msg.has_key('saltstack_id') and len(MySQLControl().select(("SELECT saltstack_id FROM hosts WHERE saltstack_id='{}';").format(msg['saltstack_id']))) == 1:
            if msg['control_type'] == 'container_info':
                sql = 'INSERT INTO containers(container_id, container_name, image_id, saltstack_id, created_at, status, info) VALUES("%s","%s","%s","%s","%s","%s","%s") ON DUPLICATE KEY UPDATE status="%s", info="%s";'
                msg['info'] = MySQLdb.escape_string(msg['info'])
                data = (msg['container_id'], MySQLdb.escape_string(msg['container_name']), msg['image_id'],
                        msg['saltstack_id'], msg['created_at'], msg['status'], msg['info'], msg['status'], msg['info'])
            elif msg['control_type'] == 'image_info':
                sql = 'INSERT INTO images(image_id, image_name, saltstack_id, created_at, info, history) VALUES("%s","%s","%s","%s","%s","%s") ON DUPLICATE KEY UPDATE info="%s";'
                msg['info'] = MySQLdb.escape_string(msg['info'])
                data = (msg['image_id'], MySQLdb.escape_string(msg['image_name']), msg['saltstack_id'],
                        msg['created_at'], msg['info'], MySQLdb.escape_string(msg['history']), msg['info'])
            elif msg['control_type'] == 'network_info':
                sql = 'INSERT INTO networks(network_id,network_name,saltstack_id,network_info) VALUES("%s","%s","%s","%s") ON DUPLICATE KEY UPDATE network_info="%s", network_id="%s";'
                msg['network_info'] = MySQLdb.escape_string(msg['network_info'])
                data = (msg['network_id'], MySQLdb.escape_string(msg['network_name']), msg['saltstack_id'],
                        msg['network_info'], msg['network_info'], msg['network_id'])
            elif msg['control_type'] == 'operation_log':
                sql = 'INSERT INTO operation_log(operation_time, saltstack_id, operation_type ,operation_id, operation_user, operation_result) VALUES("%s","%s","%s","%s","%s","%s");'
                data = (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), msg['saltstack_id'], msg['logs_type'],
                        msg['container_id'], msg['username'], msg['result'])
            MySQLControl().insert(sql, data)
        else:
            if msg['control_type'] == 'container_state':
                sql = 'INSERT INTO container_state(container_id,Cpu_percent,Memory_usage,Memory_limit,Memory_percent,Collect_time,rx_packets,tx_packets,rx_bytes,tx_bytes,rx_dropped,tx_dropped,rx_errors,tx_errors,rx_speed,tx_speed) VALUES("%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s","%s");'
                data = (msg['container_id'], msg['Cpu_percent'], msg['Memory_usage'], msg['Memory_limit'],
                        msg['Memory_percent'], msg['Collect_time'], msg['rx_packets'], msg['tx_packets'],
                        msg['rx_bytes'], msg['tx_bytes'], msg['rx_dropped'], msg['tx_dropped'], msg['rx_errors'],
                        msg['tx_errors'], msg['rx_speed'], msg['tx_speed'])
            elif msg['control_type'] == 'update_container':
                info = simplejson.loads(msg['info'])
                if info['State'].has_key('Type') and info['State']['Type'] == 'notfound':
                    sql = 'UPDATE containers SET status="%s" WHERE container_id="%s";'
                    data = (info['State']['Status'], msg['container_id'])
                else:
                    sql = 'UPDATE containers SET status="%s",info="%s" WHERE container_id="%s";'
                    data = (info['State']['Status'], MySQLdb.escape_string(msg['info']), msg['container_id'])
            MySQLControl().insert(sql, data)

        ch.basic_ack(delivery_tag=method.delivery_tag)
    channel.basic_consume(callback, queue='saveData', no_ack=False)
    channel.start_consuming()
    connection.close()


def get_queue_size():
    credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RABBIT_HOST, RABBIT_PORT, RABBIT_VHOST, credentials))
    channel = connection.channel()
    result = channel.queue_declare(queue='saveData')
    return result.method.message_count

if __name__ == "__main__":
    Watcher()
    config = ConfigParser.SafeConfigParser()
    config.read('dockerm-master.conf')
    RABBIT_USERNAME = config.get('rabbitmq', 'RABBIT_USERNAME')
    RABBIT_PASSWORD = config.get('rabbitmq', 'RABBIT_PASSWORD')
    RABBIT_HOST = config.get('rabbitmq', 'RABBIT_HOST')
    RABBIT_PORT = int(config.get('rabbitmq', 'RABBIT_PORT'))
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