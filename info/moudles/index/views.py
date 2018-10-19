"""添加网页页签图片的路由，这个请求路径是固定的  /文件名 """
from info import redis_store, constants
from info.models import User, News, Category
from info.utils.commmon import user_login_data
from info.utils.response_code import RET
from . import index_blu
from flask import render_template, current_app, session, request, jsonify, g


# 注册路由
@index_blu.route('/')
@user_login_data
def index():
    """
    返回主页(登陆后状态显示)
    0、登录注册后session中都会存储用户数据
    1、已登录、查询(session中获取)用户数据(nick_name,avatar)显示在模板
    2、未登录，查询不到数据，显示默认
    """
    # 获取session数据
    # user_id = session.get('user_id', None)
    # user = None
    # if user_id:
    #     try:
    #         # 查询数据库
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)

    # 从g变量中取出用户信息
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

    data = {
        # user有值，执行user.to_dict()；如果user没有值，将None给"user"
        "user": user.to_dict() if user else None,
        "news_dict_list": news_dict_list,
        "category_list": category_list
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


# get请求获取新闻列表,用 ？ 来传递参数
@index_blu.route('/news_list')
def news_list():
    """获取新闻列表"""
    # 1、获取参数：分类id，页数，每页新闻数
    cid = request.args.get('cid', '1')
    page = request.args.get('page', '1')
    per_page = request.args.get('per_page', '10')
    # 2、参数校验
    try:
        cid = int(cid)
        page = int(page)
        per_page = int(per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3、查询条件(不同种类新闻按照时间顺序排列，cid=1默认就是最新的新闻种类???)
    filters = []
    # 查询不是最新数据
    if cid != 1:
        # 添加条件
        filters.append(News.category_id == cid)
    # 按照创建时间降序排列,分页paginate
    try:
        paginate = News.query.filter(*filters).order_by(News.create_time.desc()).paginate(page, per_page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    news_list = paginate.items  # 模型对象列表
    total_page = paginate.pages  # 总页数
    current_page = paginate.page  # 当前页

    # 返回前端要用json格式
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())
    data = {
        "total_page": total_page,
        "current_page": current_page,
        "news_dict_list": news_dict_list
    }

    return jsonify(errno=RET.OK, errmsg="ok", data=data)
