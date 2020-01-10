import os
import tornado.escape
import settings
import hashlib
import json
import mgr.redistip as redis

import base64


def getResultFromCache(rh):
    key = rh._Srv["url"] + "\t" + "\t".join(
        [x + "=" + rh.get_argument(x) for x in sorted(rh.request.arguments)])
    key = str(base64.b64encode(bytes(key, encoding="utf8")), encoding="utf-8")
    return redis.GLOBAREDIS.get(key)


def write2Cache(rh, response):
    if rh._Srv["cachetype"] == "N":
       return
    key = rh._Srv["url"] + "\t" + "\t".join(
        [x + "=" + rh.get_argument(x) for x in sorted(rh.request.arguments)])
    key = str(base64.b64encode(bytes(key, encoding="utf8")), encoding="utf-8")
    if settings.DEBUG:
        settings.debugLogger.debug("create cache[" + key + "]:")
        print(key)
    redis.GLOBAREDIS.set(key, response, ex=settings.DEFAULTCACHETIME)


def wirteMsg2file(msg, srv, filename, request=None):
    m2 = hashlib.md5()
    m2.update(bytes(srv["url"], encoding="utf-8"))
    dirname = m2.hexdigest()
    pathname = settings.MSGLOGPATH + os.sep + dirname
    if not (os.path.exists(pathname)):
        try:
            os.makedirs(pathname)
        except Exception as e:
            settings.errorLogger.error('创建缓存目录报错，' + pathname)
            settings.errorLogger.error(e)
            return
    try:
        file = open(pathname + os.sep + filename, 'w')
        try:
            if not (request is None):
                file.write(json.dumps(request, cls=redis.DateTimeEncoder, ensure_ascii=False))
            if "msglog" in srv:
                if srv["msglog"] != "N":
                    file.write("\n====respone====\n")
                    file.write(msg)
        finally:
            file.close()

    except OSError as oserror:
        settings.errorLogger.error('创建缓存文件报错，' + pathname + os.sep + filename)
        settings.errorLogger.error(oserror)
