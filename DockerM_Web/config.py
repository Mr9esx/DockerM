# -*- coding: utf-8 -*-
import os

# basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'This is DockerM'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Rabbit MQ设置
    RABBITMQ_IP = '127.0.0.1'
    RABBITMQ_PORT = 5672
    RABBITMQ_VHOST = 'dockerm_vhost'
    RABBITMQ_USER = 'dockerm'
    RABBITMQ_PASSWD = '123456'

    # 是否启用邮箱认证
    CONFIRMED = True

    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SENDER = '1138099359@qq.com'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:asdasd@127.0.0.1/dockerm"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:asdasd@127.0.0.1/dockerm"


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:asdasd@127.0.0.1/dockerm"


#配置字典
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
