"""
处理关于redis_store相关问题
"""
from logging.handlers import RotatingFileHandler
import logging

from flask import Flask, render_template, g
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from redis import StrictRedis

from config import config_dict

db = SQLAlchemy()
# type设置变量注释后可以智能提示
redis_store = None  # type:StrictRedis


# redis_store:StrictRedis=None


def setup_log(config_name):
    """设置日志"""
    # 设置日志的记录等级
    logging.basicConfig(level=config_dict[config_name].LOG_LEVEL)  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式 日志等级 输入日志信息的文件名 行数 日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)


def create_app(config_name):
    """创建app,类似工厂方法"""
    # 配置日志,传入配置名来获取对应配置等级
    setup_log(config_name)
    # 创建flask对象
    app = Flask(__name__)
    # 加载配置,实际开发中配置信息应该从入口文件传入即传入config_name
    app.config.from_object(config_dict[config_name])
    # 初始化db,flask中可以先创建扩展包对象再调用init_app初始化
    db.init_app(app)

    # 声明为全局变量
    global redis_store
    # redis赋值，此处用于在业务逻辑中的存储  decode_response = True
    redis_store = StrictRedis(host=config_dict[config_name].REDIS_HOST, port=config_dict[config_name].REDIS_PORT)
    # 开启当前项目CSRF保护,只做服务器验证
    # CSRFProtect实现功能：从cookie、表单中取出随机值校验，返回结果。
    # 需要实现：1、界面加载时，添加一个csrf_token到cookie中；2、添加同样的csrf_token到表单
    # 登录注册用ajax请求，对于第二步让ajax请求时headers带上crsf_token。

    CSRFProtect(app)
    # 设置session保存指定位置
    Session(app)

    # 导入并添加过滤器
    from info.utils.commmon import do_index_class
    app.add_template_filter(do_index_class, "index_class")

    # 响应时设置cookie，全局多处设置cookie，所以用请求钩子after_request设置csrf_token
    @app.after_request
    def after_request(response):
        # 设置随机的csrf_token值
        csrf_token = generate_csrf()
        # 设置一个cookie
        response.set_cookie("csrf_token", csrf_token)
        return response

    # 全局404页面的处理
    from info.utils.commmon import user_login_data

    # @app.route('/404')
    # 捕获全局404异常
    @app.errorhandler(404)
    @user_login_data
    def page_not_found(e):
        """404页面渲染"""
        user = g.user
        data = {
            "user": user.to_dict() if user else None

        }
        return render_template('news/404.html', data=data)

    # 蓝图注册时再导入
    from info.moudles.index import index_blu
    # 注册蓝图
    app.register_blueprint(index_blu)

    # 注册登录模块蓝图
    from info.moudles.passport import passport_blu
    app.register_blueprint(passport_blu)
    # 新闻详情蓝图
    from info.moudles.news import news_blu
    app.register_blueprint(news_blu)
    from info.moudles.profile import profile_blu
    app.register_blueprint(profile_blu)
    return app
