from flask import render_template, g, redirect, request, jsonify, current_app, session

from info import db, constants
from info.models import User, Category
from info.utils.commmon import user_login_data
from info.utils.image_storage import storage
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
        # 实时更新session数据
        session['nick_name'] = nick_name
        return jsonify(errno=RET.OK, errmsg="操作成功")


@profile_blu.route('/user_pic', methods=["POST", "GET"])
@user_login_data
def user_pic():
    """用户头像设置"""
    user = g.user
    if not user:
        return redirect('/')
    # get请求显示默认头像
    if request.method == "GET":
        data = {
            "user": user.to_dict()

        }

        return render_template('news/user_pic_info.html', data=data)
    # post请求设置头像
    if request.method == "POST":
        try:
            avatar = request.files.get('avatar').read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
        # 七牛云存储图片
        try:
            # 封装的七牛云模块
            key = storage(avatar)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno=RET.THIRDERR, errmsg="头像上传失败")
        # 保存头像地址
        user.avatar_url = key
        return jsonify(errno=RET.OK, errmsg="上传成功", data={"avatar_url": constants.QINIU_DOMIN_PREFIX + key})


@profile_blu.route('/user_password', methods=['POST', 'GET'])
@user_login_data
def user_pass():
    """用户密码修改"""
    user = g.user
    if not user:
        return redirect('/')
    if request.method == 'GET':
        return render_template('news/user_pass_info.html')
    old_password = request.json.get('old_password')
    new_password = request.json.get('new_password')
    if not all([old_password, new_password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 判断旧密码是否正确(check_password密码校验)
    if not user.check_password(old_password):
        return jsonify(errno=RET.PARAMERR, errmsg="旧密码输入错误")
    # 修改模型，保存(新密码确认在前端表单校验)
    user.password = new_password
    return jsonify(errno=RET.OK, errmsg="修改成功")


@profile_blu.route('/user_collection')
@user_login_data
def user_collection():
    """用户收藏"""
    user = g.user
    if not user:
        return redirect('/')
    # get请求，？后携带参数 页数 默认为1
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 获取数据库模型paginate  三个参数  page  per_page  error_out=true/false
    paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
    current_page = paginate.page
    total_page = paginate.pages
    # 模型对象列表
    news_list = paginate.items
    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_dict())
    data = {
        "current_page": current_page,
        "total_page": total_page,
        "news_dict_list": news_dict_list
    }
    return render_template('news/user_collection.html', data=data)


# 发布新闻请求方式2种，get用在获取新闻分类
@profile_blu.route('/news_release', methods=['POST', 'GET'])
@user_login_data
def news_release():
    """新闻发布"""
    user = g.user
    if not user:
        return redirect('/')
    # 获取分类模型列表
    categories = []
    categories_dict_list = []

    if request.method == 'GET':
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)

        for category in categories:
            # 除去最新分类
            if category.id != 1:
                categories_dict_list.append(category.to_dict())
        data = {
            "categories_dict_list": categories_dict_list
        }
        return render_template('news/user_news_release.html', data=data)







