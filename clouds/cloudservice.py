import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.escape
import tornado.gen
import secret.appSecret as sec
import mgr.redistip as redistip
import mgr.dbtip as dbtip
import settings
import mgr.redistip as redis
import json
import traceback


class CloudSrvHandler(tornado.web.RequestHandler):
    '''
        处理大平台服务的控制和注册服务
    '''

    def isValidRequest(self):
        '''
        安全验证，判断请求是否合法
        传入参数包括：c和hash，c是平台在数据库中保存的SYSUSERNAME，hash是根据这个名字使用SYSPWD加密生成的密钥
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
        sysname = self.get_argument("c", "")
        if sysname == "":
            self.render('errormsg.html', result=u"error", msg=u"URL缺失参数c")
            settings.errorLogger.error(u"AU:身份验证请求错误,URL缺失参数c")
            self.finish()
            return [0]
        hash = self.get_argument("hash", "")
        if hash == "":
            self.render('errormsg.html', result=u"error", msg=u"URL缺失参数hash")
            settings.errorLogger.error(u"AU:身份验证请求错误,URL缺失参数hash")
            self.finish()
            return [0]
        p = redistip.getfromRedis("PC_" + sysname)
        if p is None:
            settings.infoLogger.info(u"AU:身份验证失败,c:" + sysname + "  hash:" + hash)
            return [0]

        if not sec.isValidKey(sysname, hash, p["syspwd"]):
            settings.infoLogger.info(u"AU:身份验证失败,c:" + sysname + "  hash:" + hash)
            return [0]
        settings.infoLogger.info(u"AU:身份验证成功,c:" + sysname + "  hash:" + hash)
        return [1, p]

    def getSrv(self, callback):
        p = self.isValidRequest()
        if not (p[0]):
            self.render('errormsg.html', result=u"error", msg=u"请求校验失败")

            callback()
            return
        rmap = dbtip.querySQL2map(
                "select a.SERVICEID,a.SECRET,a.SERVICENAME,a.NOTE,b.ORIGIALURL from USERVICE_DATA a INNER  JOIN USERVICE_CLOUD b on a.serviceid=b.serviceid where b.plantid=:pid",
                {"pid": p[1]["platid"]})
        for item in rmap:
            if item["SECRET"] != "N":
                acmap = dbtip.querySQL2map(
                        "SELECT b.sysusername FROM USERVICE_CLOUDROLE a inner join p_platform b on a.platid=b.platid where a.serviceid=:sid",
                        {"sid": item["SERVICEID"]})
                item["access"] = ",".join([x["SYSUSERNAME"] for x in acmap])
        rs = json.dumps(rmap, cls=redis.DateTimeEncoder, ensure_ascii=False)
        self.write(rs)
        self.finish()
        callback()

    def authSrv(self, callback):
        '''
        认证服务
        传入URL：http://127.0.0.1:8000/clouds/srvauth?sid=21&sname=shanghai&tname=beijing&c=shanghai&hash=b%274VObEmQNuJvtGXoUW3phNWTPfkg%3D%27
        其中：
         sid：服务ID
         sname：发起方平台的系统用户名
         tname：服务目标平台的系统用户名
         c：发起方系统用户名
         hash：校验码，通过数据库中保存的平台的密码对系统用户名加密的后的校验码
        @param callback:
        @return:
        '''
        p = self.isValidRequest()
        if not (p[0]):
            self.render('errormsg.html', result=u"error", msg=u"请求校验失败")

            callback()
            return
        sid = self.get_argument("sid", "")  # 请求的服务id
        sname = self.get_argument("sname", "")  # 请求发起的平台系统用户名
        tname = self.get_argument("tname", "")  # 请求目的平台系统用户名
        if sid == "":
            settings.infoLogger.info(u"请求服务id非法")
            self.render('errormsg.html', result=u"error", msg=u"请求服务id非法")

            callback()
            return
        p = redistip.getfromRedis("PC_" + sname)
        if p is None:
            settings.infoLogger.info(u"请求发起平台用户名错误")
            self.render('errormsg.html', result=u"error", msg=u"请求发起平台用户名错误")

            callback()
            return
        p2 = redistip.getfromRedis("PC_" + tname)
        if p2 is None:
            settings.infoLogger.info(u"请求目的平台用户名错误")
            self.render('errormsg.html', result=u"error", msg=u"请求目的平台用户名错误")

            callback()
            return
        m = dbtip.querySQL2map("SELECT PLATID, SERVICEID FROM USERVICE_CLOUDROLE where platid=:pid and serviceid=:sid",
                               {
                                   "pid": p["platid"],
                                   "sid": sid
                               })
        if len(m) == 0:
            settings.infoLogger.info(u"没有权限访问该服务，sid=" + sid + ",sname=" + sname + ",tname=" + tname)
            self.render('errormsg.html', result=u"error", msg=u"没有权限访问该服务")
            callback()
            return
        else:
            settings.infoLogger.info(u"验证通过，sid=" + sid + ",sname=" + sname + ",tname=" + tname)
            self.render('errormsg.html', result=u"succeed", msg=u"验证通过")
            callback()
            return

    def delcloudSrv(self, callback):
        '''
        删除云服务，级联删除服务表、权限表
        @param callback:
        @return:
        '''
        # http://127.0.0.1:8000/clouds/reg?c=&hash=
        p = self.isValidRequest()
        if not (p[0]):
            self.render('errormsg.html', result=u"error", msg=u"请求校验失败")
            self.finish()
            callback()
            return
        url = self.get_argument("origialurl", "")

        if url == "":
            self.render('errormsg.html', result=u"error", msg=u"origialurl 为空")
            self.finish()
            callback()
            return
        rmap = dbtip.querySQL2map("select SERVICEID from USERVICE_CLOUD where ORIGIALURL=:ORIGIALURL",
                                  {"ORIGIALURL": url})
        if len(rmap) == 0:
            self.render('errormsg.html', result=u"error", msg=u"没有找到要删除的服务")
            self.finish()
            callback()
            return
        sid = rmap[0]["SERVICEID"]

        def _deletecloudsrv(conn):
            cur = conn.cursor()
            try:
                cur.execute("delete USERVICE_CLOUDROLE where SERVICEID=:sid", {"sid": sid})
                cur.execute("delete USERVICE_CLOUD where SERVICEID=:sid", {"sid": sid})
                cur.execute("delete USERVICE_DATA where  SERVICEID=:sid", {"sid": sid})
                conn.commit()
            except Exception as e:
                settings.errorLogger.error("删除云服务错误")
                settings.errorLogger.error(traceback.format_exc())
                return
            self.render('errormsg.html', result=u"succeed", msg=u"succeed")
            settings.infoLogger.info(",".join(["云服务删除成功",
                                               "平台locationcode", p[1]["sysusername"],
                                               "服务地址：", url,
                                               "服务ID：", str(sid)]))

        # 删除数据
        dbtip.executeSQL(_deletecloudsrv)
        self.finish()
        callback()

    def updatecloudSrv(self, callback):
        '''
        更新云服务
        @param callback:
        @return:
        '''
        # http://127.0.0.1:8000/clouds/updatesrv?c=&hash=
        p = self.isValidRequest()
        if not (p[0]):
            self.render('errormsg.html', result=u"error", msg=u"请求校验失败")
            self.finish()
            callback()
            return

        ourl = self.get_argument("origialurl", "")#原始服务地址

        access = self.get_argument("access", "")#权限
        note = self.get_argument("note", "")#note是说明
        servicename = self.get_argument("servicename", "")#服务名

        if ourl == "":
            self.render('errormsg.html', result=u"error", msg=u"ORIGIALURL is null")
            self.finish()
            callback()
            return
        ###############################################################################################################
        # 根据SYSUSERNAME返回平台ID
        rmap = dbtip.querySQL2map("select PLATID from P_PLATFORM where SYSUSERNAME=:id", {"id": p[1]["sysusername"]})
        if len(rmap) == 0:
            self.render('errormsg.html', result=u"error", msg=u"PLANTFORM not found")
            self.finish()
            callback()
            return
        platid = rmap[0]["PLATID"]
        ################################################################################################################
        # 根据url和平台ID返回serviceid和SECRET字段
        rmap = dbtip.querySQL2map(
                "select a.SERVICEID,a.SECRET from USERVICE_DATA a INNER JOIN USERVICE_CLOUD b on a.serviceid=b.serviceid where b.plantid=:pid and b.ORIGIALURL=:url",
                {"pid": platid, "url": ourl})
        if len(rmap) == 0:
            self.render('errormsg.html', result=u"error", msg=u"service not found")
            self.finish()
            callback()
            return
        sid = rmap[0]["SERVICEID"]
        secrest = rmap[0]["SECRET"]
        ################################################################################################################
        # 如果更新了权限，则获取权限信息对应的platid，保存在accessmap中
        accessmap = None
        if secrest != "" and secrest != "NOP":
            acs = access.split(',')
            accessmap = [x["PLATID"] for x in dbtip.querySQL2map(
                    "select PLATID from P_PLATFORM where SYSUSERNAME in (" + ",".join(
                            [":ids" + str(x) for x in range(len(acs))]) + ")",
                    dict(zip(["ids" + str(x) for x in range(len(acs))], acs)))]

        def _updateservice(conn):
            r = {"sid": sid}
            # 更新USERVICE_DATA表
            sql = "update USERVICE_DATA set "
            se = []
            if note != "":
                se.append("NOTE=:note")
                r["note"] = note
            if servicename != "":
                se.append("SERVICENAME=:sname")
                r["sname"] = servicename
            if access == "NOP" and secrest != "N":
                # 更新为不进行安全认证
                se.append("SECRET='N'")
            if access != "NOP" and secrest == "N":
                # 更新为不进行安全认证
                se.append("SECRET='S'")
            sql = sql + ",".join(se) + " where serviceid=:sid"
            try:
                cur = conn.cursor()
                cur.execute(sql, r)

                if access != "":
                    # 需要更新权限
                    # 删除全部权限信息
                    cur.execute("DELETE USERVICE_CLOUDROLE where SERVICEID=:sid", {"sid": sid})
                    # 插入新的权限信息
                    if access != "NOP":
                        sql = "insert into USERVICE_CLOUDROLE (PLATID, SERVICEID) values (:PLATID, :SERVICEID)"
                        for i in accessmap:
                            cur.execute(sql, {"SERVICEID": r["sid"], "PLATID": i})
                conn.commit()
            except Exception as e:
                settings.errorLogger.error("修改云服务错误")
                settings.errorLogger.error(traceback.format_exc())
                self.render('errormsg.html', result=u"error", msg=u"数据库操作异常")
                self.finish()
                return
            self.render('errormsg.html', result=u"succeed", msg=u"succeed")
            settings.infoLogger.info(",".join(["云服务修改成功",
                                               "平台id：", str(p[1]["platid"]),
                                               ",服务名称:", servicename,
                                               ",服务地址:", ourl,
                                               ",服务说明:", note,
                                               ",服务权限:", access]))

        dbtip.executeSQL(_updateservice)
        self.finish()
        callback()

    def regcloudSrv(self, callback):
        '''
        注册云服务，由下级平台注册
        采用POST请求
        在url中包含参数：
            c：发起方系统用户名
            hash：校验码，通过数据库中保存的平台的密码对系统用户名加密的后的校验码
        post中的数据包括：
            servicename：服务名称
            note：服务说明
            origialurl：服务地址

        @param callback:
        @return:
        '''
        # http://127.0.0.1:8000/clouds/reg?c=&hash=
        p = self.isValidRequest()
        if not (p[0]):
            self.render('errormsg.html', result=u"error", msg=u"请求校验失败")
            self.finish()
            callback()
            return
        r = {"SERVICENAME": self.get_argument("servicename", ""), "NOTE": self.get_argument("note", "")}
        r2 = {"ORIGIALURL": self.get_argument("origialurl", "")}
        access = self.get_argument("access", "NOP")
        if r["SERVICENAME"] == "":
            self.render('errormsg.html', result=u"error", msg=u"SERVICENAME is null")
            self.finish()
            callback()
            return

        if r2["ORIGIALURL"] == "":
            self.render('errormsg.html', result=u"error", msg=u"ORIGIALURL is null")
            self.finish()
            callback()
            return

        r2["PLANTID"] = p[1]["platid"]
        rmap = None  # 传入的locationcode转换为PLATID的列表，在r["SECRET"] = "S"时由下面的else语句赋值
        if access == "NOP":
            r["SECRET"] = "N"
        else:
            r["SECRET"] = "S"
            acs = access.split(',')
            names = [":ids" + str(x) for x in range(len(acs))]
            sql = "select PLATID from P_PLATFORM where SYSUSERNAME in (" + ",".join(names) + ")"
            pm = dict(zip(["ids" + str(x) for x in range(len(acs))], acs))
            rmap = [x["PLATID"] for x in dbtip.querySQL2map(sql, pm)]

        '''
        判断传入的URL是否已经存在
        '''
        map2 = dbtip.querySQL2map("select * from USERVICE_CLOUD where PLANTID=:PID and ORIGIALURL=:URL",
                                  {"PID": r2["PLANTID"], "URL": r2["ORIGIALURL"]})
        if len(map2) != 0:
            self.render('errormsg.html', result=u"error", msg=u"ORIGIALURL already exist")
            self.finish()
            callback()
            return

        ################################################################################################################

        def _insertCloudsrv(conn):
            '''
            执行SQL的回调函数
            @param conn:
            @return:
            '''
            try:
                cur = conn.cursor()
                cur.execute("select USERVICE_DATA_SQ.nextval from dual")
                r["id"] = cur.fetchall()[0][0]
                r2["id"] = r["id"]
                cur.execute("insert into USERVICE_DATA (SERVICEID,TYPE,SERVICENAME,URL,ENABLED,CACHETYPE,SECRET,MSGLOG,NOTE) \
                            VALUES (:id,8,:SERVICENAME,'',1,'N',:SECRET,'N',:NOTE)", r)
                cur.execute("insert into USERVICE_CLOUD (SERVICEID,SERVICETYPE,ORIGIALURL,META,ORIGIALSECURITY,PLANTID) \
                            VALUES (:id,'0',:ORIGIALURL,'','N',:PLANTID)", r2)
                if rmap != None:
                    # 传入的SECRET!=NOP时需要插入权限表
                    sql = "insert into USERVICE_CLOUDROLE (PLATID, SERVICEID) values (:PLATID, :SERVICEID)"
                    for i in rmap:
                        cur.execute(sql, {"SERVICEID": r["id"], "PLATID": i})

                conn.commit()
            except Exception as e:
                settings.errorLogger.error("注册云服务错误")
                settings.errorLogger.error(traceback.format_exc())
                self.render('errormsg.html', result=u"error", msg=u"数据库操作异常")
                self.finish()
                return
            self.render('errormsg.html', result=u"succeed", msg=u"succeed")
            settings.infoLogger.info(",".join(["云服务注册成功",
                                               "平台id：", str(p[1]["platid"]),
                                               ",服务名称:", r["SERVICENAME"],
                                               ",服务地址:", r2["ORIGIALURL"]]))

        # 插入数据库
        dbtip.executeSQL(_insertCloudsrv)
        self.finish()
        callback()

    def registerPlantforms(self, callback):
        '''
        新平台注册
        传入：http://127.0.0.1:8000/clouds/regplant?regcode=81-d6-ac-1e-e2-35-a1-5c&pluginurl=http://test

        传入参数包括:
            regcode：注册码，每个下级平台一个
            pluginurl：前置地址，由平台前置生成
        @param callback:
        @return:
        '''
        # 新平台注册
        regcode = self.get_argument("regcode", "")
        pluginurl = self.get_argument("pluginurl", "")
        if regcode == "":
            self.render('errormsg.html', result=u"error", msg=u"注册码无效")
            self.finish()
            callback()
            return
        if pluginurl == "":
            self.render('errormsg.html', result=u"error", msg=u"注册信息不全")
            self.finish()
            callback()
            return
        Lcode = str(sec.decryptSN(regcode), encoding="utf-8")

        settings.infoLogger.info("#############debug info:")
        settings.infoLogger.info("Register Plantforms:")
        settings.infoLogger.info("   regcode:" + regcode)
        settings.infoLogger.info("   decrypt:" + Lcode)
        rmap = dbtip.querySQL2map("select * from P_PLATFORM where sysusername=:uname", {"uname": Lcode})
        if len(rmap) == 0:
            settings.debugLogger.debug("#############debug info:")
            settings.debugLogger.debug("Register Plantforms:")
            settings.debugLogger.debug("   regcode:" + regcode)
            settings.debugLogger.debug("   decrypt:" + Lcode)
            settings.debugLogger.debug("   SysuserName not found!")
            self.render('errormsg.html', result=u"error", msg=u"没有找到对应的平台注册信息")
            self.finish()
            callback()
            return

        def _updateregisterplant(conn):
            try:
                cur = conn.cursor()
                cur.execute("UPDATE P_PLATFORM set PLUGURL=:url,ACT='A' where sysusername=:sysusername",
                            {"url": pluginurl, 'sysusername': Lcode})
                conn.commit()
            except Exception as e:
                settings.errorLogger.error("平台注册数据库操作错误")
                settings.errorLogger.error("   regcode:" + regcode)
                settings.errorLogger.error("   decrypt:" + Lcode)
                settings.errorLogger.error(traceback.format_exc())
                self.render('errormsg.html', result=u"error", msg=u"数据库操作异常")

                return
            self.render('errormsg.html', result=u"succeed", msg=Lcode)
            settings.infoLogger("".join(["平台注册成功,平台id:", Lcode]))

        dbtip.executeSQL(_updateregisterplant)
        self.finish()
        callback()

    def getallplantforms(self, callback):
        # 返回所有平台
        try:
            conn = dbtip.getConnect()
            cursor = conn.cursor()
            cursor.execute("SELECT PLATID, AREA, CONTACTS, SYSUSERNAME FROM P_PLATFORM ")
            result ={'suecceed':'true','data':dbtip.dictfetchall(cursor)}

            r = json.dumps(result, cls=redis.DateTimeEncoder, ensure_ascii=False)
            self.write(r)
        finally:
            if not (cursor is None):
                cursor.close()
            conn.close()
        self.finish()
        callback()

    def getregistercode(self, callback):
        '''
            返回平台注册码
            url传入：
                plantcode：为空返回全部注册码，不为空返回指定平台的注册码
                format：传入空或不传入返回JSON格式，否则返回html格式
        @param callback:
        @return:
        '''

        sysusername = self.get_argument("plantcode", "")

        r = None
        if sysusername == "":
            r = dbtip.querySQL2map("SELECT PLATID,AREA, SYSUSERNAME FROM P_PLATFORM ")
        else:
            r = dbtip.querySQL2map("SELECT PLATID,AREA, SYSUSERNAME FROM P_PLATFORM where SYSUSERNAME=:uname",
                                   {"uname": sysusername})
        if not (r is None):
            for item in r:
                item["sncode"] = sec.getDesSn(item["SYSUSERNAME"])
            if self.get_argument("format", "") == "":
                rs = json.dumps(r, cls=redis.DateTimeEncoder, ensure_ascii=False)
                self.write(rs)
            else:
                self.render('snlist.html', result=r)
        self.finish()
        callback()

    @tornado.web.asynchronous
    @tornado.gen.engine
    def get(self, path):
        if path == u'plants':
            # 返回所有平台
            yield tornado.gen.Task(self.getallplantforms)
        elif path == u'regplant':
            # 注册下级平台
            yield tornado.gen.Task(self.registerPlantforms)
        elif path == u'getregistercode':
            # 返回注册码
            yield tornado.gen.Task(self.getregistercode)
        elif path == u'srvauth':
            # 认证服务
            yield tornado.gen.Task(self.authSrv)

        elif path == u'get':
            # 返回服务
            yield tornado.gen.Task(self.getSrv)

    @tornado.web.asynchronous
    @tornado.gen.engine
    def post(self, path):
        if path == u'reg':
            # 服务注册,创建一下序列
            # CREATE SEQUENCE USERVICE_DATA_SQ INCREMENT BY 1 MAXVALUE 9999999999999999999999999999 MINVALUE 1 CACHE 20;
            yield tornado.gen.Task(self.regcloudSrv)
        elif path == u"delsrv":
            yield tornado.gen.Task(self.delcloudSrv)
        elif path == u"updatesrv":
            yield tornado.gen.Task(self.updatecloudSrv)
