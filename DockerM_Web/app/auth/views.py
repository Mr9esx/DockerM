# -*- coding:utf-8 -*-
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, g, request
from flask_login import login_user, logout_user, current_user, login_required
from . import dockermAuth
from .. import lm
from .forms import LoginForm, RegisterForm
from ..lib.dbModel import User
from ..lib.dbController import checkUserIsRegister, checkEmailIsRegister, createUser
from werkzeug.security import check_password_hash


@dockermAuth.before_request
def before_request():
    g.user = current_user


@lm.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user


@dockermAuth.route('/login', methods=['GET', 'POST'])
def login():
    # 已登陆
    print current_user
    if g.user is not None and g.user.is_authenticated:
        session['_fresh'] = False
        return redirect(url_for('dockerm.index'))
    if g.user.is_active is True:
        print('active is True')
    else:
        pass
        # 提示尚未登陆
        # flash('no_login')
    loginform = LoginForm()
    registerform = RegisterForm()
    if loginform.validate_on_submit():
        user = User.query.filter_by(username=loginform.username.data).first()
        if ((user is not None) and check_password_hash(user.password,
                                                       loginform.password.data)):
            # remember=loginform.remember_me.data
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for('dockerm.index'))
        else:
            flash('login_failed')
    return render_template('login.html',
                           loginform=loginform,
                           registerform=registerform,
                           username=session.get('username'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())


@dockermAuth.route('/logout', methods=['GET'])
@login_required
def login_out():
    logout_user()
    flash('logout')
    return redirect(url_for('dockermAuth.login'))


@dockermAuth.route('/register', methods=['POST'])
def register():
    registerform = RegisterForm()
    cuir = checkUserIsRegister(username=registerform.username.data)
    ceir = checkEmailIsRegister(registerform.email.data)
    if (cuir and ceir) and (((registerform.password.validate('Length') and registerform.username.validate(
            'Length')) and (registerform.password.validate('Regexp') and registerform.email.validate('Email')))):
        if createUser(registerform.username.data, password=registerform.password.data, email=registerform.email.data,
                      level=1):
            flash('register_succeed', u'请登录！')
            return redirect((url_for('dockermAuth.login')))
        else:
            flash('error', u'未知错误!请联系管理员!')
            return redirect((url_for('dockermAuth.login', _anchor='signup')))
    else:
        msg = registerform.errors
        if len(msg) > 0:
            flash('register_failed', msg[msg.keys()[0]][0])
        elif not cuir:
            flash('register_failed', u'账号已存在！')
        elif not ceir:
            flash('register_failed', u'邮箱已存在！')
        return redirect((url_for('dockermAuth.login', _anchor='signup')))
