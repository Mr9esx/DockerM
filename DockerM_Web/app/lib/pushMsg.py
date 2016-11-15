# -*- coding:utf-8 -*-
import pika,json
from flask import current_app
from dbModel import getHostInfoByContainerID

class pushMsg(object):

    def __init__(self, container_id, control_type):
        self.container_id = container_id
        self.control_type = control_type
        self.host_id = getHostInfoByContainerID(container_id)

    def push(self):
        app = current_app._get_current_object()
        msg = json.dumps({'controlType': self.control_type, 'container_id': self.container_id})
        credentials = pika.PlainCredentials(app.config['RABBITMQ_USER'], app.config['RABBITMQ_PASSWD'])
        connection = pika.BlockingConnection(
        pika.ConnectionParameters(app.config['RABBITMQ_IP'], app.config['RABBITMQ_PORT'], app.config['RABBITMQ_VHOST'], credentials))
        channel = connection.channel()
        channel.queue_declare(queue=self.host_id.host_id)
        channel.basic_publish(exchange='', routing_key=self.host_id.host_id,body=msg)
        connection.close()