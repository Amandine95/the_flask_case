"""创建蓝图"""
from flask import Blueprint

# 创建蓝图
news_blu = Blueprint('news', __name__, url_prefix="/news")

# 当前目录导入views
from . import views
