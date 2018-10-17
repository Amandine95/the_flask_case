"""添加网页页签图片的路由，这个请求路径是固定的  /文件名 """
from info import redis_store
from . import index_blu
from flask import render_template, current_app


# 注册路由
@index_blu.route('/')
def index():
    redis_store.set('sam_smith', 'billy')

    return render_template('news/index.html')


# 图标路由
@index_blu.route('/favicon.ico')
def favicon():
    """查找发送页签图标"""
    # current_app应用上下文变量，表示当前应用
    # send_static_file是flask查找指定静态文件的方法，浏览器自动请求小图标
    return current_app.send_static_file('news/favicon.ico')
