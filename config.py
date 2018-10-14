"""
抽取配置代码
"""
from redis import StrictRedis


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
