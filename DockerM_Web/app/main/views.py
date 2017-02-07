# -*- coding:utf-8 -*-
from flask import render_template, session, redirect, url_for, make_response, g, request, current_app
from flask_login import login_required
from ..lib.dbModel import *
from . import dockerm
import salt.client
import json
import simplejson

from ..lib.dbModel import Hosts
from ..lib.dbController import getUser, getAllContainerAndPaginate, getAllHost, HostisExited, getAllContainer2HostAndPaginate, getAllHostAndPaginate, getAllContainer, getAllImage, getContainerByStatus, getContainerInfo, getAllImageAndPaginate



@dockerm.route('/', methods=['GET'])
@login_required
def index():
    # 未来是关注列表
    user = getUser(session['user_id'])
    client = salt.client.LocalClient()
    ret = client.cmd('*', 'grains.items')
    ping = client.cmd('*', 'test.ping')

    return render_template('index.html',
                           allHost=len(getAllHost()),
                           allContainer=len(getAllContainer()),
                           allImage=len(getAllImage()),
                           runningContainer=len(getContainerByStatus('running')),
                           username=user.username,
                           ret=json.dumps(ret, indent=4),
                           ping=ping)


@dockerm.route('/hosts/', methods=['GET'])
@login_required
def hostsPage():
    user = getUser(session['user_id'])
    host_list = []
    all_hosts = getAllHostAndPaginate(request.args.get('page'))

    for host_info in all_hosts.items:
        host_list.append({'saltstack_id': host_info.saltstack_id, 'created_at': host_info.created_at, 'created_by': host_info.created_by, 'host_info': simplejson.loads(host_info.host_info)})

    return render_template('hosts.html',
                           pagination=all_hosts,
                           username=user.username,
                           host_list=host_list)


@dockerm.route('/containers/<saltstack_id>', methods=['GET'])
@login_required
def containersPage(saltstack_id):

    user = getUser(session['user_id'])
    container_list = []

    if saltstack_id == 'all':
        all_container = getAllContainerAndPaginate(request.args.get('page'))
        all_host = getAllHost()

        for tmp in all_container.items:
            container_list.append(
                {'container_name': tmp.container_name, 'container_id': tmp.container_id, 'status': tmp.status,
                 'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at, 'json_info': simplejson.loads(tmp.info)})

        return render_template('containers.html',
                               pagination=all_container,
                               username=user.username,
                               is_all=True,
                               container_list=container_list,
                               host_list=all_host,)

    else:

        if HostisExited(saltstack_id):
            all_container = getAllContainer2HostAndPaginate(saltstack_id,request.args.get('page'))
            all_host = getAllHost()

            for tmp in all_container.items:
                container_list.append(
                    {'container_name': tmp.container_name, 'container_id': tmp.container_id, 'status': tmp.status,
                     'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at,
                     'json_info': simplejson.loads(tmp.info)})

            return render_template('containers.html',
                                   pagination=all_container,
                                   username=user.username,
                                   is_all=False,
                                   container_list=container_list,
                                   host_list=all_host,
                                   saltstack_id=saltstack_id)

        else:
            return render_template('errorPage/404.html'), 404


@dockerm.route('/images/<saltstack_id>', methods=['GET'])
@login_required
def imagesPage(saltstack_id):

    user = getUser(session['user_id'])
    image_list = []

    if saltstack_id == 'all':
        all_image = getAllImageAndPaginate(request.args.get('page'))
        all_host = getAllHost()

        for tmp in all_image.items:
            image_list.append(
                {'image_name': tmp.image_name, 'image_id': tmp.image_id,
                 'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at, 'json_info': simplejson.loads(tmp.info)})

        return render_template('images.html',
                               pagination=all_image,
                               username=user.username,
                               is_all=True,
                               image_list=image_list,
                               host_list=all_host)

    else:

        if HostisExited(saltstack_id):
            all_containers = getAllImageAndPaginate(saltstack_id,request.args.get('page'))
            all_host = getAllHost()

            for tmp in all_containers.items:
                container_list.append(
                    {'image_name': tmp.image_name, 'image_id': tmp.image_id,
                     'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at,
                     'json_info': simplejson.loads(tmp.info)})

            return render_template('json_info.html',
                                   pagination=all_containers,
                                   username=user.username,
                                   is_all=False,
                                   container_list=container_list,
                                   host_list=all_host,
                                   saltstack_id=saltstack_id)

        else:
            return render_template('errorPage/404.html'), 404


@dockerm.route('/container/info/<container_id>', methods=['GET'])
@login_required
def containerInfoPage(container_id):
    info = getContainerInfo(container_id)
    print info.container_name
    print simplejson.loads(info.info)
    return render_template('info/container_info_view.html', container_id=container_id, container_name=info.container_name, info=simplejson.loads(info.info))