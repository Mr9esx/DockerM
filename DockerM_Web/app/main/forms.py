# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,BooleanField
from wtforms.validators import DataRequired


class RabbitForm(FlaskForm):
	RABBIT_HOST = StringField(validators=[DataRequired(u'请输入 RabbitMQ 主机地址！')])
	RABBIT_HOST_USERNAME= StringField(validators=[DataRequired(u'请输入 RabbitMQ 用户名！')])
	RABBIT_HOST_PASSWORD = PasswordField(validators=[DataRequired(u'请输入 RabbitMQ 密码！')])
	register = SubmitField(u'保存')