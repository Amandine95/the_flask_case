"""创建蓝图"""
from flask import Blueprint, session, redirect, request, url_for

# 创建蓝图
admin_blu = Blueprint('admin', __name__)

# 当前目录导入views
from . import views


# 请求钩子函数根据作用范围来确定写在什么地方，作用于全局的可以写在info下的文件，
# 这里的请求钩子只作用于管理员模块因此就写在admin文件夹下
# 创建钩子函数，管理员模块的每次请求前进行权限校验
# admin_blu 装饰的路由都会调用这个方法(bug:清空cookie后访问管理员登录页失败)
@admin_blu.before_request
def check_admin():
    """管理员权限校验"""
    is_admin = session.get('is_admin', False)
    # 不是管理员 并且 访问的不是管理员登录页，跳转首页 not is_admin 为 true 才会执行
    # if not is_admin and not request.url.endswith('/admin/login'):
    if not is_admin and not request.url.endswith(url_for('admin.admin_login')):
        return redirect('/')
