"""自定义公共工具类"""
import functools

# 定义前端模板的过滤器,定以后要添加到当前过滤器集
from flask import session, current_app, g

from info.models import User


def do_index_class(index):
    """定义过滤器"""
    if index == 0:
        return "first"
    elif index == 1:
        return "second"
    elif index == 2:
        return "third"
    return ""


# (项目多处需要查询用户数据)定义装饰器(闭包)装饰视图函数来进行用户信息查询。
# func 为被装饰函数 也就是 视图函数
def user_login_data(func):
    # functools.wraps装饰内层函数，能够使装饰器装饰的函数的__name__不变(flask中不同路由指向同一个函数报错)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """用户信息查询"""
        # 获取session数据
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            try:
                # 查询数据库
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        # 应用上下文，g变量 将user给g变量
        g.user = user
        # 调用被装饰函数,函数中能够取到 g 变量
        return func(*args, **kwargs)

    return wrapper
