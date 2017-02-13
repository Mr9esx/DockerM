# -*- coding:utf-8 -*-
# Flask-SQLAlchemy 操作数据库
from .. import db, lm
from flask import current_app
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer
from sqlalchemy import desc


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


@lm.user_loader
def load_user(uid):
    user = User.query.filter_by(id=uid).first()
    return user


class Containers(db.Model):
    __tablename__ = 'containers'
    container_id = db.Column(db.String(64), primary_key=True)
    container_name = db.Column(db.String(64))
    image_id = db.Column(db.String(64))
    saltstack_id = db.Column(db.String(64), db.ForeignKey('hosts.saltstack_id'))
    created_at = db.Column(db.DateTime)
    status = db.Column(db.String(64))
    info = db.Column(db.Text)

    @classmethod
    def get_all_container(cls):
        """
        @:return:返回含有全部主机的全部容器信息的List，并按时间降序排序
        @:rtype:list
        """
        return cls.query.order_by(desc('created_at')).all()

    @classmethod
    def get_all_container_by_pagination(cls, page):
        """
        @:return:使用分页的形式返回含有全部主机的全部容器信息，并按时间降序排序
        @:rtype:flask_sqlalchemy.Pagination
        @:note:记得加 .items 才能获取或者遍历数据
        """
        # if page is None or int(page) <= 0:
        #     page = 1
        # else:
        #     try:
        #         page = int(page)
        #     except:
        #         page = 1
        result = cls.query.order_by(desc('created_at')).paginate(page, current_app._get_current_object().config['PER_PAGE'], error_out=True)
        return result

    @classmethod
    def get_container_according_to_host(cls, saltstack_id):
        """
        @:return:返回含有指定主机的全部容器信息的List，并按时间降序排序
        @:rtype:list
        @:param host_id:主机 id
        """
        return cls.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).all()

    @classmethod
    def get_container_according_to_host_with_pagination(cls, saltstack_id, page):
        """
        @:return:使用分页的形式返回含有指定主机的全部容器信息的List，并按时间降序排序
        @:rtype:flask_sqlalchemy.Pagination
        @:param host_id:主机 id
        @:param page:页数
        """
        # if page is None or int(page) <= 0:
        #     page = 1
        # else:
        #     try:
        #         page = int(page)
        #     except:
        #         page = 1
        result = cls.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).paginate(page, current_app._get_current_object().config['PER_PAGE'],
                                                                                                      error_out=True)
        return result

    @classmethod
    def get_container_according_to_status(cls, status):
        """
        @:return:返回含有全部主机的指定容器状态信息的List，并按时间降序排序
        @:rtype:list
        @:param status:主机 id
        """
        return cls.query.order_by(desc('created_at')).filter_by(status=status).all()

    @classmethod
    def get_container_according_to_status_with_paginate(cls, status, page):
        """
        @:return:使用分页的形式返回含有全部主机的指定容器状态信息的List，并按时间降序排序
        @:rtype:flask_sqlalchemy.Pagination
        @:param status:主机 id
        @:param page:页数
        """
        return cls.query.order_by(desc('created_at')).filter_by(status=status).all().paginate(page, current_app._get_current_object().config['PER_PAGE'], error_out=True)

    @classmethod
    def get_container_info_according_to_container_id(cls, container_id):
        """
        @:return:获取指定容器的全部信息
        @:rtype:app.lib.dbModel.Containers
        @:param container_id:容器 id
        """
        return cls.query.filter_by(container_id=container_id).first()

    @classmethod
    def update_container_follow_state(cls, container_id, state):
        if state is 0 or state is 1:
            container = cls.query.filter_by(container_id=container_id).first()
            container.follow = state
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def get_host_info_according_to_container_id(cls, container_id):
        """
        @:return:获取指定容器 ID 的主机信息
        @:rtype:app.lib.dbModel.Container
        @:param container_id:容器 ID
        """
        return cls.query.filter_by(container_id=container_id).first()

    @classmethod
    def container_is_exited(cls, container_id):
        """
        @:return:传入主机ID，并从数据库中查询，不存在返回False。
        @:rtype:bool
        @:param host_id:主机 ID
        """
        if cls.query.filter_by(container_id=container_id).first() is None:
            return False
        else:
            return True


