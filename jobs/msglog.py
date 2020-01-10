import os
import tornado.escape
import settings
import hashlib
import json
import mgr.redistip as redis
import pickle
import mgr.dbtip as dbtip
import time
import datetime

def wirteMsg(msg, srv, filename, request=None):
    wirteMsg2redis(msg, srv, filename, request)


def msgLog2DB():
    def insertLog(conn):
        sql = "insert into USERVICE_LOG (ID,CLIENTID,TIME,SPTIME,PARAMS,RESPONSE,SRV,SRVURL,RESPONSESIZE,DBTIME) " \
              "values (USERVICE_MSGLOG_ID.nextval,:CLIENTID,:TIME,:SPTIME,:PARAMS,:RESPONSE,:SRV,:SRVURL,:RESPONSESIZE,:DBTIME)"
        param = {
            "CLIENTID": jso["CLIENTID"],
            "TIME": datetime.datetime.strptime(jso["TIME"], "%Y-%m-%d %H:%M:%S"),
            "SPTIME": jso["SPTIME"],
            'PARAMS': json.dumps(jso["PARAMS"], cls=redis.DateTimeEncoder, ensure_ascii=False),
            "SRV": json.dumps(jso["SRV"], cls=redis.DateTimeEncoder, ensure_ascii=False),
            "SRVURL": jso["SRVURL"],
            "RESPONSE": "",
            "RESPONSESIZE": jso["RESPONSESIZE"],
            "DBTIME": jso["DBTIME"]
        }
        cur = conn.cursor()
        cur.execute(sql, param)
        conn.commit()

    while True:
        msglog = redis.GLOBAREDIS.brpop("USERVICE_MSHLOG")
        jso = tornado.escape.json_decode(msglog[1])
        dbtip.executeSQL(insertLog)
        time.sleep(0.01)



def wirteMsg2DB(msg, srv, filename, request=None):
    def insertLog(conn):
        sql = "insert into USERVICE_LOG (ID,CLIENTID,TIME,SPTIME,PARAMS,RESPONSE,SRV,SRVURL,RESPONSESIZE,DBTIME) " \
              "values (USERVICE_MSGLOG_ID.nextval,:CLIENTID,:TIME,:SPTIME,:PARAMS,:RESPONSE,:SRV,:SRVURL,:RESPONSESIZE,:DBTIME)"
        param = {
            "CLIENTID": request["clientid"],
            "TIME": request["time"],
            "SPTIME": request["sptime"],
            'PARAMS': json.dumps(request["params"], cls=redis.DateTimeEncoder, ensure_ascii=False),
            "SRV": json.dumps(srv, cls=redis.DateTimeEncoder, ensure_ascii=False),
            "SRVURL": srv["url"],
            "RESPONSE": "",
            "RESPONSESIZE": len(msg),
            "DBTIME": request["spdbtime"]
        }
        cur = conn.cursor()
        cur.execute(sql, param)
        conn.commit()

    dbtip.executeSQL(insertLog)


def wirteMsg2redis(msg, srv, filename, request=None):
    param = {
        "CLIENTID": request["clientid"],
        "TIME": request["time"],
        "SPTIME": request["sptime"],
        'PARAMS': json.dumps(request["params"], cls=redis.DateTimeEncoder, ensure_ascii=False),
        "SRV": json.dumps(srv, cls=redis.DateTimeEncoder, ensure_ascii=False),
        "SRVURL": srv["url"],
        "RESPONSE": "",
        "RESPONSESIZE": len(msg),
        "DBTIME": request["spdbtime"]
    }
    redis.GLOBAREDIS.lpush("USERVICE_MSHLOG", json.dumps(param, cls=redis.DateTimeEncoder, ensure_ascii=False))


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
