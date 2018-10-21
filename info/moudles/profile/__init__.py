"""登录注册模块"""
from flask import Blueprint

# 添加前缀
profile_blu = Blueprint('profile', __name__, url_prefix='/user')

from . import views