class Hosts(db.Model):
    __tablename__ = 'hosts'
    id = db.Column(db.Integer, primary_key=True)
    saltstack_id = db.Column(db.String(64), unique=True)
    created_at = db.Column(db.DateTime)
    created_by = db.Column(db.String(64))
    host_info = db.Column(db.Text)
    image_list = db.relationship('Images', backref='hosts', lazy='dynamic')
    container_list = db.relationship('Containers', backref='hosts', lazy='dynamic')

    @classmethod
    def get_all_host(cls):
        """
        @:return:返回含有全部主机信息的List，并按时间降序排序。如
        @:rtype:list
        """
        return cls.query.order_by(desc('created_at')).all()

    @classmethod
    def get_all_host_by_paginate(cls, page):
        """
        @:return:使用分页的形式返回含有全部主机信息的List，并按时间降序排序
        @:rtype:list
        @:param page:页数
        """
        return cls.query.order_by(desc('created_at')).paginate(page,
                                                               current_app._get_current_object().config['PER_PAGE'],
                                                               False)

    @classmethod
    def get_host_info_according_to_saltstack_id(cls, saltstack_id):
        """
        @:return:获取指定主机的信息
        @:rtype:app.lib.dbModel.Hosts
        @:param host_id:主机 ID
        """
        return cls.query.filter_by(saltstack_id=saltstack_id).first()

    @classmethod
    def host_is_exited(cls, saltstack_id):
        """
        @:return:传入主机ID，并从数据库中查询，不存在返回False。
        @:rtype:bool
        @:param host_id:主机 ID
        """
        if cls.query.filter_by(saltstack_id=saltstack_id).first() is None:
            return False
        else:
            return True


class Images(db.Model):
    __tablename__ = 'images'
    image_id = db.Column(db.String(64), primary_key=True)
    image_name = db.Column(db.Text)
    saltstack_id = db.Column(db.String(64), db.ForeignKey('hosts.saltstack_id'))
    created_at = db.Column(db.DateTime)
    info = db.Column(db.Text)
    history = db.Column(db.Text)

    @classmethod
    def get_all_image(cls):
        """
        @:return:返回含有全部主机的全部镜像信息的List，并按时间降序排序
        @:rtype:list
        """
        return cls.query.order_by(desc('created_at')).all()

    @classmethod
    def get_all_image_by_paginate(cls, page):
        """
        @:return:使用分页的形式返回含有全部主机的全部镜像信息，并按时间降序排序
        @:rtype:flask_sqlalchemy.Pagination
        @:note:记得加 .items 才能获取或者遍历数据
        """
        return cls.query.order_by(desc('created_at')).paginate(page, current_app._get_current_object().config['PER_PAGE'], error_out=True)

    @classmethod
    def get_image_according_to_host(cls, saltstack_id):
        """
        @:return:返回含有指定主机的全部镜像信息的List，并按时间降序排序
        @:rtype:list
        @:param host_id:主机 id
        """
        return cls.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).all()

    @classmethod
    def get_image_according_to_host_with_paginate(cls, saltstack_id, page):
        """
        @:return:使用分页的形式返回含有指定主机的全部镜像信息的List，并按时间降序排序
        @:rtype:flask_sqlalchemy.Pagination
        @:param host_id:主机 id
        @:param page:页数
        """
        return cls.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).paginate(page, current_app._get_current_object().config['PER_PAGE'],
                                                                                                    error_out=True)

    @classmethod
    def get_image_info_according_to_image_id(cls, image_id):
        """
        @:return:获取指定镜像的全部信息
        @:rtype:app.lib.dbModel.Images
        @:param image_id:镜像 ID
        """
        return cls.query.filter_by(image_id=image_id).first()

    @classmethod
    def image_is_exited(cls, image_id):
        """
        @:return:传入主机ID，并从数据库中查询，不存在返回False。
        @:rtype:bool
        @:param host_id:主机 ID
        """
        if cls.query.filter_by(image_id=image_id).first() is None:
            return False
        else:
            return True


class ContainerStatus(db.Model):
    __tablename__ = 'container_status'
    id = db.Column(db.Integer, primary_key=True)
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

    @classmethod
    def get_container_status(cls, container_id):
        """
        @:return:Api 接口，获取指定容器监控信息。(目前没用)
        @:rtype:list
        @:param container_id:容器 ID
        """
        if Containers.containeri_exited(container_id):
            tmp = cls.query.filter_by(container_id=container_id).limit(60).all()
            json = []
            [json.append(data.to_dict()) for data in tmp]
            return json
        else:
            pass


class OperationLog(db.Model):
    __tablename__ = 'operation_log'
    id = db.Column(db.Integer, primary_key=True)
    operation_time = db.Column(db.DateTime)
    operation_type = db.Column(db.String(128))
    operation_id = db.Column(db.String(128))
    operation_user = db.Column(db.String(128))
    operation_result = db.Column(db.String(128))
    host_id = db.Column(db.String(128))
