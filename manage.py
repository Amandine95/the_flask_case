"""
配置redis和csrf
session存储在redis里
"""
import logging

from flask import session, current_app

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from info import create_app, db

# 通过配置名创建app
app = create_app('develop')

# manage文件只关注一下代码
manager = Manager(app)
# 参数顺序不能反
Migrate(app, db)
# 添加迁移命令
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    # 设置session
    # session['name'] = 'sam'
    # 测试打印日志
    logging.debug('测试debug')
    # current输出日志
    # current_app.logger.error('测试error')
    return 'index'


if __name__ == '__main__':
    manager.run()
