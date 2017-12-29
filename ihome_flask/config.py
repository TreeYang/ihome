# coding=utf-8
import redis
class Config:
    DEBUG=False
    SQLALCHEMY_DATABASE_URI='mysql://root:mysql@127.0.0.1:3306/ihome'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
#PIL pillow
    #redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379

    #session配置
    SECRET_KEY = "iHome"
    #将session存储到redis中
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT)
    PERMANENT_SESSION_LIFETIME = 60*60*24*14#秒


class DevelopConfig(Config):
    DEBUG = True
class ProductConfig(Config):
    pass
