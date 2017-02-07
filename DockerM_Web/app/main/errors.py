# -*- coding: utf-8 -*-
from flask import render_template
from . import dockerm


# app_errorhandler可以catch住所有abort(404)以及找不到对应router的处理请求
# 在蓝图中写错误处理的不同之处是，如果使用了errorhandler装饰器，则只会调用在蓝图中引起的错误处理。而应用程序范围内的错误处理则必须使用app_errorhandler。
@dockerm.app_errorhandler(404)
def page_not_found():
    return render_template('errorPage/404.html'), 404


@dockerm.app_errorhandler(500)
def internal_server_error():
    return render_template('errorPage/500.html'), 500
