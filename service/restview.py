__author__ = 'menghui'
# coding=utf-8


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
from mgr.redistip import GLOBAREDIS
import uuid
import jobs.msglog as msglog
import service.qsService as qsService
import jobs.msgcache as msgcache


# ######################################################################################################################
# 处理HTTP代理服务
class ProxyHandler(tornado.web.RequestHandler):
    # http 代理时需要忽略的http head
    _ignoreHeader = ["Host", 'Transfer-Encoding', 'Content-Encoding', "If-None-Match", "If-Modified-Since"]
    # 当前请求对应的srv实例，由doGo方法赋值
    _Srv = None

    # 处理服务的方法最终返回正确的结果时需要调用此方法写入结果
    def writeResult(self, chunk):
        self.write(chunk)
        msgcache.write2Cache(self, chunk)

    def commonRequestParam(self):
        keys = ['_limit', '_pagesize', '_pageindex', '_action', '_opt', '_order', '_sql', '_test']
        result = {
            'limit': '',
            'pagesize': '',
            'pageindex': '',
            'action': '',
            'opt': '',
            'order': '',
            'sql': '',
            'pks': {}}
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

    # ##################################################################################################################
    @tornado.gen.engine
    @tornado.web.asynchronous
    def redisService(self, callback):
        '''
        返回纯缓存数据
        :param srv:
        :param callback:
        :return:
        '''
        ps = self.commonRequestParam()
        r = redis.GLOBAREDIS
        keys = r.keys(self._Srv["tableName"] + "*")
        p = r.pipeline()
        for k in keys:
            p.get(k)
        # r = json.dumps(p.execute(), cls=DateTimeEncoder, encoding='utf-8', ensure_ascii=False)
        r = p.execute()

        r = ",".join(map(lambda x: x.decode(), r))
        self.writeResult("[%s]" % bytes(r, "utf-8").decode('raw_unicode_escape'))
        msglog.wirteMsg(r, self._Srv, uuid.uuid1().hex,
                        {"clientid": self.request.remote_ip,
                         "time": datetime.now(),
                         "params": ps,
                         "srv": self._Srv})
        self.finish()
        callback()

    def addinnerjoin(self, row, name, prekey, buffer):
        '''
        添加一个InnerJoin节点，与innerjoinfromcache方法配合使用
        :param row:
        :param name:
        :param prekey:
        :param buffer:
        :return:
        '''
        k = u"%s%s" % (prekey[0], row[prekey[1]])
        value = buffer.get(k, None)
        if value == None:
            value = redis.getStrfromRedis(k)
            buffer[k] = value
        row[name] = value
        return row

    def innerjoinfromcache(self, innerjoin, data):
        '''
        从redis中返回缓存的数据做表链接
        :param innerjoin:
        :param data:
        :return:
        '''
        buffer = {}
        # _CACHE:stnm on CHCHE_stu_st_stbprp_b_:stcd

        cmd = innerjoin[7:].split()
        if cmd[1] == 'on':
            name = cmd[0]  # 添加到data的字段名
            prekey = cmd[2].split(':')  # [0] key前缀，[1] 字段名
            return [
                self.addinnerjoin(row, name, prekey, buffer)
                for row in data
                ]

    @tornado.gen.engine
    @tornado.web.asynchronous
    def datatableService(self, callback):
        '''
        处理数据封装服务
        :param srv:
        :return:
        '''
        p = self.commonRequestParam()
        r = qsService.tableService(self._Srv, p)
        if "errormsg" in r:
            self.render('msg.html', title=u"错误", msg=r["errormsg"])
            self.finish()
            callback()
        else:
            self.writeResult(r["result"])
            msglog.wirteMsg("", self._Srv, uuid.uuid1().hex,
                            {"clientid": self.request.remote_ip,
                             "time": datetime.now(),
                             "sptime": r["sptime"],
                             "spdbtime": r["spdbtime"],
                             "params": p})
            self.finish()
            callback()

    @tornado.gen.engine
    @tornado.web.asynchronous
    def sqlService(self, callback):
        '''
        处理SQL服务,下面的程序没有检测传入参数的类型，错误的参数传入有可能出发500系统异常
        :param srv:
        :return:
        '''
        p = self.commonRequestParam()
        r = qsService.sqlService(self._Srv, p)
        if "errormsg" in r:
            self.render('msg.html', title=u"错误", msg=r["errormsg"])
            self.finish()
            callback()
        else:
            self.writeResult(r["result"])
            msglog.wirteMsg("", self._Srv, uuid.uuid1().hex,
                            {"clientid": self.request.remote_ip,
                             "time": datetime.now(),
                             "sptime": r["sptime"],
                             "spdbtime": r["spdbtime"],
                             "params": p})
            self.finish()
            callback()

    def isValidRequest(self):
        '''
        安全验证，判断请求是否合法
        hash为传入的验证码，当srv的secret字段为N时不进行安全验证，为P时只校验APPKEY和HASH是否匹配，为S时校验整个URL和hash是否匹配，因此为S时
        每一个请求都需要重新生成hash，对于服务端P模式和S模式在性能上没有区别。
        hash算法为hmac_sha1，密码为数据库中PWD字段
        在java下使用下面算法生成hash

        import java.security.InvalidKeyException;
        import java.security.NoSuchAlgorithmException;
        import javax.crypto.Mac;
        import javax.crypto.spec.SecretKeySpec;

        public class JavaApplication1 {

            private static final String HMAC_SHA1 = "HmacSHA1";

            public static String getSignature(String data, String key) throws Exception {
                byte[] keyBytes = key.getBytes();
                SecretKeySpec signingKey = new SecretKeySpec(keyBytes, HMAC_SHA1);
                Mac mac = Mac.getInstance(HMAC_SHA1);
                mac.init(signingKey);
                byte[] rawHmac = mac.doFinal(data.getBytes());
                return encode(rawHmac);
            }

            public static String encode(byte[] bstr) {
                return new sun.misc.BASE64Encoder().encode(bstr);
            }

            public static void main(String[] args) throws Exception {
                System.out.println(getSignature("abcd", "123"));
            }

        }
        :param srv:
        :return:
        '''
        if self._Srv["secret"] == "N":
            return True
        else:
            furl = self.request.full_url()
            i = furl.find(u"hash=")
            if i < 0:
                self.render('msg.html', title=u"错误", msg=u"请求安全服务必须传入hash参数")
                self.finish()
                return False
            hurl = tornado.escape.url_unescape(furl[:i - 1])
            try:
                hashcode = self.get_argument("hash", "")
            except:
                self.render('msg.html', title=u"错误", msg=u"hash参数只能包含ASCII数据")
                self.finish()
                return False
            appcode = self.get_argument("appcode", "")
            if appcode == "":
                self.render('msg.html', title=u"错误", msg=u"请求安全服务必须传入appcode参数")
                self.finish()
                return False
            appkey = redis.getfromRedis("APPKEY_" + appcode)
            if appkey is None:
                self.render('msg.html', title=u"错误", msg=u"没有找到对应的应用系统信息，appcode：" + appcode)
                self.finish()
                return False
            if self._Srv["secret"] == "S":
                # 安全控制,每个请求都验证
                if not sec.isValidKey(hurl, hashcode, appkey['pwd']):
                    self.render('msg.html', title=u"错误", msg=u"密钥验证失败")
                    self.finish()
                    return False
            if self._Srv["secret"] == "P":
                # 安全控制,只验证appcode和hashcode
                if not sec.isValidKey(appcode, hashcode, appkey['pwd']):
                    self.render('msg.html', title=u"错误", msg=u"密钥验证失败")
                    self.finish()
                    return False
            for svrid in appkey['services']:

                if svrid == self._Srv['serviceid']:
                    return True
        self.render('msg.html', title=u"错误", msg=u"没有调用该服务的权限")
        self.finish()
        return False

    @tornado.gen.engine
    @tornado.web.asynchronous
    def doProxy(self, path, method, callback):
        '''
        处理代理服务
        :param path:
        :param method:
        :param srv:
        :return:
        '''
        # 拼新的URL
        starttime = (datetime.now())
        if self.request.query is None or self.request.query == "":
            url = self._Srv["origialurl"]
        else:
            url = self._Srv["origialurl"] + "?" + self.request.query
        # 构造请求
        r = tornado.httpclient.HTTPRequest(url, method=method)
        # 复制http header
        for h in self.request.headers:
            if not (h in self._ignoreHeader):
                r.headers[h] = self.request.headers[h]

        if method == "POST":
            r.body = self.request.body
        # 异步请求
        http = tornado.httpclient.AsyncHTTPClient()
        part = self
        dbtime = datetime.now()

        # ##################################################################################################################
        # 代理请求原始服务，异步响应处理
        def on_response(response):
            spdbtime = (datetime.now() - dbtime).total_seconds() * 1000
            # if response.error:
            #     raise tornado.web.HTTPError(500)
            for h in response.headers:
                if h != 'Transfer-Encoding' and h != 'Content-Encoding':
                    self.set_header(h, response.headers[h])
            part.write(response.body)
            part.finish()
            msglog.wirteMsg(response.body, self._Srv, uuid.uuid1().hex,
                            {"clientid": self.request.remote_ip,
                             "time": datetime.now(),
                             "sptime": (datetime.now() - starttime).total_seconds() * 1000,
                             "spdbtime": spdbtime,
                             "params": ""})
            callback()

        http.fetch(r, callback=on_response)

    # ##################################################################################################################
    # 处理请求
    @tornado.web.asynchronous
    @tornado.gen.engine
    def doGO(self, path, method):
        st = (datetime.now())

        self._Srv = redis.getfromRedis("SRV_URL_" + path)

        if self._Srv is None:
            self.render('msg.html', title=u"错误", msg=u"没有找到请求的服务")
            self.finish()
            return
        if self._Srv["enabled"] == 0:
            self.render('msg.html', title=u"错误", msg=u"该服务尚未启动")
            self.finish()
            return
        if not self.isValidRequest():
            return

        r = msgcache.getResultFromCache(self)
        if (self._Srv["cachetype"] == "N") or (r is None):
            if self._Srv['type'] == 1:  # WebService
                yield tornado.gen.Task(self.doProxy, path=path, method=method)
            elif self._Srv['type'] == 2:  # RESTful
                yield tornado.gen.Task(self.doProxy, path=path, method=method)
            elif self._Srv['type'] == 5:
                # result = sqlService(request, srv)
                yield tornado.gen.Task(self.sqlService)
            elif self._Srv['type'] == 6:
                # result = datatableService(request, srv)
                yield tornado.gen.Task(self.datatableService)
            elif self._Srv['type'] == 7:
                yield tornado.gen.Task(self.redisService)
            else:
                self.render('msg.html', title=u"错误", msg=u"该服务类型不支持访问")
                self.finish()
                return
        else:
            # 缓存命中
            self.write(r)
            self.finish()
            msglog.wirteMsg("", self._Srv, uuid.uuid1().hex,
                            {"clientid": self.request.remote_ip,
                             "time": datetime.now(),
                             "sptime": (datetime.now() - st).total_seconds() * 1000,
                             "spdbtime": -1,
                             "params": ""})

        # 计算服务调用时间，更新服务计数器
        dt = (datetime.now() - st).total_seconds() * 1000
        GLOBAREDIS.incr("SRV_COUNT_" + str(self._Srv["serviceid"]))
        mt = GLOBAREDIS.mget(
            ["SRV_MAXTIME_" + str(self._Srv["serviceid"]), "SRV_MINTIME_" + str(self._Srv["serviceid"])])
        if mt[0] == None:
            GLOBAREDIS.set("SRV_MAXTIME_" + str(self._Srv["serviceid"]), str(dt))
        else:
            if dt > float(mt[0]):
                GLOBAREDIS.set("SRV_MAXTIME_" + str(self._Srv["serviceid"]), str(dt))

        if mt[1] == None:
            GLOBAREDIS.set("SRV_MINTIME_" + str(self._Srv["serviceid"]), str(dt))
        else:
            if dt < float(mt[1]):
                GLOBAREDIS.set("SRV_MINTIME_" + str(self._Srv["serviceid"]), str(dt))
        if settings.DEBUG:
            settings.debugLogger.debug("".join(["服务调用历时(ms),sid(", str(self._Srv["serviceid"]), "):", str(dt)]))

    # ##################################################################################################################
    # 代理GET请求

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, path):
        self.doGO(path, "GET")

    # ##################################################################################################################
    # 代理POST请求
    @tornado.gen.engine
    @tornado.web.asynchronous
    def post(self, path):
        self.doGO(path, "POST")
