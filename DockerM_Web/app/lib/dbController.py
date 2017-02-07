# -*- coding:utf-8 -*-
from .. import db
from werkzeug.security import generate_password_hash
import time
from sqlalchemy import desc

from dbModel import User, Hosts, Containers, Images, Container_Status, Operation_Log


def getAllOperationLogAndPaginate(page):
    """
    @:return:使用分页的形式返回全部日志的List，并按时间降序排序
    @:param page:页数
    """
    return Operation_Log.query.order_by(desc(operation_time)).paginate(page, 15, False)


def getAllOperationLog():
    """
    @:return:获取全部日志，并按时间降序排序
    """
    return Operation_Log.query.order_by(desc(operation_time)).all()


def getOperationLog2HostAndPaginate(host_id, page):
    """
    @:return:使用分页的形式返回含有指定主机的全部日志的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param host_id:主机 id
    @:param page:页数
    """
    return Operation_Log.query.filter_by(host_id=host_id).order_by(desc(operation_time)).paginate(page, 15, False)


"""用户操作"""


def createUser(username, password, email, level):
    """
    @:return:创建用户函数
    @:rtype:bool
    @:param username:用户名
    @:param password:用户密码
    @:param email:用户邮箱地址
    @:param level:用户权限
    """
    try:
        password = generate_password_hash(password)
        u = User(username, password, email, level)
        db.session.add(u)
        db.session.commit()
        # 添加：日志纪录（用户注册成功）
        return True
    except Exception, e:
        db.session.rollback
        return False


def checkUserIsRegister(username):
    """
    @:return:检查用户名是否已经注册了
    @:rtype:bool
    @:param username:用户名
    """
    userisexited = User.query.filter_by(username=username).first()
    if userisexited == None:
        return True
    else:
        # 添加：日志纪录（用户注册失败）
        return False


def checkEmailIsRegister(email):
    """
    @:return:检查用户邮箱地址是否已经注册了
    @:rtype:bool
    @:param email:用户邮箱地址
    """
    emailisexited = User.query.filter_by(email=email).first()
    if emailisexited == None:
        return True
    else:
        # 添加：日志纪录（用户注册失败）
        return False


def getUser(user_id):
    """
    @:return:根据 flask-login 生成保存 seesion 中的 u_id 来获取用户信息
    @:param user_id:用户 id
    """
    user = User.query.filter_by(id=user_id).first()
    return user


"""/用户操作"""

"""获取容器信息"""


def getAllContainer():
    """
    @:return:返回含有全部主机的全部容器信息的List，并按时间降序排序
    @:rtype:list
    """
    return Containers.query.order_by(desc('created_at')).all()


def getAllContainerAndPaginate(page):
    """
    @:return:使用分页的形式返回含有全部主机的全部容器信息，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:note:记得加 .items 才能获取或者遍历数据
    """
    if page is None or int(page) <= 0:
        page = 1
    else:
        try:
            page = int(page)
        except:
            page = 1
    result = Containers.query.order_by(desc('created_at')).paginate(page, 15, False)
    if page > result.pages:
        result = Containers.query.order_by(desc('created_at')).paginate(result.pages, 15, False)
    return result


def getAllContainer2Host(saltstack_id):
    """
    @:return:返回含有指定主机的全部容器信息的List，并按时间降序排序
    @:rtype:list
    @:param host_id:主机 id
    """
    return Containers.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).all()


def getAllContainer2HostAndPaginate(saltstack_id, page):
    """
    @:return:使用分页的形式返回含有指定主机的全部容器信息的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param host_id:主机 id
    @:param page:页数
    """
    if page is None or int(page) <= 0:
        page = 1
    else:
        try:
            page = int(page)
        except:
            page = 1
    result = Containers.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).paginate(page, 15,
                                                                                                         False)
    if page > result.pages and result.pages != 0:
        result = Containers.query.order_by(desc('created_at')).paginate(result.pages, 15, False)
    return result


def getContainerByStatus(status):
    """
    @:return:返回含有全部主机的指定容器状态信息的List，并按时间降序排序
    @:rtype:list
    @:param status:主机 id
    """
    return Containers.query.order_by(desc('created_at')).filter_by(status=status).all()


def getContainerByStatusAndPaginate(status, page):
    """
    @:return:使用分页的形式返回含有全部主机的指定容器状态信息的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param status:主机 id
    @:param page:页数
    """
    return Containers.query.order_by(desc('created_at')).filter_by(status=status).all().paginate(page, 15, False)


def getContainerInfo(container_id):
    """
    @:return:获取指定容器的全部信息
    @:rtype:app.lib.dbModel.Containers
    @:param container_id:容器 id
    """
    return Containers.query.filter_by(container_id=container_id).first()


