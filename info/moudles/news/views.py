from flask import render_template, session, current_app, g, jsonify, abort, request

from info import constants, db
from info.models import User, News, Category, Comment
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

    # (用户登录后)判断是否收藏
    if user:
        # lazy=dynamic 让 sqlalchemy在使用时自动加载，不需要.all()去加载
        if news in user.collection_news:
            is_collected = True

    # 传递data，详情页继承于base页面，base中需要用到data变量所以传入data
    data = {
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "news": news.to_dict(),
        "is_collected": is_collected

    }
    # print(news.to_dict())
    return render_template("news/detail.html", data=data)


@news_blu.route('/news_collect', methods=['post'])
@user_login_data
def collect_news():
    """新闻收藏"""
    user = g.user
    # 判断用户是否登录
    if not user:
        return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
    # 1、获取参数(新闻id、操作类型action)
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    # 2、校验参数
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    if action not in ["collect", "cancel_collect"]:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3、查询新闻
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="未查询到新闻")
    # 4、收藏，取消收藏(存储的是query对象)
    # if news not in user.collection_news:
    #     user.collection_news.append(news)

    if action == 'collect':
        # 收藏
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        # 取消收藏
        if news in user.collection_news:
            user.collection_news.remove(news)
    return jsonify(errno=RET.OK, errmsg="收藏成功")


@news_blu.route('/news_comment', methods=['post'])
@user_login_data
def comment_news():
    """新闻评论"""
    user = g.user
    # 1、判断登录
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户未登录")
    # 2、获取参数
    news_id = request.json.get('news_id')
    comment_data = request.json.get('comment')
    parent_id = request.json.get('parent_id')
    # 3、参数校验
    if not all([news_id, comment_data]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 校验数据类型
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 查询数据库
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="没有该新闻")
    # 4、初始化数据库模型，存储数据(插入一条评论记录)
    comment = Comment()
    comment.news_id = news_id
    comment.user_id = user.id
    comment.content = comment_data
    if parent_id:
        comment.parent_id = parent_id
    try:
        # 添加记录到数据库
        db.session.add(comment)
        # 自动提交在return之后，这里需要返回comment,所以在return之前手动commit
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库错误")
    # print(comment.to_dict())
    # 返回结果，前端需要获取评论相关信息  传入data
    return jsonify(errno=RET.OK, errmag="评论成功", data=comment.to_dict())
