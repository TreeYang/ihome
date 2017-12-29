# coding=utf-8
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


db=SQLAlchemy()

class BaseModel(object):
    create_time=db.Column(db.DATETIME,default=datetime.now())
    update_time=db.Column(db.DATETIME,default=datetime.now(),onupdate=datetime.now())

    def add_update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

class User(BaseModel, db.Model):
    __tablename__ = "ihome_user"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32),unique=True,nullable=False)
    password_hash=db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(11), unique=True, nullable=False)
    id_name = db.Column(db.String(32))
    id_card = db.Column(db.String(20), unique=True)
    avatar_url = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError("不可读")

    @password.setter
    def password(self, passwd):
        """设置密码加密"""
        self.password_hash = generate_password_hash(passwd)

    def check_password(self, passwd):
        """检查密码的正确性"""
        return check_password_hash(self.password_hash, passwd)

    def to_basic_dict(self):
        return {
            'id':self.id,
            'avator':self.avatar_url,
            'name':self.name,
            'phone':self.phone,
        }


