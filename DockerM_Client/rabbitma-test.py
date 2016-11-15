#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pika

credentials = pika.PlainCredentials(Config.RABBIT_USER, Config.RABBIT_PASSWD)
connection = pika.BlockingConnection(pika.ConnectionParameters(Config.RABBIT_HOST,Config.RABBIT_PORT,Config.RABBIT_VHOST,credentials))
channel = connection.channel()

channel.queue_declare(queue='hello')

count = 0

while True:
    channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
    count += 1
    print count
    if count == 6000:
        connection.close()
        exit()

