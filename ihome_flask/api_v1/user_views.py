# coding=utf-8
from flask import Blueprint,session,make_response,jsonify, request,current_app
user_blueprint=Blueprint('user', __name__)

from captcha.captcha import captcha
from ytx_sdk.ytx_send import sendTemplateSMS
from status_code import *
import re
from models import User
import random
import logging
from qiniu import put_file,Auth


@user_blueprint.route('/yzm')
def yzm():
    name,text,image=captcha.generate_captcha()
    session['image_yzm']=text
    response=make_response(image)
    response.headers['Content-Type']='image/jpeg'
    return response

@user_blueprint.route('/send_sms')
def send_sms():
    # 接收请求的数据
    dict = request.args
    mobile = dict.get('mobile')
    imageCode = dict.get('imageCode')
    # 手机号
    # 验证码
    # 验证图片码
    # 验证参数是否存在
    if not all([mobile, imageCode]):
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])
    # 验证手机号格式
    if not re.match(r'^1[34578]\d{9}$', mobile):
        return jsonify(code=RET.PARAMERR, msg=u'手机号格式有误')
    # 验证手机号是否存在
    if User.query.filter_by(phone=mobile).count():
        return jsonify(code=RET.PARAMERR, msg=u'手机号存在')
    # 验证图片验证码
    if imageCode != session['image_yzm']:
        return jsonify(code=RET.PARAMERR, msg=u'图片验证码错误')
    # 调用云通讯函数进行发送短信
    sms_code=random.randint(1000, 9999)
    session['sms_yzm'] = sms_code
    print(sms_code)
    result="0 0 0 0 0 0"
    # 根据云通讯返回的结果进行响应
    if result=='0 0 0 0 0 0':
        return jsonify(code=RET.OK, msg=ret_map[RET.OK])
    else:
        return jsonify(code=RET.UNKOWNERR, msg=u'信息发送失败')

@user_blueprint.route('/',methods=['POST'])
def user_register():
    # 接收参数
    dict = request.form
    mobile=dict.get('mobile')
    imagecode=dict.get('imagecode')
    phonecode=dict.get('phonecode')
    password=dict.get("password")
    password2=dict.get('password2')
    # 验证参数是否存在
    if not all([mobile, imagecode, phonecode, password, password2]):
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])
    if imagecode != session['image_yzm']:
        return jsonify(code=RET.PARAMERR, msg=u'图片验证码错误' )
    if int(phonecode) != session['sms_yzm']:
        return jsonify(code=RET.PARAMERR, msg=u'短信验证码错误')
    if not re.match(r'^1[34578]\d{9}$', mobile):
        return jsonify(code=RET.PARAMERR, msg=u'手机号格式有误')
    if User.query.filter_by(phone=mobile).count():
        return jsonify(code=RET.PARAMERR, msg=u'手机号存在')
    # 验证参数
    # 保存用户对象
    user=User()
    user.phone=mobile
    user.name=mobile
    user.password=password
    try:
        user.add_update()
        return jsonify(code=RET.OK, msg=ret_map[RET.OK])
    except:
        logging.ERROR(u'用户注册更新数据库失败,手机号:%s,密码:%s' % (mobile,password))
        return jsonify(code=RET.DBERR, msg=ret_map[RET.DBERR])

@user_blueprint.route('/', methods=['GET'])
def user_my():
    # 获取当前登陆的用户
    user_id=session['user_id']
    # 档查当前用户的头像,用户名,手机号,并返回
    user=User.query.get(user_id)
    return jsonify(user=user.to_basic_dict())

@user_blueprint.route('/', methods=['PUT'])
def user_profile():
    dict = request.form
    if 'avatar1' in dict:
        try:
        # 获取头像
            f1 = request.files['avatar_url']
            # if not re.match('image/.*',f1.mimetype):
            #     return jsonify(code=RET.PARAMERR)
        except:
            return jsonify(code=RET.PARAMERR)
        # 上传到七牛云
        # 需要填写你的 Access Key 和 Secret Key
        access_key = '0mUz_taFmgf8MQFXNKfZ5oCIDbjMYAnN-yV0jlNt'
        secret_key = 'ZVRRJFhJmG_n3Hrjuxqz03g20AwyWntODDhZ0SHP'
        # 构建鉴权对象
        try:
            q = Auth(access_key, secret_key)
            # 要上传的空间
            bucket_name = 'zhangshuyang'
            # 生成上传 Token，可以指定过期时间等
            token = q.upload_token(bucket_name)
            # 要上传文件数据,ret是字典,键为hash,key,值为新文件名,info是response对象
            ret, info = put_file(token, None, f1.read())
        except:
            logging.ERROR("访问七牛云出错")
            return jsonify(code=RET.SERVERERR)
        # 如果未出错,保存用户的头像信息
        user = User.query.get(session['user_id'])
        user.avatar_url = ret.get('key')
        user.add_update()
        # 返回图片信息
        return jsonify(code=RET.OK,url=current_app.config['QINIU_URL'] + ret.get('key'))
    elif 'name' in dict:
        # 上传用户名
        pass
    else:
        pass

@user_blueprint.route('/session', methods=['POST'])
def user_login():
    # 接收参数
    dict = request.form
    mobile=dict.get('mobile')
    password=dict.get('password')
    # 验证非空
    if not all([mobile,password]):
        return jsonify(code=RET.PARAMERR, )
    # 验证手机号是否格式正确
    if not re.match(r"^1[34578]\d{9}", mobile):
        return jsonify(code=RET.PARAMERR, msg=u'手机格式错误')
    # 数据处理
    try:
        user=User.query.filter_by(phone=mobile).first()
    except:
        logging.ERROR('用户登陆--数据库出错')
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])

    # 判断手机号是否存在
    if user:
        # 判断密码是否正确
        if user.check_password(password):
            session['user_id'] = user.id
            return jsonify(code=RET.OK, msg=u'ok')
        else:
            return jsonify(code=RET.PARAMERR, msg=u'密码不正确')
    else:
        return jsonify(code=RET.PARAMERR, msg=u'手机号不存在')

@user_blueprint.route('/session', methods=['GET'])
def user_is_login():
    if 'user_id' in session:
        user=User.query.filter_by(id=session['user_id']).first()
        return jsonify(code=RET.OK, name=user.name)
    else:
        return jsonify(code=RET.PARAMERR)

@user_blueprint.route('/session', methods=['DELETE'])
def user_logout():
    # del session['user_id']
    session.clear()
    return jsonify(code=RET.OK)