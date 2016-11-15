from datetime import datetime
from flask import  session, redirect, url_for,jsonify,g,request
from flask_login import login_required
from . import dockermApi
from ..lib.rawSQL import rawSQLControl

@dockermApi.route('/api/v1.0/container/getstatus/<container_id>',methods=['GET'])
@login_required
def getStatus(container_id):
    return jsonify(rawSQLControl().getContainerState(container_id,60))