def getFollowing(follow):
    """
    @:return:获取被关注的信息
    @:rtype:app.lib.dbModel.Containers
    @:param container_id:容器 id

    """
    followList = []
    for tmp in follow:
        if int(tmp.follow) is 1:
            followList.append(tmp)
    return followList


def updateContainerFollowState(container_id, state):
    if state is 0 or state is 1:
        container = Containers.query.filter_by(container_id=container_id).first()
        container.follow = state
        db.session.commit()
        return True
    else:
        return False


def getHostInfoByContainerID(container_id):
    """
    @:return:获取指定容器 ID 的主机信息
    @:rtype:app.lib.dbModel.Container
    @:param container_id:容器 ID
    """
    return Containers.query.filter_by(container_id=container_id).first()


"""\获取容器信息"""

"""获取主机信息"""


def getAllHost():
    """
    @:return:返回含有全部主机信息的List，并按时间降序排序。如
    @:rtype:list
    """
    return Hosts.query.order_by(desc('created_at')).all()


def getAllHostAndPaginate(page):
    """
    @:return:使用分页的形式返回含有全部主机信息的List，并按时间降序排序
    @:rtype:list
    @:param page:页数
    """
    return Hosts.query.order_by(desc('created_at')).paginate(page, 15, False)


def getHostInfo(host_id):
    """
    @:return:获取指定主机的信息
    @:rtype:app.lib.dbModel.Hosts
    @:param host_id:主机 ID
    """
    return Hosts.query.filter_by(host_id=host_id).first()


"""\获取主机信息"""

"""获取镜像信息"""


def getAllImage():
    """
    @:return:返回含有全部主机的全部镜像信息的List，并按时间降序排序
    @:rtype:list
    """
    return Images.query.order_by(desc('created_at')).all()


def getAllImageAndPaginate(page):
    """
    @:return:使用分页的形式返回含有全部主机的全部镜像信息，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:note:记得加 .items 才能获取或者遍历数据
    """
    return Images.query.order_by(desc('created_at')).paginate(page, 15, False)


def getAllImage2Host(saltstack_id):
    """
    @:return:返回含有指定主机的全部镜像信息的List，并按时间降序排序
    @:rtype:list
    @:param host_id:主机 id
    """
    return Images.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).all()


def getAllImage2HostAndPaginate(saltstack_id, page):
    """
    @:return:使用分页的形式返回含有指定主机的全部镜像信息的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param host_id:主机 id
    @:param page:页数
    """
    return Images.query.filter_by(saltstack_id=saltstack_id).order_by(desc('created_at')).paginate(page, 15, False)


def getImageInfo(image_id):
    """
    @:return:获取指定镜像的全部信息
    @:rtype:app.lib.dbModel.Images
    @:param image_id:镜像 ID
    """
    return Images.query.filter_by(image_id=image_id).first()


"""\获取镜像信息"""

"""验证页数"""


def checkPageFormat(page):
    """
    @:return:传入 GET 传来的页数，验证类型是否为 int ，因为 Python 的 int 长度大于 SQL 长度，所以限制页面小于 9999999 ，防止 SQL 溢出。
    @:rtype:int
    @:param page:页数
    """
    if page is None:
        return 1
    try:
        page = int(page)
        if page > 9999999:
            return 0
    except Exception, ValueError:
        return 0
    return page


"""验证主机是否存在"""


def HostisExited(saltstack_id):
    """
    @:return:传入主机ID，并从数据库中查询，不存在返回False。
    @:rtype:bool
    @:param host_id:主机 ID
    """
    if Hosts.query.filter_by(saltstack_id=saltstack_id).first() is None:
        return False
    else:
        return True


"""验证容器是否存在"""


def ContaineriExited(container_id):
    """
    @:return:传入主机ID，并从数据库中查询，不存在返回False。
    @:rtype:bool
    @:param host_id:主机 ID
    """
    if Containers.query.filter_by(container_id=container_id).first() is None:
        return False
    else:
        return True


"""验证镜像是否存在"""


def ImageExited(image_id):
    """
    @:return:传入主机ID，并从数据库中查询，不存在返回False。
    @:rtype:bool
    @:param host_id:主机 ID
    """
    if Images.query.filter_by(image_id=image_id).first() is None:
        return False
    else:
        return True


"""Api"""


def getContainerStatus(container_id):
    """
    @:return:Api 接口，获取指定容器监控信息。(目前没用)
    @:rtype:list
    @:param container_id:容器 ID
    """
    if ContaineriExited(container_id):
        tmp = Container_Status.query.filter_by(container_id=container_id).limit(60).all()
        json = []
        [json.append(data.to_dict()) for data in tmp]
        return json
    else:
        pass


"""/Api"""
