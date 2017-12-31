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
from qiniu import put_data,Auth
from my_decorator import is_login

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

@is_login
@user_blueprint.route('/', methods=['GET'])
def user_my():
    # 获取当前登陆的用户
    user_id=session['user_id']
    # 档查当前用户的头像,用户名,手机号,并返回
    user=User.query.get(user_id)
    return jsonify(user=user.to_basic_dict())

@is_login
@user_blueprint.route('/', methods=['PUT'])
def user_profile():
    dict = request.form
    if 'avatar1' in dict:
        try:
        # 获取头像
            f1 = request.files['avatar']
            # mime-type:国际规范,表示文件的类型,如text/html,text/xml,image/png,image/jpeg..
            if not re.match('image/.*',f1.mimetype):
                return jsonify(code=RET.PARAMERR)
        except:
            return jsonify(code=RET.PARAMERR)
        # 上传到七牛云
        # 需要填写你的 Access Key 和 Secret Key
        access_key = '0mUz_taFmgf8MQFXNKfZ5oCIDbjMYAnN-yV0jlNt'
        secret_key = 'ZVRRJFhJmG_n3Hrjuxqz03g20AwyWntODDhZ0SHP'
        # 要上传的空间
        bucket_name = 'zhangshuyang'
        # 构建鉴权对象
        try:
            q = Auth(access_key, secret_key)

            # 生成上传 Token，可以指定过期时间等
            token = q.upload_token(bucket_name)
            # 要上传文件数据,ret是字典,键为hash,key,值为新文件名,info是response对象
            ret, info = put_data(token, None, f1.read())
        except:
            logging.ERROR("访问七牛云出错")
            return jsonify(code=RET.SERVERERR)
        # 如果未出错,保存用户的头像信息
        user = User.query.get(session['user_id'])
        user.avatar_url = ret.get('key')
        user.add_update()
        # 返回图片信息
        return jsonify(code=RET.OK, url=current_app.config['QINIU_URL'] + ret.get('key'))
    elif 'name' in dict:
        # 上传用户名
        name=dict.get('name')
        # 判断用户名是否存在
        if User.query.filter_by(name=name).count():
            return jsonify(code=RET.DATAEXIST)
        else:
            user=User.query.get(session['user_id'])
            user.name=name
            user.add_update()
            return jsonify(code=RET.OK)
    else:
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])

@is_login
@user_blueprint.route('/auth', methods=['GET'])
def user_auth():
    # 获取当前登陆用户的编号
    user_id=session['user_id']
    # 根据编号查询当前用户
    user=User.query.get(user_id)
    # 返回用户的真是姓名,身份证号
    return jsonify(user.to_auth_dict())

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

@is_login
@user_blueprint.route('/auth', methods=['PUT'])
def user_auth_set():
    # 接收参数
    dict = request.form
    id_name=dict.get('id_name')
    id_card=dict.get('id_card')
    # 验证参数有效性
    if not all([id_name,id_card]):
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])
    # 公安部证明姓名存在重复,所以不需要验证是否存在
    if not re.match(r'^[1-9]\d{5}(19|20)\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$',id_card):
        return jsonify(code=RET.PARAMERR, msg=ret_map[RET.PARAMERR])
    # 修改数据对象
    try:
        user = User.query.get(session['user_id'])
    except:
        logging.ERROR(u'查询用户失败')
        return jsonify(code=RET.DATAEXIST)
    try:
        user.id_name=id_name
        user.id_card=id_card
        user.add_update()
    except:
        logging.ERROR(u'修改用户姓名失败')
        return jsonify(code=RET.DBERR)
    # 返回数据
    return jsonify(code=RET.OK)


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