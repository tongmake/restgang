__author__ = 'menghui'
# coding=utf-8
import mgr.redistip as redis
import settings
from datetime import *

import json
from sql import sqlGenerator
from sql import sqlParse
import mgr.dbtip as dbtip


def addinnerjoin(row, name, prekey, buffer):
    """
    添加一个InnerJoin节点，与innerjoinfromcache方法配合使用
    :param row:
    :param name:
    :param prekey:
    :param buffer:
    :return:
    """
    k = u"%s%s" % (prekey[0], row[prekey[1]])
    value = buffer.get(k, None)
    if value == None:
        value = redis.getStrfromRedis(k)
        buffer[k] = value
    row[name] = value
    return row


def innerjoinfromcache(innerjoin, data):
    """
    从redis中返回缓存的数据做表链接
    :param innerjoin:
    :param data:
    :return:
    """
    buffer = {}
    # _CACHE:stnm on CHCHE_stu_st_stbprp_b_:stcd

    cmd = innerjoin[7:].split()
    if cmd[1] == 'on':
        name = cmd[0]  # 添加到data的字段名
        prekey = cmd[2].split(':')  # [0] key前缀，[1] 字段名
        return [
            addinnerjoin(row, name, prekey, buffer)
            for row in data
            ]


def sqlService(srv, params):
    """
    处理SQL服务,下面的程序没有检测传入参数的类型，错误的参数传入有可能出发500系统异常
    :param srv:
    :return:
    """

    starttime = (datetime.now())

    p = params

    sql = srv["sql"]

    #####################################################################
    # 根据传入的参数处理SQL语句
    try:
        sql = sqlGenerator.parseTrim(sql, p['pks'])
    except sqlGenerator.SQLExpParseError as e:
        return {"errormsg": u"SQL语句非法:" + e.msg}

        #####################################################################
        # 处理SQL中的站位符
    phNames = sqlGenerator.findplaceholder(sql)
    if phNames != None:
        for item in phNames:
            if item in p['pks']:
                sql = sql.replace("$" + item, p['pks'][item])
    #####################################################################
    if settings.DEBUG:
        settings.debugLogger.debug("pager sql:" + sql)
    if p['sql'] == "true":
        return {"result": sql,"spdbtime": 0,
            "sptime": 0}
    if not sqlParse.availableSQL(sql):
        # 非法SQL语句
        return {"errormsg": u"SQL语句非法:" + sql}

    if p['pagesize'] == 0 and p['limit'] == 0:
        p["limit"] = 10000
    if p["limit"] > 10000:
        p["limit"] = 10000
    ds = srv["datasource"]
    if ds is None:
        ds = settings.DEFAULTRESTCONN

    builder = sqlGenerator.SelectPagerBuilder(None, p['pagesize'], p['pageindex'], p['limit'], sql=sql,dbtype=dbtip.getDBType(ds))
    sql = builder.buildSQL().getSQL()


    #####################################################################
    # 因为处理后的SQL中的参数有可能和传入的不同
    # 因此下面的程序必须对传入的参数进行修改，删除那些在SQL中不存在的参数
    # hh24:mi:ss
    sql2 = sql.upper()
    sql3 = sql
    a = 0
    while a != -1:
        a = sql2.find("HH24:MI:SS")
        if a != -1:
            sql3 = sql3[:a] + sql3[a + 10:]
            sql2 = sql2[:a] + sql2[a + 10:]

    a = 0
    while a != -1:
        a = sql2.find("HH24:MI")
        if a != -1:
            sql3 = sql3[:a] + sql3[a + 7:]
            sql2 = sql2[:a] + sql2[a + 7:]

    a = 0
    while a != -1:
        a = sql2.find("MI:SS")
        if a != -1:
            sql3 = sql3[:a] + sql3[a + 5:]
            sql2 = sql2[:a] + sql2[a + 5:]

    a = 0
    while a != -1:
        a = sql2.find("HH:MI")
        if a != -1:
            sql3 = sql3[:a] + sql3[a + 5:]
            sql2 = sql2[:a] + sql2[a + 5:]

    pNames = sqlGenerator.findparam(sql3)  # 解析SQL之后的参数列表
    spdbtime = 0
    result = None
    try:

        if pNames != None:
            ps = {}
            for item in pNames:
                if item in p['pks']:
                    ps[item] = p['pks'][item]
                else:
                    return {"errormsg": (u"服务调用参数不全,参数" + item['name'] + u"没有找到")}

            DBstarttime = (datetime.now())
            conn = dbtip.getConnect(ds)
            cursor = conn.cursor()
            cursor.execute(sql, ps)
            spdbtime = (datetime.now() - DBstarttime).total_seconds() * 1000
        else:
            DBstarttime = (datetime.now())
            conn = dbtip.getConnect(ds)
            cursor = conn.cursor()
            cursor.execute(sql)
            spdbtime = (datetime.now() - DBstarttime).total_seconds() * 1000
        result = dbtip.dictfetchall(cursor)
    except Exception as e:
        return {"errormsg": (u"访问数据库时发生错误，" + e.msg)}
    finally:
        if not (cursor is None):
            cursor.close()
        conn.close()

    return {"result": json.dumps(result, cls=redis.DateTimeEncoder, ensure_ascii=False),
            "spdbtime": spdbtime,
            "sptime": (datetime.now() - starttime).total_seconds() * 1000}


