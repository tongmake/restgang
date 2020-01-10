__author__ = 'menghui'
# coding=utf-8
import textwrap

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.escape
import tornado.gen
import mgr.redistip as redis
import secret.appSecret as sec
import tornado.httputil
import settings
from datetime import *
import string
import json
from sql import sqlGenerator
from sql import sqlParse
from mgr.redistip import GLOBAREDIS
import mgr.dbtip as dbtip


# ######################################################################################################################
#  处理直接的SQL服务
class sqlSrvHandler(tornado.web.RequestHandler):
    def commonRequestParam(self):
        keys = ['_limit', '_pagesize', '_pageindex', '_opt', '_sql']
        result = {
            'limit': '',
            'pagesize': '',
            'pageindex': '',
            'opt': '',
            'sql': '',
            'pks': {}
        }
        for item in self.request.arguments:
            if item in keys:
                result[item[1:]] = self.get_argument(item, "")
            else:
                result['pks'][item] = self.get_argument(item, "")
        if result['limit'] == "":
            result['limit'] = 0
        else:
            result['limit'] = int(result['limit'])
        if result['pagesize'] == "":
            result['pagesize'] = 0
        else:
            result['pagesize'] = int(result['pagesize'])
        if result['pageindex'] == "":
            result['pageindex'] = 0
        else:
            result['pageindex'] = int(result['pageindex'])
        return result
    @tornado.gen.engine
    @tornado.web.asynchronous
    def doSQL(self, callback):
        p = self.commonRequestParam()
        if not sqlParse.availableSQL(p["sql"]):
            # 非法SQL语句
            self.render('msg.html', title=u"错误", msg=u"SQL语句非法:" + p["sql"])
            self.finish()
            callback()
            return
        if p['pagesize'] == 0 and p['limit'] == 0:
            p["limit"] = 10000
        if p["limit"] > 10000:
            p["limit"] = 10000
        builder = sqlGenerator.SelectPagerBuilder(None, p['pagesize'], p['pageindex'], p['limit'], sql=p['sql'])
        sql = builder.buildSQL().getSQL()

        conn = dbtip.getConnect(settings.DEFAULTRESTCONN)
        cursor = conn.cursor()

        try:
            if len(p['pks']) != 0:
                cursor.execute(sql, p['pks'])
            else:
                cursor.execute(sql)
            result = dbtip.dictfetchall(cursor)
            r = json.dumps(result, cls=redis.DateTimeEncoder, ensure_ascii=False)
            self.write(r)
        finally:
            if not (cursor is None):
                cursor.close()
            conn.close()
        self.finish()
        callback()

    # ##################################################################################################################
    # 代理GET请求
    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self):
        pass

    # ##################################################################################################################
    # 代理POST请求
    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self):
        yield tornado.gen.Task(self.doSQL)

class hugeSQLHandler(tornado.web.RequestHandler):
    pass