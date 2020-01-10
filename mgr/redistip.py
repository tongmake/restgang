__author__ = 'menghui'
import tornado.escape
import redis
import settings
import json
import datetime
import decimal
import string


# ######################################################################################################################
def getRedis():
    return redis.Redis(host=settings.REDISHOST, port=settings.REDISPORT, db=settings.REDISDB)


GLOBAREDIS = getRedis()


# ######################################################################################################################
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        elif isinstance(obj, map):
            return json.JSONEncoder.default(self, list(obj))
        else:
            return json.JSONEncoder.default(self, obj)


# ######################################################################################################################
def putSrv2redis(srv, r=None, keys=[]):
    content = json.dumps(srv, cls=DateTimeEncoder).replace("</", "<\\/")
    key = srv["serviceid"]
    if r is None:
        r = GLOBAREDIS
    if ("SRV_ID_" + str(key)).encode(encoding="utf-8") in keys:
        keys.remove(("SRV_ID_" + str(key)).encode(encoding="utf-8"))
    if ("SRV_URL_" + str(srv['url'])).encode(encoding="utf-8") in keys:
        keys.remove(("SRV_URL_" + str(srv['url'])).encode(encoding="utf-8"))
    r.set("SRV_ID_" + str(key), content)
    r.set("SRV_URL_" + str(srv['url']), content)


# ######################################################################################################################
def put2redis(key, data, r=None):
    if r is None:
        r = GLOBAREDIS
    content = json.dumps(data, cls=DateTimeEncoder).replace("</", "<\\/")
    r.set(key, content)


def putStr2redis(key, data, r=None):
    if r is None:
        r = GLOBAREDIS
    r.set(key, json.dumps(data).replace('"', ""))


def getStrfromRedis(key, r=None):
    if r is None:
        r = GLOBAREDIS
    s = r.get(key)
    if s is None:
        return None
    if s is string:
        bytes(s, 'utf-8').decode('raw_unicode_escape')
    else:
        return s.decode('raw_unicode_escape')


# ######################################################################################################################
def getfromRedis(key, r=None):
    if r is None:
        r = GLOBAREDIS
    d = r.get(key)
    if d is None:
        return None
    return tornado.escape.json_decode(d)


# ######################################################################################################################
def getKeys(p, r=None):
    if r is None:
        r = GLOBAREDIS
    return r.keys(p)
