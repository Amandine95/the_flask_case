"""
将业务逻辑代码抽取,info存放所有业务逻辑代码
"""
from flask import Flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from redis import StrictRedis

from config import config_dict

app = Flask(__name__)
# 加载配置
app.config.from_object(config_dict['develop'])
# 初始化数据库
db = SQLAlchemy(app)
# redis初始化
redis_store = StrictRedis(host=config_dict['develop'].REDIS_HOST, port=config_dict['develop'].REDIS_PORT)
# 开启当前项目CSRF保护,只做服务器验证
CSRFProtect(app)
# 设置session保存指定位置
Session(app)