def tableService(srv, params):
    starttime = (datetime.now())
    p = params
    if p['action'] == 'meta':
        # 返回元数据
        r = json.dumps(srv['meta'],
                       cls=redis.DateTimeEncoder,

                       ensure_ascii=False)
        return {"result": r}
    if p['action'] == 'dict':
        # 返回元数据
        r = json.dumps(srv['dict'],
                       cls=redis.DateTimeEncoder,
                       ensure_ascii=False)
        return {"result": r}
    # 默认动作，查询数据及根据主键返回数据
    selectBuilder = sqlGenerator.SelectBuilder()

    if srv['fieldlist'] != '' and not (srv['fieldlist'] is None):
        str = srv['fieldlist']
        sarry = str.split(',')
        for item in sarry:
            selectBuilder.column(item)
    tablename = srv['tableName']
    if tablename.find(".") == -1:
        tablename = srv['schemaName'] + "." + srv['tableName']
    selectBuilder.table(tablename)

    if p['action'] == 'query' and p['opt'] != "":
        # 根据条件返回数据
        selectBuilder.addWhere(p['opt'])
    # elif p['action'] == 'sql' and request.method == "POST":
    #     # 执行SELECT语句
    #     pass
    elif len(p['pks']) != 0:
        # 处理主键查询
        for pk in p['pks']:
            pass
    if p['order'].strip():
        # 处理排序字段
        orders = p['order'].split("|")
        for s in orders:
            selectBuilder.orderby(s)

    # stnm from stu.st_stbprp_b on st_stbprp_b.stcd=src.stcd
    if srv['innerjoin'] != "" and not (srv['innerjoin'] is None):
        # '_CACHE:stnm on stcd'
        if srv['innerjoin'][0:6] != '_CACHE:':
            selectBuilder = sqlGenerator.InnerSelectBuilder(selectBuilder, srv['innerjoin'])

    if p['pagesize'] == 0 and p['limit'] == 0:
        p["limit"] = 10000
    if p["limit"] > 10000:
        p["limit"] = 10000
    ds = srv["datasource"]
    if ds is None:
        ds = settings.DEFAULTRESTCONN
    builder = sqlGenerator.SelectPagerBuilder(selectBuilder, p['pagesize'], p['pageindex'], p['limit'],dbtype=dbtip.getDBType(ds))
    sql = builder.buildSQL().getSQL()

    if settings.DEBUG:
        settings.debugLogger.debug("pure sql:" + selectBuilder.buildSQL().getSQL())
        settings.debugLogger.debug("pager sql:" + sql)

    if p['sql'] == "true":
        return {"result": sql}
    if not sqlParse.availableSQL(selectBuilder.buildSQL().getSQL()):
        # 非法SQL语句
        # self.render('msg.html', title=u"错误", msg=u"SQL语句非法:" + selectBuilder.buildSQL().getSQL())
        # self.finish()
        # callback()
        return {"errormsg": u"SQL语句非法:" + selectBuilder.buildSQL().getSQL()}

    # cursor = connections[settings.DEFAULTRESTCONN].cursor()
    # cursor.execute(sql)

    DBstarttime = (datetime.now())
    data = dbtip.querySQL2map(sql, param=None, dbid=ds)
    spdbtime = (datetime.now() - DBstarttime).total_seconds() * 1000
    if srv['innerjoin'] != "" and not (srv['innerjoin'] is None) and (
                srv['innerjoin'][0:7] == '_CACHE:'):
        # '_CACHE:stnm on stcd'
        result = innerjoinfromcache(srv['innerjoin'], data)
    else:
        result = data
    if p['opt'] == 'd':
        # 处理元数据动作
        result = {'dict': srv['dict'], 'data': result}
    if p['opt'] == 'm':
        # 处理元数据动作
        result = {'dict': srv['meta'], 'data': result}

    r = json.dumps(result, cls=redis.DateTimeEncoder, ensure_ascii=False)
    return {"result": r,
            "spdbtime": spdbtime,
            "sptime": (datetime.now() - starttime).total_seconds() * 1000}
