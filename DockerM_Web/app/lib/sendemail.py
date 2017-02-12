# -*- coding:utf-8 -*-
from threading import Thread
from flask_mail import Message
from flask import current_app, render_template
from .. import mail


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


def send_email(to, temp, **kwargs):
    app = current_app._get_current_object()
    msg = Message('DockerM : 确认您的账号。', sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(temp + '.txt', **kwargs)
    msg.html = render_template(temp + '.html', **kwargs)
    sendthread = Thread(target=send_async_email, args=[app, msg])
    sendthread.start()
    return sendthread
