"""创建根路由、模板文件夹"""
from info import redis_store
from . import index_blu
from flask import render_template


# 注册路由
@index_blu.route('/')
def index():
    redis_store.set('sam_smith', 'billy')

    return render_template('news/index.html')
