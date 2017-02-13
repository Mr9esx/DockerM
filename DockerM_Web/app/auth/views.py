# -*- coding:utf-8 -*-
from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, g, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from . import dockermAuth
from .. import db
from .forms import LoginForm, RegisterForm
from ..lib.dbModel import User
from ..lib.sendemail import send_email


# before_request在当前蓝本，before_app_request在全局
@dockermAuth.before_app_request
def before_request():
    if current_user.is_authenticated and current_app._get_current_object().config['CONFIRMED']:
        if not current_user.confirmed \
                and request.endpoint \
                and request.endpoint[:12] != 'dockermAuth.' \
                and request.endpoint != 'static':
            return redirect(url_for('dockermAuth.unconfirmed'))


@dockermAuth.route('/confirm/<token>', methods=['GET', 'POST'])
@login_required
def confirm(token):
    if not current_app._get_current_object().config['CONFIRMED']:
        return redirect(url_for('dockerm.index'))
    if current_user.confirmed:
        return redirect(url_for('dockerm.index'))
    if current_user.confirm(token):
        flash(u'确认成功！', 'success')
        return redirect(url_for('dockerm.index'))
    else:
        flash(u'链接无效或过期！', 'error')
        return redirect(url_for('dockermAuth.unconfirmed'))


@dockermAuth.route('/unconfirmed', methods=['GET'])
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('dockermAuth.login'))
    if not current_app._get_current_object().config['CONFIRMED']:
        return redirect(url_for('dockerm.index'))
    return render_template('auth/unconfirmed.html', username=current_user.username)


@dockermAuth.route('/resendfirmed', methods=['GET'])
@login_required
def resendconfirmed():
    if not current_app._get_current_object().config['CONFIRMED']:
        return redirect(url_for('dockerm.index'))
    if not current_user.confirmed:
        token = current_user.generate_confirmation_token()
        send_email(current_user.email, 'mail/confirm_temp', user=current_user.username, token=token)
        flash(u'已重新发送一封认证邮件到您的邮箱！', 'success')
        return redirect(url_for('dockermAuth.unconfirmed'))
    return redirect(url_for('dockerm.index'))


@dockermAuth.route('/login', methods=['GET', 'POST'])
def login():
    # 已登陆
    if current_user is not None and current_user.is_authenticated:
        session['_fresh'] = False
        return redirect(url_for('dockerm.index'))
    loginform = LoginForm()
    registerform = RegisterForm()
    if loginform.validate_on_submit():
        username = loginform.username.data
        if '@' in username:
            user = User.query.filter_by(email=username).first()
        else:
            user = User.query.filter_by(username=username).first()
        if (user is not None) and user.verify_password(loginform.password.data):
            # remember=loginform.remember_me.data
            login_user(user, remember=True)
            return redirect(request.args.get("next") or url_for('dockerm.index'))
        else:
            flash(u'用户名或者密码错误！', 'error')
    return render_template('auth/login.html',
                           loginform=loginform,
                           registerform=registerform,
                           username=session.get('username'),
                           known=session.get('known', False),
                           current_time=datetime.utcnow())


@dockermAuth.route('/register', methods=['POST'])
def register():
    registerform = RegisterForm()
    if registerform.validate_on_submit():
        app = current_app._get_current_object()
        user = User(username=registerform.username.data, hash_password=registerform.password.data,
                    email=registerform.email.data, confirmed=(not current_app._get_current_object().config['CONFIRMED']))
        db.session.add(user)
        db.session.commit()
        if app.config['CONFIRMED']:
            token = user.generate_confirmation_token()
            send_email(registerform.email.data, 'mail/confirm_temp', user=user, token=token)
        flash(u'注册成功！', 'success')
        return redirect((url_for('dockermAuth.login', _anchor='login')))
    else:
        for error in registerform.errors:
            for info in registerform.errors[error]:
                flash(unicode(info), 'error')
        return redirect((url_for('dockermAuth.login', _anchor='signup')))


@dockermAuth.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash(u'注销成功！', 'success')
    return redirect(url_for('dockermAuth.login'))
