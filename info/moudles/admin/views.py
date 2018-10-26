import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, redirect, url_for, g, jsonify, abort

from info import constants, db
from info.models import User, News, Category
from info.moudles.admin import admin_blu

from info.utils.commmon import user_login_data

# 访问管理员主页要做权限校验
from info.utils.image_storage import storage
from info.utils.response_code import RET


@admin_blu.route('/index')
@user_login_data
def admin_index():
    """管理员主页"""
    user = g.user
    data = {
        "user": user.to_dict()
    }

    return render_template('admin/index.html', data=data)


@admin_blu.route('/login', methods=['POST', 'GET'])
def admin_login():
    """管理员登录"""
    if request.method == 'GET':
        # 登陆之前先判断是不是已经登录并且是不是管理员,已登录直接跳转管理员主页。
        user_id = session.get("user_id", None)
        is_admin = session.get("is_admin", False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))

        return render_template('admin/login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        if not all([username, password]):
            # 模板刷新
            return render_template('admin/login.html', errmsg="参数错误")
        try:
            # 查询数据库
            user = User.query.filter(User.mobile == username, User.is_admin == True).first()
        except Exception as e:
            current_app.logger.error(e)
            return render_template('admin/login.html', errmsg="数据库查询错误")
        if not user:
            return render_template('admin/login.html', errmsg="用户不存在")
        # 核对密码
        if not user.check_password(password):
            return render_template('admin/login.html', errmsg="密码错误")
        # 保存登录信息
        session["user_id"] = user.id
        session["mobile"] = user.mobile
        session["nick_name"] = user.nick_name
        session["is_admin"] = user.is_admin
        #  跳转主界面(前缀.函数名),执行其他视图函数
        return redirect(url_for('admin.admin_index'))


# 用户统计
@admin_blu.route('/user_count')
def user_count():
    """用户统计"""
    # 总人数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin == False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 月活跃(从本月1号0:0起)
    mon_count = 0
    # 当前时间(当年tm_year、当月tm_mon、当日tm_day、时、分、秒)
    t = time.localtime()
    # 月统计起始时间,返回一个时间对象
    mon_begin_time = datetime.strptime('%d-%02d-01' % (t.tm_year, t.tm_mon), '%Y-%m-%d')
    try:
        # 创建时间大于本月初
        mon_count = User.query.filter(User.is_admin == False, User.create_time > mon_begin_time).count()
    except Exception as e:
        current_app.logger.error(e)
    # 日活跃(从当天0点起)
    day_count = 0
    day_begin_time = datetime.strptime('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday), '%Y-%m-%d')
    try:
        mon_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_time).count()
    except Exception as e:
        current_app.logger.error(e)
    # 活跃曲线数据(从当天向前推30天,最后登陆时间在每天00:00到次日00:00)
    # 日期: today-1 today-2 today-3...
    active_count = []
    active_time = []
    # 当天时间对象
    today_date = datetime.strptime(('%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)), "%Y-%m-%d")
    for i in range(0, 31):
        # 开始时间
        begin_date = today_date - timedelta(days=i)
        # 结束时间
        end_date = today_date - timedelta(days=i - 1)
        count = User.query.filter(User.is_admin == False, User.last_login >= begin_date,
                                  User.last_login < end_date).count()
        active_count.append(count)
        active_time.append(begin_date.strftime("%Y-%m-%d"))
    # 反转
    active_time.reverse()
    active_count.reverse()
    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count,
        "active_count": active_count,
        "active_time": active_time
    }

    return render_template('admin/user_count.html', data=data)


# 用户列表
@admin_blu.route('/user_list')
def user_list():
    """用户列表"""
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1
    users_list = []
    current_page = 1
    total_page = 1
    try:
        paginate = User.query.filter(User.is_admin == False).paginate(page, constants.ADMIN_USER_PAGE_MAX_COUNT, False)
        users_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
    user_dict_list = []
    for user in users_list:
        user_dict_list.append(user.to_admin_dict())
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "user_dict_list": user_dict_list
    }

    return render_template('admin/user_list.html', data=data)


# 新闻审核
@admin_blu.route('/review_list')
def review_list():
    """新闻审核列表"""
    page = request.args.get("page", 1)
    # 关键字搜索功能
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_review_list = []
    current_page = 1
    total_page = 1
    # 查询条件过滤器列表(可以将多个条件放里面)
    filters = [News.status != 0]
    if keywords:
        # 新闻标题包含关键词
        filters.append(News.title.contains(keywords))
    try:
        # status == 0  审核通过      对查询条件过滤器解包
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_review_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_review_list:
        news_dict_list.append(news.to_review_dict())

    data = {"total_page": total_page, "current_page": current_page, "news_dict_list": news_dict_list}

    return render_template('admin/news_review.html', data=data)


@admin_blu.route('/news_review_detail/<int:news_id>')
def news_review_detail(news_id):
    """新闻审核详情"""
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    if not news:
        return render_template('admin/news_review_detail.html', data={"errmsg": "没有这条新闻"})
    data = {
        "news": news.to_dict()
    }
    return render_template('admin/news_review_detail.html', data=data)


@admin_blu.route('/news_review_action', methods=["POST"])
def news_review_action():
    """新闻审核操作"""
    news_id = request.json.get('news_id')
    action = request.json.get('action')
    if not all([news_id, action]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news_id = int(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not news:
        return jsonify(errno=RET.NODATA, errmsg="没有这条新闻")
    if action == "accept":
        news.status = 0
    else:
        reason = request.json.get('reason')
        if not reason:
            return jsonify(errno=RET.PARAMERR, errmsg="请输入拒绝原因")
        news.reason = reason
        news.status = -1
    return jsonify(errno=RET.OK, errmsg="ok")


@admin_blu.route('/news_edit')
def news_edit():
    """新闻版式编辑"""
    page = request.args.get("page", 1)
    # 关键字搜索功能
    keywords = request.args.get("keywords", None)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_review_list = []
    current_page = 1
    total_page = 1
    # 新闻版式编辑查询的是审核通过的新闻
    filters = [News.status == 0]
    if keywords:
        # 新闻标题包含关键词
        filters.append(News.title.contains(keywords))
    try:
        # status == 0  审核通过      对查询条件过滤器解包
        paginate = News.query.filter(*filters) \
            .order_by(News.create_time.desc()) \
            .paginate(page, constants.ADMIN_NEWS_PAGE_MAX_COUNT, False)

        news_review_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_review_list:
        news_dict_list.append(news.to_basic_dict())

    data = {"total_page": total_page, "current_page": current_page, "news_dict_list": news_dict_list}

    return render_template('admin/news_edit.html', data=data)


@admin_blu.route('/news_edit_detail', methods=["POST", "GET"])
def news_edit_detail():
    """新闻编辑详情"""
    # get请求获取新闻编辑详情页内容
    if request.method == "GET":
        news_id = request.args.get('news_id')
        if not news_id:
            abort(404)
        try:
            news_id = int(news_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
        if not news:
            return render_template('admin/news_edit_detail.html', data={"errmsg": "没有这条新闻"})
        # 新文编辑详情页和审核详情页区别：多出分类选项
        categories = []
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        category_dict_list = []
        for category in categories:
            # category_dict = category.to_dict()
            # 增加判断字段,前端根据字段来显示指定分类
            if category.news_id == news.id:
                category["is_selected"] = True
            # 移除最新分类
            if category.id != 1:
                category_dict_list.append(category.to_dict())
        data = {
            "news": news.to_dict(),
            "category_dict_list": category_dict_list
        }
        return render_template('admin/news_edit_detail.html', data=data)
    # post请求提交编辑后的内容
    else:
        news_id = request.form.get("news_id")
        title = request.form.get("title")
        digest = request.form.get("digest")
        content = request.form.get("content")
        index_image = request.files.get("index_image")
        category_id = request.form.get("category_id")
        # 1.1 判断数据是否有值
        if not all([title, digest, content, category_id]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

        news = None
        try:
            news = News.query.get(news_id)
        except Exception as e:
            current_app.logger.error(e)
        if not news:
            return jsonify(errno=RET.NODATA, errmsg="未查询到新闻数据")

        # 1.2 尝试读取图片
        if index_image:
            try:
                index_image = index_image.read()
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

            # 2. 将标题图片上传到七牛
            try:
                key = storage(index_image)
            except Exception as e:
                current_app.logger.error(e)
                return jsonify(errno=RET.THIRDERR, errmsg="上传图片错误")
            news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
        # 3. 设置相关数据
        news.title = title
        news.digest = digest
        news.content = content
        news.category_id = category_id

        return jsonify(errno=RET.OK, errmsg="编辑成功")


@admin_blu.route('/news_category')
def news_category():
    """新闻分类编辑"""
    try:
        categories = Category.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not categories:
        return jsonify(errno=RET.NODATA, errmsg="分类信息为空")
    category_dict_list = []
    for category in categories:
        if category.id != 1:
            category_dict_list.append(category.to_dict())

    data = {
        "category_dict_list": category_dict_list
    }
    return render_template('admin/news_type.html', data=data)


# 分类操作传递参数：修改(当前id,name)、新增(name)
@admin_blu.route('/category_operate', methods="POST")
def category_operate():
    """新闻分类的操作"""
    category_id = request.json.get('category_id')
    category_name = request.json.get('category_name')
    # 修改当前id对应的name
    if category_id:
        try:
            category = Category.query.get(category_id)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
        if not category:
            return jsonify(errno=RET.NODATA, errmsg="没有这个分类")
        category.name = category_name
        return jsonify(errno=RET.OK, errmsg="修改成功")
    # 新增分类
    else:
        if not category_name:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        categories = Category.query.all()
        if category_name in categories.name:
            return jsonify(errno=RET.PARAMERR, errmsg="分类重复")
        # 新建分类对象
        category = Category()
        category.name = category_name
        try:
            db.session.add(category)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
        return jsonify(errno=RET.OK, errmsg="新增成功")
