from flask import render_template, g, redirect, request, jsonify, current_app

from info import db
from info.models import User
from info.utils.commmon import user_login_data
from info.utils.response_code import RET
from . import profile_blu


@profile_blu.route('/info')
@user_login_data
def user_info():
    """用户信息主界面"""
    user = g.user
    if not user:
        return redirect('/')

    data = {"user": user.to_dict()}
    return render_template('news/user.html', data=data)


@profile_blu.route('/base_info', methods=["POST", "GET"])
@user_login_data
def user_base_info():
    """基本信息"""
    user = g.user
    if not user:
        return redirect('/')

    # get请求渲染模板
    data = {
        "user": user.to_dict()
    }
    # 获取基本信息
    if request.method == "GET":
        return render_template('news/user_base_info.html', data=data)
    # post请求修改基本信息
    if request.method == "POST":
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')
        if not all([nick_name, signature, gender]):
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        if gender not in ['MAN', 'WOMAN']:
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        # 查询所有用户昵称,判断昵称不重复
        # user_list = User.query.all()
        # user_nick_names = [user.nick_name for user in user_list]
        # if nick_name in user_nick_names:
        #     return jsonify(errno=RET.PARAMERR, errmsg="昵称被使用")
        user.nick_name = nick_name
        user.signature = signature
        user.gender = gender
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=RET.DBERR, errmsg="数据库错误")
        # return render_template('news/user_base_info.html', data=data)
        return jsonify(errno=RET.OK, errmsg="操作成功")
