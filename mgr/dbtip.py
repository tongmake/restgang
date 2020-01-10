__author__ = 'menghui'
# coding=utf-8
import settings
import cx_Oracle
import pymssql
import mgr.redistip as redistip
from DBUtils.PooledDB import PooledDB

__pool = {}  # 连接池对象


def isFunction(f):
    """
        判断是否为函数
    :param f:
    :return:
    """
    return hasattr(f, '__call__')


def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    fields=[]
    for des in desc:
        if des[0]!="_RN" and des[0]!="_tempCol":
            fields.append(des)
    return [
        dict(zip([col[0] for col in fields], row))
        for row in cursor.fetchall()
        ]


def __getConnectcfg(dbid=None):
    """
    返回指定的数据库链接
    :param dbid:
    :return:
    """
    # if dbid is None:
    #    dbid = "default"

    dbcfg = settings.DATABASES[dbid]
    if dbcfg is None:
        d = redistip.getfromRedis("P_AT_DATASOURCE_%s" % dbid)
        if d is None:
            dbcfg = settings.DATABASES[settings.DEFAULTRESTCONN]
        else:
            settings.DATABASES[dbid] = d
            dbcfg = settings.DATABASES[dbid]

    # con = cx_Oracle.connect("".join([dbcfg["USER"], '/', dbcfg["PASSWORD"], '@', dbcfg['HOST'], '/', dbcfg["NAME"]]))
    return dbcfg

def getDBType(dbid=None):
    if dbid is None:
        return "oracle"
    dbcfg = __getConnectcfg(dbid)
    return dbcfg["TYPE"]

def getConnect(dbid=None):
    if dbid is None:
        dbid = "default"
    dbcfg = __getConnectcfg(dbid)
    if dbid in __pool:
        return __pool[dbid].connection()
    else:
        if dbcfg["TYPE"]=="oracle":
            dbp = PooledDB(cx_Oracle,
                           user=dbcfg["USER"],
                           password=dbcfg["PASSWORD"],
                           dsn="%s:%s/%s" % (dbcfg['HOST'], 1521, dbcfg["NAME"]),
                           mincached=5,
                           maxcached=20)
            __pool[dbid] = dbp
        if dbcfg["TYPE"]=="mssql":
            args = (0, 0, 0, 5, 0, 0, None)
            conn_kwargs = {"host": dbcfg["HOST"] , "user": dbcfg["USER"], "password": dbcfg["PASSWORD"],"database": dbcfg["NAME"],"charset":"GBK"}
            dbp=PooledDB(pymssql, *args, **conn_kwargs)
            __pool[dbid] = dbp
        return __pool[dbid].connection()


def executeSQL(executeFuc, dbid=None):
    """
    执行SQL语句，执行后调用 executeFuc
    :param executeFuc: 执行后调用的函数句柄
    :param dbid:
    :return:
    """
    if executeFuc is None:
        return
    if not isFunction(executeFuc):
        return
    con = getConnect(dbid)
    res = None
    try:
        res = executeFuc(con)
    finally:
        con.close()
    return res


def querySQL2map(sql, param=None, dbid=None):
    """
    执行SQL语句返回序列，每个记录为一个dict
    :param sql:
    :param dbid:
    :return:
    """
    conn = getConnect(dbid)

    cur = None
    result = None
    try:
        cur = conn.cursor()
        if param is None:
            cur.execute(sql)
        else:
            cur.execute(sql, param)
        desc = cur.description
        result = [
            dict(zip([col[0] for col in desc], row))
            for row in cur.fetchall()
            ]
    finally:
        if not (cur is None):
            cur.close()
        conn.close()
    return result


def querySQL(sql, callBack, param=None, dbid=None):
    """
    执行SQL语句，成功后调用callBack
    :param sql:
    :param callBack:
    :param dbid:
    :return:
    """
    conn = getConnect(dbid)
    cur = None
    if not isFunction(callBack):
        return
    try:
        cur = conn.cursor()
        if param is None:
            cur.execute(sql)
        else:
            cur.execute(sql, param)
        callBack(cur)
    finally:
        if not (cur is None):
            cur.close()
        conn.close()
