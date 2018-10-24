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
