"""登录注册视图函数"""
from flask import request, abort, current_app, make_response

from info import redis_store, constants

from info.utils.captcha.captcha import captcha
from . import passport_blu


@passport_blu.route('/image_code')
def get_image_code():
    """
    获取图片验证码
    1、获取参数
    2、判断参数是否有值
    3、生成图片验证码
    4、保存图片验证码内容到redis
    5、返回验证码图片
    """
    # 取参数、args获取url里 ？ 后面的内容
    image_code_id = request.args.get("imageCodeId", None)
    # 判断是否有值
    if not image_code_id:
        # 抛出异常
        return abort(403)
    else:
        # 生成验证码，调用captcha模块的generate_captcha方法
        name, text, image = captcha.generate_captcha()
        # 保存图片验证码内容到redis
        try:
            redis_store.set("imageCodeId" + image_code_id, text, constants.IMAGE_CODE_REDIS_EXPIRES)
        except Exception as e:
            # 记录异常日志
            current_app.logger.error(e)
            abort(500)
        # 返回验证图片,修改content-type,使浏览器能够识别(解决css不能识别问题)
        response = make_response(image)
        response.headers["Content-Type"] = "image/jpg"
        return response
