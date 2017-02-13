# -*- coding:utf-8 -*-
# from sqlalchemy import desc
#
# from dbModel import User, Hosts, Containers, Images, Container_Status, Operation_Log
#
#
# def getAllOperationLogAndPaginate(page):
#     """
#     @:return:使用分页的形式返回全部日志的List，并按时间降序排序
#     @:param page:页数
#     """
#     return Operation_Log.query.order_by(desc(operation_time)).paginate(page, 15, False)
#
#
# def getAllOperationLog():
#     """
#     @:return:获取全部日志，并按时间降序排序
#     """
#     return Operation_Log.query.order_by(desc(operation_time)).all()
#
#
# def getOperationLog2HostAndPaginate(host_id, page):
#     """
#     @:return:使用分页的形式返回含有指定主机的全部日志的List，并按时间降序排序
#     @:rtype:flask_sqlalchemy.Pagination
#     @:param host_id:主机 id
#     @:param page:页数
#     """
#     return Operation_Log.query.filter_by(host_id=host_id).order_by(desc(operation_time)).paginate(page, 15, False)
