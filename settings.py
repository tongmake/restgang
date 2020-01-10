# coding=utf-8
__author__ = 'menghui'


# =====================================================================================================================
# 配置文件
DEBUG = True  # 是否开启调试模式

# =====================================================================================================================
# 日志处理占位
# 在httpclient中初始化
infoLogger = None
errorLogger = None
debugLogger = None

# =====================================================================================================================
# 配置数据库

SRVDATABASETYPE = "oracle"  # 数据查询服务数据库类型
DEFAULTRESTCONN = "stu"  # 数据查询服务数据库链接名称，为DATABASES中的KEY名称

# 数据库配置，key为数据库配置别名
DATABASES = {
    'default': {
        "TYPE":"oracle",
        'NAME': 'orcl',
        'USER': 'bjntu_er',
        'PASSWORD': '123456',
        'HOST': '127.0.0.1',
        'PORT': '1521'
    },
    'mdu': {
        "TYPE":"oracle",
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'orcl',
        'USER': 'mdu',
        'PASSWORD': 'mdu',
        'HOST': '127.0.0.1',
        'PORT': '1521'
    },
    'stu': {
        "TYPE":"oracle",
        'ENGINE': 'django.db.backends.oracle',
        'NAME': 'orcl',
        'USER': 'stu',
        'PASSWORD': 'stu',
        'HOST': '127.0.0.1',
        'PORT': '1521'
    }
}

# =====================================================================================================================
# 配置单点登录，以下配置没有使用
# 用户认证服务，当前没有使用
USERAUTHSERVICE = 'http://127.0.0.1:8090/wsGDPT/services/UserMgrService?wsdl'

# 单点登录地址，当前没有使用
CAS_SERVER_URL = 'http://127.0.0.1:8090/cas/login'

# 彻底登出，当前没有使用
CAS_LOGOUT_COMPLETELY = True

# 开启单点登出，当前没有使用
CAS_SINGLE_SIGN_OUT = True

# 自动创建新用户，当前没有使用
CAS_AUTO_CREATE_USERS = True

# =====================================================================================================================
# 关闭浏览器Session过期，未在IE中测试，以下配置没有使用
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# Session过期时间，单位秒
SESSION_COOKIE_AGE = 120

# =====================================================================================================================
# Redis服务器链接
# KEY规则：
#         CACHE_    缓存数据，由下面的CACHE_TABLES配置项定义
#         APPKEY_   应用系统注册信息，后跟应用系统ID，JSON格式
#                   {"privatekey": "3081c3020100300d06092a864886f70d01010105000481ae3081ab02010002210096f1842616ebce830
#                                   f34fa4a51cb1e6daffc5a12e5629deed96609c9dbc6bc15020301000102203951b7a41b3a2aaedc3c7a
#                                   fb73fa15306df6b150dc14884bd89d73ed2155cfb5021100d9fb8eaffa5e399f1ce82ad08619a13b0211
#                                   00b144ce4ff75b5eddb37ce8a5c65842ef021100a5f9ca0aaa9b864a65eb4d765b3536b30211008f2e9b
#                                   521de2b07a744a9503a9748b030210136419178fae85bcb0f54f93d5abb45c", "app_id": "ZNSHZH",
#                    "publickey":   "303c300d06092a864886f70d0101010500032b00302802210096f1842616ebce830f34fa4a51cb1e6da
#                                   ffc5a12e5629deed96609c9dbc6bc150203010001",
#                    "uname": "SYSUSER_ZNSHZH",
#                    "services": [8],
#                    "pwd": "UFdEX1pOU0haSA=="}
#         SRV_URL_    服务信息，后跟服务的URL，不同的服务类型保存的格式不同，JSON格式
#                   {   "secret": "N",
#                       "serviceid": 6,
#                       "enabled": 1,
#                       "msglog": "N",
#                       "type": 7,
#                       "serviceName": "testservice_5",
#                       "tableName": "CACHE_Buffer_stbprp_b_",
#                       "cachetype": "N",
#                       "innerjoin": null,
#                       "fieldlist": null,
#                       "url": "test_5",
#                       "schemaName": "redis"}
#        PC_        平台信息，JSON格式:
#                   {   "syspwd": "123456",
#                       "area": "重庆",
#                       "contacts": null,
#                       "platid": 5,
#                       "pluguel": null,
#                       "sysusername": "chongqing"}


REDISHOST = '127.0.0.1'
REDISPORT = "6379"
REDISDB = 0
RELOADREDISTIME = 10  # 重新加载redis中数据缓存的时间间隔，单位秒

# 缓存的数据库表
# [SQL,SCHEMA,[DBKEYS],PREKEY,[BUFFER DATA FIELD]]
CACHE_TABLES = [
    ['select STCD,STNM from su9921.st_stbprp_b', 'stu', ['STCD'], 'stu_st_stbprp_b', ['STNM']],
    ['select * from su9921.st_stbprp_b', 'stu', ['STCD'], 'Buffer_stbprp_b', []]
]

########################################################################################################################
MSGLOGPATH="/project/project/fangxunii/codes/clouds/restgang/cache/log"  #消息日志记录的根目录

HUGESQLPATH="/project/project/fangxunii/codes/clouds/restgang/hugesqls"

DEFAULTCACHETIME=60