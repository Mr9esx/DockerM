# -*- coding:utf-8 -*-

import time
from datetime import datetime
from flask import  session, redirect, url_for,jsonify,g,request
from flask_login import login_required
import salt.client
import re
import simplejson

from . import dockermApi
from ..lib.rawSQL import rawSQLControl
from .. import db
from ..lib.dbModel import Hosts, Images, Containers
from ..lib.dbController import getUser, getAllImage2Host, getAllHost, getAllContainer2Host, getHostInfoByContainerID, HostisExited
from ..lib.pushMsg import pushMsg
from ..lib.tools import createContainer


@dockermApi.route('/api/container/getstatus/<container_id>', methods=['GET'])
@login_required
def getStatus(container_id):
    return jsonify(rawSQLControl().getContainerState(container_id,60))

@dockermApi.route('/api/container/getstatus_now/<container_id>', methods=['GET'])
@login_required
def getStatusNow(container_id):
    return jsonify(rawSQLControl().getContainerState(container_id, 1))


@dockermApi.route('/api/get/hosts/', methods=['GET'])
@login_required
def getHostList():
    req_list = []
    id = 0
    for host_info in getAllHost():
        info = simplejson.loads(host_info.host_info)
        req_list.append({
            "id": host_info.saltstack_id,
            "text": host_info.saltstack_id,
            "osarch": info[host_info.saltstack_id]['osarch'],
            "lsb_distrib_description": info[host_info.saltstack_id]['lsb_distrib_description'],
            "docker_version": info[host_info.saltstack_id]['docker_version'],
            "docker_apiversion": info[host_info.saltstack_id]['docker_apiversion']
        })
    return jsonify(req_list)


@dockermApi.route('/api/get/images/<saltstack_id>', methods=['GET'])
@login_required
def getAllImageList(saltstack_id):
    req_list = []
    for image_info in getAllImage2Host(saltstack_id):
        info = simplejson.loads(image_info.info)
        req_list.append({
            "id": info['Id'][7:],
            "text": simplejson.loads(image_info.image_name)[0],
            "size": info['Size']
        })
    return jsonify(req_list)


@dockermApi.route('/api/get/containers/<saltstack_id>', methods=['GET'])
@login_required
def getAllContainerList(saltstack_id):
    req_list = []
    for container_info in getAllContainer2Host(saltstack_id):
        req_list.append({
            "id": container_info.container_id[0:12],
            "text": container_info.container_name,
            "status": container_info.status
        })
    return jsonify(req_list)


