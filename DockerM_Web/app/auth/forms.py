# -*- coding:utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, Email, Regexp, EqualTo


class LoginForm(FlaskForm):
    username = StringField(validators=[DataRequired(u'请输入用户名!')])
    password = PasswordField(validators=[DataRequired(u'请输入密码!')])
    login = SubmitField(u'登陆')


class RegisterForm(FlaskForm):
    username = StringField(validators=[DataRequired(u'请输入用户名！'),Length(6, 24, u'用户名长度必须在 6-24 之间!')])
    password = PasswordField(validators=[DataRequired(u'请输入密码！'),
        Length(6, 24, u'密码长度必须在 6-24 之间!'),
        Regexp(r'^[a-zA-Z0-9_][a-zA-Z0-9_]*$', 0, u'密码只能包含字母数字下划线!')])
    email = StringField(validators=[DataRequired(u'请填写此字段'),
        Length(min=6, max=64, message=u'邮箱地址长度必须在 6-64 之间!'),
        Email(u'邮箱地址格式有误!')])
    register = SubmitField(u'注册')
