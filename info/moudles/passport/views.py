"""登录注册视图函数"""
import random
import re

from flask import request, abort, current_app, make_response, json, jsonify

from info import redis_store, constants, db
from info.libs.yuntongxun.sms import CCP
from info.models import User

from info.utils.captcha.captcha import captcha
from info.utils.response_code import RET
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


@passport_blu.route('/sms_code')
def send_sms_code():
    """
    发送短信验证码
    0、获取参数(非表单提交，从request.data获取)
    1、判断参数是否为空、是否符合规则
    2、从redis读取图片内容及编号进行比对
    3、图码不符合返回提示信息
    4、图码符合--生成短信码内容、发送短信码、提示发送结果
    """
    # 测试、默认成功
    # print("调用")
    # return jsonify(errno=RET.OK, errmsg="发送成功")

    # 0、获取参数字典(手机号、图码内容、图码编号-所有参数以json格式传送)
    params_dict = json.loads(request.data)
    # params_dict = request.json
    print(params_dict)
    mobile = params_dict["mobile"]
    image_code = params_dict["image_code"]
    image_code_id = params_dict["image_code_id"]
    # 1、校验参数(有值、符合规则)
    # 是否有值
    if not all([mobile, image_code, image_code_id]):
        # {"xx:xx,yy:yy"}
        return jsonify(errno=RET.PARAMERR, errmsg="参数不能为空")
    # 手机号规则校验
    if not re.match('^1[35678]\\d{9}$', mobile):
        return jsonify(errno=RET.PARAMERR, errmsg="手机号不合法")
    # 2、从redis中读取保存的图码内容
    try:
        real_image_code = redis_store.get('ImageCodeId' + image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库查询错误")
    if not real_image_code:
        return jsonify(errno=RET.NODATA, errmsg="图片验证码已过期")
    # 与用户输入参数进行比对(这里为了避免大小写造成的影响，将参数和读取的结果都转换大写再比较)
    # 3、不符合，提示错误
    if real_image_code.upper() != image_code.upper():
        return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 4、符合则生成短信码(随机数,确保6位，不足0补)
    sms_code_str = "%06d" % random.randint(0, 999999)
    current_app.logger.debug("短信码内容是%s" % sms_code_str)
    # 发送,过期时间单位为分钟
    result = CCP().send_template_sms(mobile, [sms_code_str, constants.SMS_CODE_REDIS_EXPIRES / 60], "1")
    if result != 0:
        return jsonify(errno=RET.THIRDERR, errmsg="第三方发送失败")
    # 保存短信码在redis里
    try:
        # 验证码设置保存时间300s
        redis_store.set("sms" + mobile, sms_code_str, constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库保存失败")
    # 提示结果(之前需要保存短信码在redis)
    return jsonify(errno=RET.OK, errmsg="发送成功")


@passport_blu.route('/register', methods=["POST"])
def register():
    """
    注册
    1、获取参数(从表单获取)、并判断是否为空
    2、读取redis存储的验证码进行比对
    3、比对通过初始化user模型，并添加数据到数据库
    4、保持当前状态(session)
    5、返回注册结果
    6、注意：此时不需要图片验证码及手机号规则校验
    """
    # 1、获取参数
    params_dict = request.json
    mobile = params_dict.get('mobile')
    smscode = params_dict.get('smscode')
    password = params_dict.get('password')
    # 校验参数
    # 是否为空
    if not all([mobile, smscode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不能为空")
    # 2、获取redis存储
    try:
        real_sms_code = redis_store.get("sms" + mobile).decode('utf-8')
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据库读取失败")
    if not real_sms_code:
        return jsonify(errno=RET.NODATA, errmsg="手机号错误或验证码过期")
    if smscode != real_sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码输入错误")
    # 3、初始化user模型，赋值属性
    user = User()
    user.mobile = mobile
    # 手机号暂代昵称
    user.nick_name = mobile
    # 最后登陆时间
    from datetime import datetime
    user.last_login = datetime.now()
    # todo 密码加密
    # 添加数据到数据库
    try:
        db.Session.add(user)
        db.Session.commit()
    except Exception as e:
        current_app.logger.error(e)
        # 异常回滚
        db.Session.rollback()
        return jsonify(errno=RET.DBERR, errmsg="数据库写入失败")
    # 4、创建session用来保持状态(登录)
    from flask import session
    session["user_id"] = user.id
    session["mobile"] = user.mobile
    session["nick_name"] = user.nick_name
    # 5、返回成功响应
    return jsonify(errno=RET.OK, errmsg="注册成功")
