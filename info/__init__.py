"""
将业务逻辑代码抽取,info存放所有业务逻辑代码
"""
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config_dict

# 创建数据库对象
db = SQLAlchemy()


def create_app(config_name):
    """创建app,类似工厂方法"""
    app = Flask(__name__)
    # 加载配置,实际开发中配置信息应该从入口文件传入即传入config_name
    app.config.from_object(config_dict[config_name])
    # 初始化db,flask中可以先创建扩展包对象再调用init_app初始化
    db.init_app(app)

    # redis初始化
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST, port=config_dict[config_name].REDIS_PORT)
    # 开启当前项目CSRF保护,只做服务器验证
    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)
    return app
