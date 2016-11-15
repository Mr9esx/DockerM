# -*- coding:utf-8 -*-
from flask import render_template, session, redirect, url_for,make_response,g,request
from flask_login import login_required
from . import dockerm
from ..lib.dbModel import *
from ..lib.jinja2models import *
from ..lib.pushMsg import pushMsg

@dockerm.route('/', methods=['GET'])
@login_required
def index():
    # 未来是关注列表
    all_container = getAllContainer()
    follow_container = getFollowing(all_container)
    container_list = []
    user = getUser(session['user_id'])
    for tmp in follow_container:
        container_list.append({'container_id':tmp.container_id,'container_name':tmp.container_name,'status':tmp.status,'host_id':tmp.host_id,'host_name':tmp.host_name})
    return render_template('index.html',
                           username=user.username,
                           containersList=container_list,
                           allHost=len(getAllHost()),
                           allContainer=len(all_container),
                           runningContainer=len(getContainerByStatus(status='running')))

@dockerm.route('/hosts/',methods=['GET'])
@login_required
def hostsPage():
    user = getUser(session['user_id'])
    page = checkPageFormat(request.args.get('page'))
    if page <= 0:
        return render_template('errorPage/404.html'), 404
    all_host = getAllHostAndPaginate(page)
    if page > all_host.pages:
        return render_template('errorPage/404.html'), 404
    hosts_list = []
    for tmp in all_host.items:
        hosts_list.append(
            {'host_id': tmp.host_id, 'host_name': tmp.host_name, 'create_time': tmp.create_time,
             'host_ip': tmp.host_ip,})
    return render_template('hosts.html',
                           pagination=all_host,
                           username=user.username,
                           hostsList=hosts_list)

@dockerm.route('/containers/<host>',methods=['GET'])
@login_required
def containersPage(host):
    user = getUser(session['user_id'])
    container_list = []
    page = checkPageFormat(request.args.get('page'))
    if host == 'all':
        # 判断页面是否小于0在前，因为不需要操作数据库即可判断
        if page <= 0:
            return render_template('errorPage/404.html'), 404
        all_containers = getAllContainerAndPaginate(page)
        # 判断页面是否大于最大页
        if page > all_containers.pages:
            return render_template('errorPage/404.html'), 404
        all_host = getAllHost()
        for tmp in all_containers.items:
            container_list.append(
                {'container_name': tmp.container_name, 'container_id': tmp.container_id, 'status': tmp.status,
                 'host_name':tmp.host_name,'host_id':tmp.host_id,'create_time':tmp.create_time,'json_info':tmp.info})
        return render_template('containers.html',
                               pagination=all_containers,
                               username=user.username,
                               is_all=True,
                               container_list=container_list,
                               host_list=all_host,)
    else:
        if HostisExited(host):
            if page <= 0:
                return render_template('errorPage/404.html'), 404
            all_containers = getAllContainer2HostAndPaginate(host,request.args.get('page'))
            if page > all_containers.pages:
                return render_template('errorPage/404.html'), 404
            all_host = getAllHost()
            for tmp in all_containers.items:
                container_list.append(
                    {'container_name': tmp.container_name, 'container_id': tmp.container_id, 'status': tmp.status,
                     'host_name': tmp.host_name, 'host_id': tmp.host_id, 'create_time': tmp.create_time,
                     'json_info': tmp.info})
            return render_template('containers.html',
                                   pagination=all_containers,
                                   username=user.username,
                                   is_all=False,
                                   container_list=container_list,
                                   host_list=all_host,
                                   host_id=host,
                                   host_name=container_list[0]['host_name'])
        else:
            return render_template('errorPage/404.html'), 404


@dockerm.route('/images/<host>',methods=['GET'])
@login_required
def imagesPage(host):
    user = getUser(session['user_id'])
    # 检查页数是否有输入和是否字符串
    page = checkPageFormat(request.args.get('page'))
    image_list = []
    if host == 'all':
        if page <= 0:
            return render_template('errorPage/404.html'), 404
        all_images = getAllImageAndPaginate(page)
        if page > all_images.pages:
            return render_template('errorPage/404.html'), 404
        all_host = getAllHost()
        for tmp in all_images.items:
            image_list.append(
                {'image_name': tmp.image_name, 'image_id': tmp.image_id, 'json_info': tmp.info,
                 'host_name':tmp.host_name,'host_id':tmp.host_id,'create_time':tmp.create_time})
        return render_template('images.html',
                               pagination=all_images,
                               username=user.username,
                               is_all=True,
                               image_list=image_list,
                               host_list=all_host,)
    else:
        if HostisExited(host):
            if page <= 0:
                return render_template('errorPage/404.html'), 404
            all_images = getAllImage2HostAndPaginate(host,page)
            if page > all_images.pages:
                return render_template('errorPage/404.html'), 404
            all_host = getAllHost()
            for tmp in all_images.items:
                image_list.append(
                    {'image_name': tmp.image_name, 'image_id': tmp.image_id, 'json_info': tmp.info,
                      'host_name': tmp.host_name,'host_id': tmp.host_id, 'create_time': tmp.create_time})
            return render_template('images.html',
                                   username=user.username,
                                   pagination=all_images,
                                   is_all=False,
                                   image_list=image_list,
                                   host_list=all_host,
                                   host_id=host,
                                   host_name=image_list[0]['host_name'])
        else:
            return render_template('errorPage/404.html'), 404

@dockerm.route('/container/info/<container_id>',methods=['GET'])
@login_required
def containerInfoView(container_id):
    if ContaineriExited(container_id):
        info = getContainerInfo(container_id)
        return render_template('info/container_info_view.html',
                               status = info.status,
                               host_id = info.host_id,
                               info = info.info,
                               container_name=info.container_name,
                               container_id=info.container_id)
    else:
        return render_template('errorPage/404.html'),404

@dockerm.route('/image/info/<image_id>',methods=['GET'])
@login_required
def imageInfoView(image_id):
    if ImageExited(image_id):
        info = getImageInfo(image_id)
        return render_template('info/image_info_view.html',
                               host_id = info.host_id,
                               info = info.info,
                               history = info.history,
                               image_name = info.image_name,
                               image_id = info.image_id)
    else:
        return render_template('errorPage/404.html'),404

@dockerm.route('/container/download/inspect/<container_id>',methods=['GET'])
@login_required
def downloadContainerInspect(container_id):
    try:
        content = json.dumps(getContainerInfo(container_id).info, indent=4)
    except Exception,e:
        return render_template('errorPage/404.html'), 404
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=container__{}__InspectInfomation.txt".format(container_id)
    return response

@dockerm.route('/image/download/inspect/<image_id>',methods=['GET'])
@login_required
def downloadImageInspect(image_id):
    try:
        content = json.dumps(getImageInfo(image_id).info, indent=4)
    except Exception,e:
        return render_template('errorPage/404.html'), 404
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=image__{}__InspectInfomation.txt".format(image_id)
    return response

@dockerm.route('/control/container/<control_type>',methods=['POST'])
@login_required
def containerControl(control_type):
    print control_type
    if control_type == 'start':
        pushMsg(request.form['container_id'],control_type).push()
    elif control_type == 'follow':
        updateContainerFollowState(request.form['container_id'],1)
    elif control_type == 'unfollow':
        print 'unfollow'
        updateContainerFollowState(request.form['container_id'], 0)
    return '0'