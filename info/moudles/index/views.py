"""视图函数"""
from . import index_blu


# 注册路由
@index_blu.route('/')
def index():
    # 设置session
    # session['name'] = 'sam'
    # 测试打印日志
    # logging.debug('测试debug')
    # current输出日志
    # current_app.logger.error('测试error')
    return 'index'
