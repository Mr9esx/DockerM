# -*- coding:utf-8 -*-
from flask import render_template, session, redirect, url_for, make_response, g, request
from flask_login import login_required, current_user
import salt.client
import json
import simplejson

from . import dockerm
from ..lib.dbModel import *


@dockerm.route('/', methods=['GET'])
@login_required
def index():
    # 未来是关注列表
    client = salt.client.LocalClient()
    ret = client.cmd('*', 'grains.items')
    ping = client.cmd('*', 'test.ping')
    return render_template('index.html',
                           allHost=len(Hosts.get_all_host()),
                           allContainer=len(Containers.get_all_container()),
                           allImage=len(Images.get_all_image()),
                           runningContainer=len(Containers.get_container_according_to_status('running')),
                           username=current_user.username,
                           ret=json.dumps(ret, indent=4),
                           ping=ping)


@dockerm.route('/hosts', methods=['GET'])
@login_required
def hosts_page():
    host_list = []
    all_hosts = Hosts.get_all_host_by_paginate(page=request.args.get('page', 1, type=int))
    for host_info in all_hosts.items:
        # for info in host_info.image_list:
        #     print info.image_id
        host_list.append({'saltstack_id': host_info.saltstack_id, 'created_at': host_info.created_at,
                          'created_by': host_info.created_by, 'host_info': simplejson.loads(host_info.host_info)})
    return render_template('hosts.html',
                           pagination=all_hosts,
                           username=current_user.username,
                           host_list=host_list)


@dockerm.route('/containers/<saltstack_id>', methods=['GET'])
@login_required
def containers_page(saltstack_id):
    container_list = []
    if saltstack_id == 'all':
        all_container = Containers.get_all_container_by_pagination(request.args.get('page', 1, type=int))
        all_host = Hosts.get_all_host()
        for tmp in all_container.items:
            container_list.append(
                {'container_name': tmp.container_name, 'container_id': tmp.container_id, 'status': tmp.status,
                 'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at,
                 'json_info': simplejson.loads(tmp.info)})
        return render_template('containers.html',
                               pagination=all_container,
                               username=current_user.username,
                               is_all=True,
                               container_list=container_list,
                               host_list=all_host, )
    else:
        if Hosts.host_is_exited(saltstack_id):
            all_container = Containers.get_container_according_to_host_with_pagination(saltstack_id,
                                                                                       page=request.args.get('page', 1,
                                                                                                             type=int))
            all_host = Hosts.get_all_host()
            for tmp in all_container.items:
                container_list.append(
                    {'container_name': tmp.container_name, 'container_id': tmp.container_id, 'status': tmp.status,
                     'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at,
                     'json_info': simplejson.loads(tmp.info)})

            return render_template('containers.html',
                                   pagination=all_container,
                                   username=current_user.username,
                                   is_all=False,
                                   container_list=container_list,
                                   host_list=all_host,
                                   saltstack_id=saltstack_id)

        else:
            return render_template('error/404.html'), 404


@dockerm.route('/images/<saltstack_id>', methods=['GET'])
@login_required
def images_page(saltstack_id):
    image_list = []
    if saltstack_id == 'all':
        all_image = Images.get_all_image_by_paginate(page=request.args.get('page', 1, type=int))
        all_host = Hosts.get_all_host()
        for tmp in all_image.items:
            image_list.append(
                {'image_name': tmp.image_name, 'image_id': tmp.image_id,
                 'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at,
                 'json_info': simplejson.loads(tmp.info)})
        return render_template('images.html',
                               pagination=all_image,
                               username=current_user.username,
                               is_all=True,
                               image_list=image_list,
                               host_list=all_host)
    else:
        if Hosts.host_is_exited(saltstack_id):
            all_containers = Images.get_image_according_to_host_with_paginate(saltstack_id,
                                                                              page=request.args.get('page', 1,
                                                                                                    type=int))
            all_host = Hosts.get_all_host()
            for tmp in all_containers.items:
                image_list.append(
                    {'image_name': tmp.image_name, 'image_id': tmp.image_id,
                     'saltstack_id': tmp.saltstack_id, 'created_at': tmp.created_at,
                     'json_info': simplejson.loads(tmp.info)})
            return render_template('json_info.html',
                                   pagination=all_containers,
                                   username=current_user.username,
                                   is_all=False,
                                   image_list=image_list,
                                   host_list=all_host,
                                   saltstack_id=saltstack_id)
        else:
            return render_template('error/404.html'), 404


@dockerm.route('/container/info/<container_id>', methods=['GET'])
@login_required
def container_info_page(container_id):
    info = Containers.get_container_info_according_to_container_id(container_id)
    return render_template('info/container_info_view.html', container_id=container_id,
                           container_name=info.container_name, info=simplejson.loads(info.info))
