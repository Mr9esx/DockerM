# -*- coding:utf-8 -*-
# Flask-SQLAlchemy 操作数据库
from .. import db
from werkzeug.security import generate_password_hash
import time

class User(db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(128),unique=True)
    password = db.Column(db.String(128))
    email = db.Column(db.String(128),primary_key=True)
    level = db.Column(db.Integer)
    confirmed = db.Column(db.Integer)

    # 构造函数
    def __init__(self,username,password,email,level):
        self.username = username
        self.password = password
        self.email = email
        self.level = level
        self.confirmed = 1

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)

class Containers(db.Model):
    __tablename__ = 'Containers'
    container_id = db.Column(db.String(128),primary_key=True)
    container_name = db.Column(db.String(128))
    image_id = db.Column(db.String(128))
    host_id = db.Column(db.String(128))
    host_name = db.Column(db.String(128))
    create_time = db.Column(db.DateTime)
    status = db.Column(db.String(45))
    info = db.Column(db.JSON)
    follow = db.Column(db.Integer)

    # 构造函数
    def __init__(self,container_id,container_name,host_id,host_name,create_time,status,info,follow):
        self.container_id = container_id
        self.container_name = container_name
        self.host_id = host_id
        self.host_name = host_name
        self.create_time = create_time
        self.status = status
        self.info = info
        self.follow = follow

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)

class Hosts(db.Model):
    __tablename__ = 'Hosts'
    id = db.Column(db.Integer, primary_key=True)
    host_id = db.Column(db.String(128), primary_key=True)
    host_name = db.Column(db.String(128))
    host_ip = db.Column(db.String(32))
    host_redis_port = db.Column(db.String(16))
    host_redis_pw = db.Column(db.String(128))
    create_time = db.Column(db.DateTime)

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)

class Images(db.Model):
    __tablename__ = 'Images'
    id = db.Column(db.Integer, primary_key=True)
    image_id = db.Column(db.String(128), primary_key=True)
    image_name = db.Column(db.JSON)
    host_id = db.Column(db.String(128))
    host_name = db.Column(db.String(128))
    create_time = db.Column(db.DateTime)
    info = db.Column(db.JSON)
    history = db.Column(db.JSON)

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)

class Container_Status(db.Model):
    __tablename__ = 'Container_Status'
    id = db.Column(db.Integer,primary_key=True)
    container_id = db.Column(db.String(255))
    cpu_percent = db.Column(db.Float)
    memory_usage = db.Column(db.String(255))
    memory_limit = db.Column(db.String(255))
    memory_percent = db.Column(db.Float)
    tx_packets = db.Column(db.String(255))
    tx_bytes = db.Column(db.String(255))
    tx_dropped = db.Column(db.String(255))
    tx_errors = db.Column(db.String(255))
    tx_speed = db.Column(db.String(255))
    rx_packets = db.Column(db.String(255))
    rx_bytes = db.Column(db.String(255))
    rx_dropped = db.Column(db.String(255))
    rx_errors = db.Column(db.String(255))
    rx_speed = db.Column(db.String(255))
    collect_time = db.Column(db.String(255))

    def to_dict(self):
        column_name_list = [value[0] for value in self._sa_instance_state.attrs.items()]
        return dict((column_name, getattr(self, column_name, None)) for column_name in column_name_list)


'''用户操作'''
def createUser(username,password,email,level):
    '''
    @:return:创建用户函数
    @:rtype:bool
    @:param username:用户名
    @:param password:用户密码
    @:param email:用户邮箱地址
    @:param level:用户权限
    '''
    try:
        password = generate_password_hash(password)
        u = User(username,password,email,level)
        db.session.add(u)
        db.session.commit()
        # 添加：日志纪录（用户注册成功）
        return True
    except Exception, e:
        db.session.rollback
        return False

def checkUserIsRegister(username):
    '''
    @:return:检查用户名是否已经注册了
    @:rtype:bool
    @:param username:用户名
    '''
    userisexited = User.query.filter_by(username=username).first()
    if userisexited == None:
        return True
    else:
        # 添加：日志纪录（用户注册失败）
        return False

def checkEmailIsRegister(email):
    '''
    @:return:检查用户邮箱地址是否已经注册了
    @:rtype:bool
    @:param email:用户邮箱地址
    '''
    emailisexited = User.query.filter_by(email=email).first()
    if emailisexited == None:
        return True
    else:
        # 添加：日志纪录（用户注册失败）
        return False

def getUser(user_id):
    '''
    @:return:根据 flask-login 生成保存 seesion 中的 u_id 来获取用户信息
    @:param user_id:用户 id
    '''
    user = User.query.filter_by(id=user_id).first()
    return user
'''/用户操作'''


'''获取容器信息'''
def getAllContainer():
    '''
    @:return:返回含有全部主机的全部容器信息的List，并按时间降序排序
    @:rtype:list
    '''
    return Containers.query.order_by('create_time DESC').all()

def getAllContainerAndPaginate(page):
    '''
    @:return:使用分页的形式返回含有全部主机的全部容器信息，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:note:记得加 .items 才能获取或者遍历数据
    '''
    return Containers.query.order_by('create_time DESC').paginate(page, 15, False)

def getAllContainer2Host(host_id):
    '''
    @:return:返回含有指定主机的全部容器信息的List，并按时间降序排序
    @:rtype:list
    @:param host_id:主机 id
    '''
    return Containers.query.filter_by(host_id=host_id).order_by('create_time DESC').all()

def getAllContainer2HostAndPaginate(host_id,page):
    '''
    @:return:使用分页的形式返回含有指定主机的全部容器信息的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param host_id:主机 id
    @:param page:页数
    '''
    return Containers.query.filter_by(host_id=host_id).order_by('create_time DESC').paginate(page, 15, False)

