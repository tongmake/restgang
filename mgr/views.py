__author__ = 'menghui'
# coding=utf-8
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.escape

import mgr.redistip as redistip
import secret.appSecret as sec
from mgr.redistip import GLOBAREDIS
import service.utils as utils


########################################################################################################################
class RedisHanler(tornado.web.RequestHandler):
    '''
    处理针对redis的管理类的请求
    主要用于重新加载redis中的数据，默认的系统的配置信息是保存在oracle中的，为了提高访问性能将数据缓存到redis中。
    使用本类的方法可以重新加载这些数据，实现oracle和redis的数据同步
    依赖与数据缓存的语句，有些同步操作可能非常耗时
    GET     /keys?p=[QUERY]         查询REDIS中的KEY值，等同于redis的keys命令
    GET     /get?key=[KEYNAME]      返回redis中的值
    GET     /createHash?key=&data=  返回加密后的hash值
    GET     /reload？type=           重新加载redis缓存数据
                type==appkey    重新加载应用系统密钥信息，表P_APPKEY

                type==wssrv     重新加载服务信息

                type==cachedata 重新加载有setting文件中的CACHE_TABLES定义的数据缓存信息
    '''

    ####################################################################################################################
    def get(self, path):
        if path == u"srvstic":
            res = []
            keys = redistip.getKeys("SRV_ID_*")
            for key in keys:
                s = str(key, encoding="utf-8")
                sid = s.replace("SRV_ID_", "")
                item = redistip.getfromRedis(key)
                if item is None:
                    continue
                if redistip.getfromRedis("SRV_COUNT_" + sid) is None:
                    item["count"] = 0
                else:
                    item["count"] = redistip.getfromRedis("SRV_COUNT_" + sid)

                if redistip.getfromRedis("SRV_MINTIME_" + sid) is None:
                    item["min"] = 0
                else:
                    item["min"] = redistip.getfromRedis("SRV_MINTIME_" + sid)

                if redistip.getfromRedis("SRV_MAXTIME_" + sid) is None:
                    item["max"] = 0
                else:
                    item["max"] = redistip.getfromRedis("SRV_MAXTIME_" + sid)

                res.append(item)
            self.render("redis/static.html", res=res)

        # ###############################################
        # 查询REDIS的键值
        if path == u"keys":
            p = self.get_argument("p", u"*")
            self.render('redis/keys.html', keys=redistip.getKeys(p))
        # ###############################################
        # 获取REDIS的键值
        if path == u"get":
            k = self.get_argument("key", u"")
            if k == u"":
                raise tornado.web.HTTPError(404)
            self.write(redistip.getStrfromRedis(k))
        # ###############################################
        # 输出加密后的Hash
        if path == "createHash":
            key = self.get_argument("key", u"")
            data = self.get_argument("data", u"")
            if data == u"":
                raise tornado.web.HTTPError(404)
            if key == u"":
                raise tornado.web.HTTPError(404)
            self.write(tornado.escape.url_escape(sec.hmac_sha1(key, data)))
        # ###############################################
        # 从数据库重新加载缓存数据
        if path == u"reload":
            type = self.get_argument("type", u"")
            if type == u"":
                raise tornado.web.HTTPError(404)
            if type == "appkey":
                appid = self.get_argument("appid", None)
                utils._reloadAppky(appid)
            if type == "plant":
                utils._reloadPlant()

            if type == "wssrv":
                ks = GLOBAREDIS.keys("SRV_URL_*")
                for k in ks:
                    GLOBAREDIS.delete(k)
                ks = GLOBAREDIS.keys("SRV_ID_*")
                for k in ks:
                    GLOBAREDIS.delete(k)
                utils._reloadwssrv()  # type==1
                utils._reloaddatatable()  # type==3、4、5、6、7
                utils._reloadrestsrv()  # type==2
                # utils._reloadcloudSrv()  # type==8
                utils.reloadDataSource()  # 重新加载数据源信息

            if type == "cachedata":
                utils._reloadCacheData()  # ######################################################################################################################


class RedisIndex(tornado.web.RequestHandler):
    def get(self):
        self.render('redis/index.html')


# ######################################################################################################################
class MgrHandler(tornado.web.RequestHandler):
    def get(self, path):
        if path == u'getsrv':
            sid = self.get_argument("sid", "-1")
            url = self.get_argument("url", "")
            if sid == -1 and url != "":
                srv = utils.getSrvbyURLfromredis(url)
                self.write(tornado.escape.json_encode(srv).decode('unicode_escape'))
            elif sid != -1 and url == "":
                srv = utils.getSrvbyIDfromredis(sid)
                self.write(tornado.escape.json_encode(srv).decode('unicode_escape'))
            else:
                raise tornado.web.HTTPError(404)
        else:
            self.render(u"mgr/" + path + u".html")
