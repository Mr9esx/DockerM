# -*- coding:utf-8 -*-
# Flask-SQLAlchemy 操作数据库
from .. import db
from werkzeug.security import generate_password_hash
import time


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(128),unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128),primary_key=True)
    level = db.Column(db.Integer)
    confirmed = db.Column(db.Integer)

    # 构造函数
    def __init__(self,username,password,email,level):
        self.username = username
        self.password = password
        self.email = email
        self.level = level
        self.confirmed = 1

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


class Containers(db.Model):
    __tablename__ = 'containers'
    container_id = db.Column(db.String(64),primary_key=True)
    container_name = db.Column(db.String(64))
    image_id = db.Column(db.String(64))
    saltstack_id = db.Column(db.String(64), db.ForeignKey('hosts.saltstack_id'))
    created_at = db.Column(db.DateTime)
    status = db.Column(db.String(64))
    info = db.Column(db.Text)

    # 构造函数
    def __init__(self, container_id, container_name, saltstack_id, created_at, status, info):
        self.container_id = container_id
        self.container_name = container_name
        self.saltstack_id = saltstack_id
        self.created_at = created_at
        self.status = status
        self.info = info

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


class Hosts(db.Model):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    saltstack_id = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(64))
    host_info = db.Column(db.Text)
    image_list = db.relationship('Images', backref='hosts', lazy='dynamic')
    container_list = db.relationship('Containers', backref='hosts', lazy='dynamic')

    # 构造函数
    def __init__(self,saltstack_id,created_at,created_by,host_info):
        self.saltstack_id = saltstack_id
        self.created_at = created_at
        self.created_by = created_by
        self.host_info = host_info

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


class Images(db.Model):
    __tablename__ = 'images'
    image_id = db.Column(db.String(64), primary_key=True)
    image_name = db.Column(db.Text)
    saltstack_id = db.Column(db.String(64), db.ForeignKey('hosts.saltstack_id'))
    created_at = db.Column(db.DateTime)
    info = db.Column(db.Text)
    history = db.Column(db.Text)

    def __init__(self, image_id, image_name, saltstack_id, created_at, info, history):
        self.image_id = image_id
        self.image_name = image_name
        self.saltstack_id = saltstack_id
        self.created_at = created_at
        self.info = info
        self.history = history

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


class Container_Status(db.Model):
    __tablename__ = 'container_status'
    id = db.Column(db.Integer,primary_key=True)
    container_id = db.Column(db.String(64))
    cpu_percent = db.Column(db.Float)
    memory_usage = db.Column(db.String(64))
    memory_limit = db.Column(db.String(64))
    memory_percent = db.Column(db.Float)
    tx_packets = db.Column(db.String(64))
    tx_bytes = db.Column(db.String(64))
    tx_dropped = db.Column(db.String(64))
    tx_errors = db.Column(db.String(64))
    tx_speed = db.Column(db.String(64))
    rx_packets = db.Column(db.String(64))
    rx_bytes = db.Column(db.String(64))
    rx_dropped = db.Column(db.String(64))
    rx_errors = db.Column(db.String(64))
    rx_speed = db.Column(db.String(64))
    collect_time = db.Column(db.String(64))

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


class Operation_Log(db.Model):
    __tablename__ = 'operation_log'
    id = db.Column(db.Integer,primary_key=True)
    operation_time = db.Column(db.DateTime)
    operation_type = db.Column(db.String(128))
    operation_id = db.Column(db.String(128))
    operation_user = db.Column(db.String(128))
    operation_result = db.Column(db.String(128))
    host_id = db.Column(db.String(128))
