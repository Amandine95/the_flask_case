"""创建蓝图"""
from flask import Blueprint

# 创建蓝图
index_blu = Blueprint('index', __name__)

# 当前目录导入views
from . import views
