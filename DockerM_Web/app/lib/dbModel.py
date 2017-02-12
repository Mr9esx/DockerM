# -*- coding:utf-8 -*-
# Flask-SQLAlchemy 操作数据库
from .. import db, lm
from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128), unique=True)
    confirmed = db.Column(db.Boolean, default=False)
    token_created_at = db.Column(db.DateTime)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    @property
    def hash_password(self):
        raise AttributeError(u'密码不可读！')

    @hash_password.setter
    def hash_password(self, password):
        self.password = generate_password_hash(password)

    def generate_confirmation_token(self, expiration=1800):
        """
        :param expiration: 超时时间，默认3600秒。
        :return: 令牌
        """
        sersializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'], expiration)
        self.token_created_at = datetime.now()
        db.session.add(self)
        return sersializer.dumps({'confirm': self.id})

    def confirm(self, token):
        sersializer = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            data = sersializer.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            print "no"
            return False
        print "ok"
        self.confirmed = True
        db.session.add(self)
        return True

    def verify_password(self, form_data_password):
        """
        :param form_data_password: 表单传入的密码
        :return: 布尔值
        """
        return check_password_hash(self.password, form_data_password)

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


@lm.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user


class Containers(db.Model):
    __tablename__ = 'containers'
    container_id = db.Column(db.String(64),primary_key=True)
    container_name = db.Column(db.String(64))
    image_id = db.Column(db.String(64))
    saltstack_id = db.Column(db.String(64), db.ForeignKey('hosts.saltstack_id'))
    created_at = db.Column(db.DateTime)
    status = db.Column(db.String(64))
    info = db.Column(db.Text)

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