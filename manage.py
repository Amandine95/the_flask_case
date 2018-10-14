"""
配置redis和csrf
session存储在redis里
"""
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect
# 指定session保存的位置
from flask_session import Session
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from config import Config

app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)
# redis初始化
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目CSRF保护,只做服务器验证
CSRFProtect(app)
# 设置session保存指定位置
Session(app)
manager = Manager(app)
# 参数顺序不能反
Migrate(app, db)
# 添加迁移命令
manager.add_command('db', MigrateCommand)


@app.route('/')
def index():
    # 设置session
    session['name'] = 'sam'
    return 'index'


if __name__ == '__main__':
    manager.run()
