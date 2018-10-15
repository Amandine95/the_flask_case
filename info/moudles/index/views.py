"""视图函数"""
from info import redis_store
from . import index_blu


# 注册路由
@index_blu.route('/')
def index():
    redis_store.set('sam_smith', 'billy')

    return 'index'
