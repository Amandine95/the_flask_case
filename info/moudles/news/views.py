from flask import render_template, session, current_app, g, jsonify, abort

from info import constants
from info.models import User, News, Category
from info.moudles.news import news_blu
from info.utils.commmon import user_login_data
from info.utils.response_code import RET


@news_blu.route('/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    获取新闻详情
    """
    # 获取session数据
    # user_id = session.get('user_id', None)
    # user = None
    # if user_id:
    #     try:
    # 查询数据库
    #     user = User.query.get(user_id)
    # except Exception as e:
    #     current_app.logger.error(e)
    user = g.user
    # 右侧排行榜逻辑(查询数据库新闻点击量，大到小排序，取出前六(可通过修改常量改变))
    news_list = []
    try:
        # 数据库取出的是对象列表，要将对象转换为dict
        news_list = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    # 新闻字典列表
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    # 访问根路由时，查询新闻分类，通过模板渲染
    categories = None
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
    category_list = []
    for category in categories:
        category_list.append(category.to_dict())

    # 查询新闻数据
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    # 未查到抛出404
    if not news:
        abort(404)
    # 更新新闻点击次数
    news.clicks += 1

    # 是否收藏标志
    is_collected = False

    # 判断是否收藏

    # 传递data，详情页继承于base页面，base中需要用到data变量所以传入data
    data = {
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "news": news.to_dict(),
        "is_collected": is_collected

    }
    # print(news.to_dict())
    return render_template("news/detail.html", data=data)
