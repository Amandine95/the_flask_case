"""登录注册模块"""
from flask import Blueprint

# 添加前缀
passport_blu = Blueprint('passport', __name__, url_prefix='/passport')

from . import views
