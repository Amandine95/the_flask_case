import time
from datetime import datetime

from flask import render_template, request, current_app, session, redirect, url_for, g

from info.models import User
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

    data = {
        "total_count": total_count,
        "mon_count": mon_count,
        "day_count": day_count
    }

    return render_template('admin/user_count.html', data=data)
