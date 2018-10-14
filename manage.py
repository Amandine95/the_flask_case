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


class Config(object):
    """项目配置"""
    # 秘钥
    SECRET_KEY = 'asjshdjddjfkh'
    DEBUG = True
    # 添加数据库配置
    SQLALCHEMY_DATABASE_URI = 'mysql://root:950324lyx@127.0.0.1:3306/information_flask'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    # session保存在redis里
    SESSION_TYPE = 'redis'
    # 开启session签名
    SESSION_SIGNER = True
    # 指定session保存的redis
    SESSION_REDIS = StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    # 设置session需要过期
    SESSION_PERMANENT = False
    # 过期时间为2天
    PERMANENT_SESSION_LIFETIME = 86400 * 2


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


@app.route('/')
def index():
    # 设置session
    session['name'] = 'sam'
    return 'index'


if __name__ == '__main__':
    manager.run()
