# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from lib.jinja2models import *

from config import config

db = SQLAlchemy()
lm = LoginManager()
lm.session_protection = 'strong'
lm.login_view = 'dockermAuth.login'

# 函数工厂，批量注册
def create_app(config_name):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'This is DockerM'
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # 数据库链接设置
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    db.init_app(app)
    lm.init_app(app)

    #注册自定义函数init_app
    env = app.jinja_env
    env.filters['validataipaddress'] = validataipaddress
    env.filters['cutStr'] = cutStr
    env.filters['imageSize'] = imageSize
    env.filters['stopRunTime'] = stopRunTime
    env.filters['nowRunTime'] = nowRunTime
    env.filters['formatPortsJson'] = formatPortsJson
    env.filters['formatNetwrokJson'] = formatNetwrokJson
    env.filters['showJsonPage'] = showJsonPage
    env.filters['getImageName'] = getImageName
    env.filters['getImageVer'] = getImageVer
    env.filters['strptime2time'] = strptime2time

    # 注册蓝图
    from .auth import dockermAuth as dockermAuth
    from .main import dockerm as dockerm
    from .api import dockermApi as dockermApi
    app.register_blueprint(dockermAuth)
    app.register_blueprint(dockerm)
    app.register_blueprint(dockermApi)
    return app