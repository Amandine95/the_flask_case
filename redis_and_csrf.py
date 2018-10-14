"""
配置redis和csrf
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf import CSRFProtect


class Config(object):
    """项目配置"""
    DEBUG = True
    # 添加数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:950324lyx@127.0.0.1:3306/information_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379


app = Flask(__name__)
# 加载配置
app.config.from_object(Config)
# 初始化数据库
db = SQLAlchemy(app)
# redis初始化
redis_store = StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT)
# 开启当前项目CSRF保护,只做服务器验证
CSRFProtect(app)


@app.route('/')
def index():
    return 'index'


if __name__ == '__main__':
    app.run()
