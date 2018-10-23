"""创建蓝图"""
from flask import Blueprint

# 创建蓝图
admin_blu = Blueprint('admin', __name__)

# 当前目录导入views
from . import views
