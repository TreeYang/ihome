# coding=utf-8
from flask import Blueprint, jsonify, current_app
house_blueprint=Blueprint('house', __name__)

from models import Area,Facility
import json


@house_blueprint.route('/area_facility', methods=["GET"])
def newhouse():
    # 查询地址
    area_dict_list = current_app.redis.get("area_list")
    if not area_dict_list:
        area_list=Area.query.all()
        area_dict_list=[area.to_dict() for area in area_list]
        current_app.redis.set("area_list", json.dumps(area_dict_list))
    else:
        # 存储到REdis后被转换为字符串,所以取出来后需要转换
        area_dict_list=json.loads(area_dict_list)

    # 查询设施
    facility_dict_list = current_app.redis.get("facility_list")
    if not facility_dict_list:
        facility_list = Facility.query.all()
        facility_dict_list=[facility.to_dict() for facility in facility_list]
        current_app.redis.set("facility_list", json.dumps(facility_dict_list))
    else:
        facility_dict_list=json.loads(facility_dict_list)
    # 构造结果并返回
    return jsonify(area=area_dict_list, facility=facility_dict_list)