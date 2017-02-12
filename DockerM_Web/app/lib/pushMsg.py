# -*- coding:utf-8 -*-
import pika,json
from flask import current_app


class pushMsg(object):

    def __init__(self, control_type, username, body, saltstack_id):
        self.body = body
        self.control_type = control_type
        self.username = username
        self.saltstack_id = saltstack_id

    def push(self):
        # 获取上下文，读取配置
        app = current_app._get_current_object()
        print self.body
        msg = json.dumps({'control_type': self.control_type, 'username' : self.username , 'body': self.body})
        credentials = pika.PlainCredentials(app.config['RABBITMQ_USER'], app.config['RABBITMQ_PASSWD'])
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(app.config['RABBITMQ_IP'], app.config['RABBITMQ_PORT'],
                                      app.config['RABBITMQ_VHOST'], credentials))
        channel = connection.channel()
        channel.queue_declare(queue=self.saltstack_id)
        channel.basic_publish(exchange='', routing_key=self.saltstack_id,body=msg)
        connection.close()