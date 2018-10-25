import time
from datetime import datetime, timedelta

from flask import render_template, request, current_app, session, redirect, url_for, g

from info import constants
from info.models import User, News
from info.moudles.admin import admin_blu

from info.utils.commmon import user_login_data


# 访问管理员主页要做权限校验
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
        #  跳转主界面(前缀.函数名)
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
    """新闻审核"""
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = 1

    news_review_list = []
    current_page = 1
    total_page = 1

    try:
        # status == 0  审核通过
        paginate = News.query.filter(News.status != 0) \
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