def getContainerByStatus(status):
    '''
    @:return:返回含有全部主机的指定容器状态信息的List，并按时间降序排序
    @:rtype:list
    @:param status:主机 id
    '''
    return Containers.query.order_by('create_time DESC').filter_by(status=status).all()

def getContainerByStatusAndPaginate(status,page):
    '''
    @:return:使用分页的形式返回含有全部主机的指定容器状态信息的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param status:主机 id
    @:param page:页数
    '''
    return Containers.query.order_by('create_time DESC').filter_by(status=status).all().paginate(page, 15, False)

def getContainerInfo(container_id):
    '''
    @:return:获取指定容器的全部信息
    @:rtype:app.lib.dbModel.Containers
    @:param container_id:容器 id
    '''
    return Containers.query.filter_by(container_id=container_id).first()


def getFollowing(follow):
    '''
    @:return:获取被关注的信息
    @:rtype:app.lib.dbModel.Containers
    @:param container_id:容器 id

    '''
    followList = []
    for tmp in follow:
        if int(tmp.follow) is 1:
            followList.append(tmp)
    return followList

def updateContainerFollowState(container_id,state):
    if state is 0 or state is 1:
        print state
        container = Containers.query.filter_by(container_id=container_id).first()
        container.follow = state
        print container.follow
        db.session.commit()
        return True
    else:
        return False

def getHostInfoByContainerID(container_id):
    '''
    @:return:获取指定容器 ID 的主机信息
    @:rtype:app.lib.dbModel.Container
    @:param container_id:容器 ID
    '''
    return Containers.query.filter_by(container_id=container_id).first()
'''\获取容器信息'''


'''获取主机信息'''
def getAllHost():
    '''
    @:return:返回含有全部主机信息的List，并按时间降序排序。如
    @:rtype:list
    '''
    return Hosts.query.order_by('create_time DESC').all()

def getAllHostAndPaginate(page):
    '''
    @:return:使用分页的形式返回含有全部主机信息的List，并按时间降序排序
    @:rtype:list
    @:param page:页数
    '''
    return Hosts.query.order_by('create_time DESC').paginate(page, 15, False)

def getHostInfo(host_id):
    '''
    @:return:获取指定主机的信息
    @:rtype:app.lib.dbModel.Hosts
    @:param host_id:主机 ID
    '''
    return Hosts.query.filter_by(host_id=host_id).first()
'''\获取主机信息'''


'''获取镜像信息'''
def getAllImage():
    '''
    @:return:返回含有全部主机的全部镜像信息的List，并按时间降序排序
    @:rtype:list
    '''
    return Images.query.order_by('create_time DESC').all()

def getAllImageAndPaginate(page):
    '''
    @:return:使用分页的形式返回含有全部主机的全部镜像信息，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:note:记得加 .items 才能获取或者遍历数据
    '''
    return Images.query.order_by('create_time DESC').paginate(page, 15, False)

def getAllImage2Host(host_id):
    '''
    @:return:返回含有指定主机的全部镜像信息的List，并按时间降序排序
    @:rtype:list
    @:param host_id:主机 id
    '''
    return Images.query.filter_by(host_id=host_id).order_by('create_time DESC').all()

def getAllImage2HostAndPaginate(host_id,page):
    '''
    @:return:使用分页的形式返回含有指定主机的全部镜像信息的List，并按时间降序排序
    @:rtype:flask_sqlalchemy.Pagination
    @:param host_id:主机 id
    @:param page:页数
    '''
    return Images.query.filter_by(host_id=host_id).order_by('create_time DESC').paginate(page, 15, False)

def getImageInfo(image_id):
    '''
    @:return:获取指定镜像的全部信息
    @:rtype:app.lib.dbModel.Images
    @:param image_id:镜像 ID
    '''
    return Images.query.filter_by(image_id=image_id).first()
'''\获取镜像信息'''


'''验证页数'''
def checkPageFormat(page):
    '''
    @:return:传入 GET 传来的页数，验证类型是否为 int ，因为 Python 的 int 长度大于 SQL 长度，所以限制页面小于 9999999 ，防止 SQL 溢出。
    @:rtype:int
    @:param page:页数
    '''
    if page is None:
        return 1
    try:
        page = int(page)
        if page > 9999999:
            return 0
    except Exception,ValueError:
        return 0
    return page


'''验证主机是否存在'''
def HostisExited(host_id):
    '''
    @:return:传入主机ID，并从数据库中查询，不存在返回False。
    @:rtype:bool
    @:param host_id:主机 ID
    '''
    if Hosts.query.filter_by(host_id=host_id).first() is None:
        return False
    else:
        return True


'''验证容器是否存在'''
def ContaineriExited(container_id):
    '''
    @:return:传入主机ID，并从数据库中查询，不存在返回False。
    @:rtype:bool
    @:param host_id:主机 ID
    '''
    if Containers.query.filter_by(container_id=container_id).first() is None:
        return False
    else:
        return True


'''验证镜像是否存在'''
def ImageExited(image_id):
    '''
    @:return:传入主机ID，并从数据库中查询，不存在返回False。
    @:rtype:bool
    @:param host_id:主机 ID
    '''
    if Images.query.filter_by(image_id=image_id).first() is None:
        return False
    else:
        return True

'''Api'''
def getContainerStatus(container_id):
    '''
    @:return:Api 接口，获取指定容器监控信息。(目前没用)
    @:rtype:list
    @:param container_id:容器 ID
    '''
    if ContaineriExited(container_id):
        tmp = Container_Status.query.filter_by(container_id=container_id).limit(60).all()
        print len(tmp)
        json = []
        [json.append(data.to_dict()) for data in tmp]
        print json
        return json
    else:
        pass
'''/Api'''