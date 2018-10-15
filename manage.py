"""
manage.py程序启动入口
不关心app创建及业务逻辑、只关心启动相关参数
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

if __name__ == '__main__':
    manager.run()
