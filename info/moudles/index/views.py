"""添加网页页签图片的路由，这个请求路径是固定的  /文件名 """
from info import redis_store
from info.models import User, News
from . import index_blu
from flask import render_template, current_app, session


# 注册路由
@index_blu.route('/')
def index():
    """
    返回主页(登陆后状态显示)
    0、登录注册后session中都会存储用户数据
    1、已登录、查询(session中获取)用户数据(nick_name,avatar)显示在模板
    2、未登录，查询不到数据，显示默认
    """
    # 获取session数据
    user_id = session.get('user_id', None)
    user = None
    if user_id:
        try:
            # 查询数据库
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)

    # 右侧排行榜逻辑(查询数据库新闻点击量，大到小排序，取出前六)
    news_list = []
    try:
        # 数据库取出的是对象列表，要将对象转换为dict
        news_list = News.query.order_by(News.clicks.desc()).limit(6)
    except Exception as e:
        current_app.logger.error(e)
    # 新闻字典列表
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
        # user有值，执行user.to_dict()；如果user没有值，将None给"user"
    data = {
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list
    }

    # 渲染模板
    return render_template('news/index.html', data=data)


# 图标路由
@index_blu.route('/favicon.ico')
def favicon():
    """查找发送页签图标"""
    # current_app应用上下文变量，表示当前应用
    # send_static_file是flask查找指定静态文件的方法，浏览器自动请求小图标
    return current_app.send_static_file('news/favicon.ico')
