"""
抽取配置代码，不同应用场景，不同的配置
字典记录配置
"""
import logging

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
    # 设置日志等级,默认环境下为debug
    LOG_LEVEL = logging.DEBUG


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境"""
    DEBUG = False
    # 生产环境下日志等级为warning
    LOG_LEVEL = logging.WARNING


class TestingConfig(Config):
    """测试环境"""
    TESTING = True

# 字典记录配置
config_dict = {
    'develop': DevelopmentConfig,
    'product': ProductionConfig,
    'test': TestingConfig
}
