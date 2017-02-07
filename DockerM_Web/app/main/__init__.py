from flask import Blueprint

dockerm = Blueprint('dockerm', __name__)

from . import views, errors