@dockermApi.route('/control/container/<control_type>', methods=['POST'])
@login_required
def containerControl(control_type):
    print control_type
    user = getUser(session['user_id'])
    if control_type == 'start':
        saltstack_id = getHostInfoByContainerID(request.form['container_id']).saltstack_id
        if (checkHost(saltstack_id)):
            pushMsg(control_type, user.username, {"container_id": request.form['container_id']}, getHostInfoByContainerID(request.form['container_id']).saltstack_id).push()
            return jsonify({'status': 'success', 'title': '操作发送成功！',
                            'text': u'启动容器 ' + request.form['container_name'] + ' [' + request.form['container_id'][
                                                                                       0:12] + u'] 成功！',})
        else:
            return jsonify({'status': 'error', 'title': '操作发送失败！', 'text': u'失败！' + saltstack_id + u' 主机无法访问！'})
    elif control_type == 'stop':
        saltstack_id = getHostInfoByContainerID(request.form['container_id']).saltstack_id
        print saltstack_id
        if (checkHost(saltstack_id)):
            pushMsg(control_type, user.username, {"container_id": request.form['container_id']}, getHostInfoByContainerID(request.form['container_id']).saltstack_id).push()
            return jsonify({'status': 'success', 'title': '操作发送成功！',
                            'text': u'关闭容器 ' + request.form['container_name'] + ' [' + request.form['container_id'][
                                                                                       0:12] + u'] 成功！',})
        else:
            return jsonify({'status': 'error', 'title': '操作发送失败！', 'text': u'失败！' + saltstack_id + u' 主机无法访问！'})
    elif control_type == 'follow':
        updateContainerFollowState(request.form['container_id'],1)
    elif control_type == 'unfollow':
        print 'unfollow'
        updateContainerFollowState(request.form['container_id'], 0)
    elif control_type == 'create':
        saltstack_id = request.form['saltstack_id']
        if (checkHost(saltstack_id)):
            image_id = request.form['image_id']

            for link in request.form.getlist("link[]"):
                link_dict = simplejson.loads(link)
                if Containers.query.filter_by(container_name=link_dict.keys()[0]).first() is None:
                    return jsonify({'status': 'error', 'title': '操作失败！', 'text': u'失败！所链接的容器不存在！'})

            for port in request.form.getlist("port[]"):
                port_dict = simplejson.loads(port)
                try:
                    int(port_dict['container-port'])
                    int(port_dict['host-port'])
                except ValueError:
                    return jsonify({'status': 'error', 'title': '操作失败！', 'text': u'失败！端口只能是数字！'})
                if not re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$').match('55.258.365.12'):
                    return jsonify({'status': 'error', 'title': '操作失败！', 'text': u'失败！IP 地址不规范！'})

            if Images.query.filter_by(image_id=image_id).first() is None:
                return jsonify({'status': 'error', 'title': '操作失败！', 'text': u'失败！无此镜像！'})

            pushMsg('create', user.username,
                    {"container_name": request.form['container_name'], "saltstack_id": saltstack_id,
                     "image": image_id, "hostname": request.form['hostname'],
                     "command": request.form["command"].replace(',', ' && '), "link": request.form.getlist("link[]"),
                     "port": request.form.getlist("port[]")},
                    request.form['saltstack_id'].encode('utf-8')).push()

            return jsonify({'status': 'success', 'title': '操作发送成功！', 'text': u'成功！容器已创建！'})
        else:
            return jsonify({'status': 'error', 'title': '操作发送失败！', 'text': u'失败！' + saltstack_id + u' 主机无法访问！'})
    return '0'


@dockermApi.route('/api/hostIsAlive/', methods=['POST'])
@login_required
def hostIsAlive():
    return jsonify({"saltstack_id": request.form['saltstack_id'],"status": checkHost(request.form['saltstack_id'])})


def checkHost(saltstack_id):
    client = salt.client.LocalClient()
    try:
        ping = client.cmd(saltstack_id, 'test.ping',timeout=3)
        print ping
    except SaltClientError:
        return False
    if (ping.has_key(saltstack_id) and ping[saltstack_id] == True and HostisExited(saltstack_id)):
        print saltstack_id
        return True
    else:
        return False


@dockermApi.route('/api/createHost/', methods=['POST'])
@login_required
def createHost():
    #检查saltstack_id是否已存在数据库中
    if (not Hosts.query.filter_by(saltstack_id=request.form['saltstack_id']).first()):
        # 运行 test.ping 检查是否连通
        client = salt.client.LocalClient()
        ping = client.cmd(request.form['saltstack_id'], 'test.ping')
        if (ping.has_key(request.form['saltstack_id']) and ping[request.form['saltstack_id']] == True):
            if (client.cmd(request.form['saltstack_id'], 'cp.get_dir', ['salt://dockerm-minion', '/srv'])[
                    request.form['saltstack_id']] == []):
                return jsonify({'status': '103', 'msg': u'失败！'+request.form['saltstack_id']+u' 主机文件复制错误！'}) #已存在数据库中 #文件复制失败
            db.session.add(Hosts(request.form['saltstack_id'], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), getUser(session['user_id']).username, json.dumps(client.cmd(request.form['saltstack_id'], 'grains.items'))))
            db.session.commit()
            return jsonify({'status': '100', 'msg': u'成功！'+request.form['saltstack_id']+u' 主机已成功添加！'})
        else:
            return jsonify({'status': '102', 'msg': u'失败！'+request.form['saltstack_id']+u' 主机无法访问！'}) #主机无法连通
    else:
        return jsonify({'status': '101', 'msg': u'失败！'+request.form['saltstack_id']+u' 主机已存在！'}) #已存在数据库中



