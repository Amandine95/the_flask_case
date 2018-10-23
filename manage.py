"""
manage.py程序启动入口
不关心app创建及业务逻辑、只关心启动相关参数
"""
import logging

from flask import session, current_app

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from info import create_app, db, models

# 通过配置名创建app
from info.models import User

app = create_app('develop')

# manage文件只关注一下代码
manager = Manager(app)
# 参数顺序不能反
Migrate(app, db)
# 添加迁移命令
manager.add_command('db', MigrateCommand)


# 创建管理员(实现命令操作创建管理员)
# 创建命令行的装饰器,将函数添加到命令行
# 命令行运行方式(命令窗口)：python manage.py createsuperuser -n xxx -p xxx
# dest--> 目标 option--> 参数
@manager.option('-n', '-name', dest='name')
@manager.option('-p', '-password', dest='password')
def createsuperuser(name, password):
    """创建管理员"""
    if not all([name, password]):
        print('参数错误')

    # 初始化用户模型
    user = User()
    user.nick_name = name
    user.mobile = name
    user.password = password
    # 是否是管理员的标志
    user.is_admin = True
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e)
    print('ok')


if __name__ == '__main__':
    manager.run()
