import mgr.dbtip as db
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.escape
import mgr.redistip as redistip
import string
from mgr.redistip import GLOBAREDIS
import settings


# ######################################################################################################################
# 返回字符串是否为数字
def isnumeric(s):
    '''returns True if string s is numeric'''
    return all(c in "0123456789.+-" for c in s)


# ######################################################################################################################
# 字符串转换为数字
def convertToNumber(s):
    if not (isnumeric(s)):
        return None
    if '.' in s:
        return string.atof(s)
    else:
        return int(s)


########################################################################################################################
def reloadDataSource():
    '''
    加载数据库中的P_AT_DATASOURCE表保存的数据源，只支持jdbc:oracle:thin:@127.0.0.1:1521:orcl,stu,stu格式的数据库链接串
    @return:
    '''
    dbmap = db.querySQL2map("select DATAID,DATAURL from P_AT_DATASOURCE")
    if len(dbmap) == 0:
        return
    rs = {}
    for item in dbmap:
        url = item["DATAURL"]
        if url.find("jdbc:oracle:thin") != -1:
            # jdbc:oracle:thin:@127.0.0.1:1521:orcl,stu,stu
            us = url.split(",")
            if len(us) != 3:
                continue
            r = {"USER": us[1], "PASSWORD": us[2]}
            i = us[0].find("@")
            if i == -1:
                continue

            s = us[0][-1 * (len(us[0]) - us[0].find("@") - 1):]
            ss = s.split(":")
            if len(ss) != 3:
                continue
            r["HOST"] = ss[0]
            r["PORT"] = ss[1]
            r["NAME"] = ss[2]
            rs[item["DATAID"]] = r
    redistip.put2redis("P_AT_DATASOURCE", rs)
    for key in rs:
        redistip.put2redis("P_AT_DATASOURCE_%s" % key, rs[key])
        settings.DATABASES[key] = rs[key]


########################################################################################################################
def getSrvbyURLfromredis(url, r=None):
    """
    根据url返回服务实体
    :param url:
    :param r:
    :return:
    """
    if r is None:
        r = redistip.GLOBAREDIS
    id = r.get("SRV_URL_" + url)
    if id is None:
        return None
    s = r.get(id)
    if s is None:
        return None
    return tornado.escape.json_decode(s)


########################################################################################################################
def getSrvbyIDfromredis(sid, r=None):
    """
    根据serviceid返回服务实体
    :param sid:
    :param r:
    :return:
    """
    if r is None:
        r = redistip.GLOBAREDIS
    s = r.get("SRV_ID_" + sid)
    if id is None:
        return None
    return tornado.escape.json_decode(s)


# ##################################################################################################################
def _reloadPlant():
    '''
    加载平台信息
    @return:
    '''

    def reloadplant(cur):
        field = ['platid', 'area', 'contacts', 'pluguel', 'sysusername', 'syspwd']
        for item in cur.fetchall():
            redistip.put2redis("PC_" + item[4], dict(zip(field, item)))
            if settings.DEBUG:
                settings.infoLogger.info("add plantfrom,key:%s" % ("PC_" + item[4]))

    db.querySQL("select PLATID, AREA, CONTACTS, PLUGURL, SYSUSERNAME, SYSPWD from P_PLATFORM", reloadplant)


# ##################################################################################################################
def _reloadcloudSrv():
    '''
    加载云服务
    @return:
    '''

    def reloadcloudSrv(cur):
        field = ["SERVICEID", "TYPE", "SERVICENAME", "URL", "ENABLED", "CACHETYPE", "SECRET", "MSGLOG", "NOTE",
                 "SERVICETYPE", "ORIGIALURL", "META", "ORIGIALSECURITY", "PLANTID"]
        for item in cur.fetchall():
            redistip.put2redis("SC_" + str(item[0]), dict(zip(field, item)))
            if settings.DEBUG:
                settings.infoLogger.info("add cloud service,key:%s" % ("PC_" + str(item[0])))

    db.querySQL("SELECT a.SERVICEID,a.TYPE,a.SERVICENAME,a.URL,a.ENABLED,a.CACHETYPE,a.SECRET,a.MSGLOG,a.NOTE,b.SERVICETYPE,b.ORIGIALURL,b.META,b.ORIGIALSECURITY,b.PLANTID FROM USERVICE_DATA a\
                    inner join USERVICE_CLOUD b on a.serviceid=b.serviceid", reloadcloudSrv)


# ##################################################################################################################
def _reloadAppky(appkey=None):
    """
    重新加载AppKey
    :return:
    redis中
            appkey的生成逻辑是“APPKEY_”与appid的字符串连接
            rest服务的redis key 是SRV_URL_
    """

    if appkey is None:
        appsrv = db.querySQL2map("select APP_ID,SERVICE_ID from uservice_servicerole")
    else:
        appsrv = db.querySQL2map("select APP_ID,SERVICE_ID from uservice_servicerole where APP_ID=:APPID", {"APPID": appkey})

    def reloadAppkey(cur):
        """
        重新加载appkey回调句柄
        :param cur:
        :return:
        """
        preKey = "APPKEY_"
        ks = GLOBAREDIS.keys(preKey + "*")
        field = ['app_id', 'publickey', 'privatekey', 'uname', 'pwd']
        appkeys = []
        for item in cur.fetchall():
            d = dict(zip(field, item))
            srvs = []
            for srv in appsrv:
                if srv["APP_ID"] == d['app_id']:
                    srvs.append(srv["SERVICE_ID"])
            d["services"] = srvs
            key = preKey + d['app_id']
            redistip.put2redis(key, d)
            if key in ks:
                ks.remove(key)
            appkeys.append(key)
            if settings.DEBUG:
                settings.infoLogger.info("add app data,appkey:%s" % (preKey + d['app_id']))
        for k in ks:
            GLOBAREDIS.delete(k)

    if appkey is None:
        db.querySQL("SELECT APP_ID,PUBLICKEY,PRIVATEKEY,UNAME,PWD FROM P_APPKEY", reloadAppkey)
    else:
        db.querySQL("SELECT APP_ID,PUBLICKEY,PRIVATEKEY,UNAME,PWD FROM P_APPKEY where APP_ID=:APP_ID",
                    {"APP_ID": appkey}, reloadAppkey)


# ##################################################################################################################
def _reloadrestsrv(keys=[]):
    '''
    重新加载REST SERVICE数据
    @return:
    '''

    # sql查询回调函数
    def reloadservice(cur):
        field = ['serviceid', 'type', 'servicename', 'url', 'enabled', 'cachetype', 'origialurl', 'secret',
                 'msglog']

        for item in cur.fetchall():
            d = dict(zip(field, item))
            redistip.put2redis("SRV_URL_" + d["url"], d)
            if ("SRV_URL_" + d["url"]).encode(encoding="utf-8") in keys:
                keys.remove(("SRV_URL_" + d["url"]).encode(encoding="utf-8"))
            if settings.DEBUG:
                settings.infoLogger.info("app rest service,key:%s" % ("SRV_URL_" + d["url"]))

    sql = "select " \
          "USERVICE_DATA.SERVICEID," \
          "USERVICE_DATA.TYPE," \
          "USERVICE_DATA.SERVICENAME," \
          "USERVICE_DATA.URL," \
          "USERVICE_DATA.ENABLED," \
          "USERVICE_DATA.CACHETYPE, " \
          "USERVICE_REST.ORIGIALURL, " \
          "USERVICE_DATA.SECRET, " \
          "USERVICE_DATA.MSGLOG " \
          "from USERVICE_DATA " \
          "inner join USERVICE_REST on USERVICE_REST.serviceid=USERVICE_DATA.serviceid"
    db.querySQL(sql, reloadservice)


# ##################################################################################################################
def _reloadwssrv(keys=[]):
    '''
    重新加载WebService SERVICE数据
    @return:
    '''

    # sql查询回调函数
    def reloadservice(cur):
        field = ['serviceid', 'type', 'servicename', 'url', 'enabled', 'cachetype', 'origialurl', 'namespace',
                 'secret',
                 'msglog']

        for item in cur.fetchall():
            d = dict(zip(field, item))
            redistip.put2redis("SRV_URL_" + d["url"], d)
            if ("SRV_URL_" + d["url"]).encode(encoding="utf-8") in keys:
                keys.remove(("SRV_URL_" + d["url"]).encode(encoding="utf-8"))
            if settings.DEBUG:
                settings.infoLogger.info("app ws service,key:%s" % ("SRV_URL_" + d["url"]))

    sql = "select " \
          "USERVICE_DATA.SERVICEID, " \
          "USERVICE_DATA.TYPE, " \
          "USERVICE_DATA.SERVICENAME, " \
          "USERVICE_DATA.URL, " \
          "USERVICE_DATA.ENABLED, " \
          "USERVICE_DATA.CACHETYPE," \
          "USERVICE_WS.ORIGIALURL, " \
          "USERVICE_WS.NAMESPACE, " \
          "USERVICE_DATA.SECRET," \
          "USERVICE_DATA.MSGLOG " \
          "from USERVICE_DATA  " \
          "inner join USERVICE_WS on USERVICE_WS.serviceid=USERVICE_DATA.serviceid"
    db.querySQL(sql, reloadservice)


# ######################################################################################################################
def _getDict(schema, tablename):
    '''
    从Oracle获取数据字典
    @param schema:
    @param tablename:
    @return:
    '''
    if settings.SRVDATABASETYPE != 'oracle':
        return None
    dicts = db.querySQL2map("select table_name,owner,"
                            "column_name,data_type,data_length,"
                            "data_precision,Data_Scale,nullable "
                            "from all_tab_columns where owner='%s' and table_name='%s'" % (
                                schema.upper(), tablename.upper()))
    if len(dicts) == 0:
        return None
    return [
        dict(
                list(map(lambda x: [x, row[x]],
                         ['TABLE_NAME', 'OWNER', 'COLUMN_NAME', 'DATA_TYPE', 'DATA_LENGTH'])))
        for row in dicts]


# typemap = {1: u'WebService',
#            2: u'RESTful',
#            3: u'普通URL，HTTP GET方法',
#            4: u'普通URL，HTTP POST方法',
#            5: u'SQL服务',
#            6: u'数据封装服务',
#            7: u'redis数据缓存服务'}
#            8: u'云服务'


# ######################################################################################################################
def _getMeta(schema, tablename):
    '''
    从元数据库获取元数据
    @param schema:
    @param tablename:
    @return:
    '''
    ident = db.querySQL2map("SELECT IDENTID,"
                            "YSJBZ,"
                            "IDEDVER,"
                            "IDTITLE,"
                            "IDENTCODE,"
                            "IDABS,"
                            "IDPURP,"
                            "KEYWORD,"
                            "ISTATUS,"
                            "ADALANG,"
                            "DATACHAR,"
                            "TPCAT,"
                            "GTMEAN,"
                            "GTMEANBH,"
                            "FORMATNAME,"
                            "FORMATVER "
                            "FROM MD_IDENT_M where IDENTID='%s.%s'" % (schema.lower(), tablename.lower()),
                            dbid="mdu")

    if len(ident) == 0:
        return None
    fields = db.querySQL2map("SELECT IDENTID,CNNAME,ENNAME,VERSION,MS,LX,CD,GS,DW,ZY,GLSJJ,IS_PK,IS_MC "
                             "FROM MD_DATAMETA_M WHERE IDENTID='%s.%s'" % (schema.lower(), tablename.lower()),
                             dbid="mdu")

    if len(fields) == 0:
        return None
    return {
        'tablename': ident[0]["IDTITLE"],
        'tableid': ident[0]["IDENTCODE"],
        'fields': list(map(lambda x: (
            {'name': x["CNNAME"], 'code': x["ENNAME"], 'unit': x["DW"], 'type': x["LX"], 'length': x["CD"]}),
                           fields))
    }


####################################################################################################################
def _getAllSrv():
    '''
    返回除WS和REST外所有服务type=3,4,5,6,7
    @return:
    '''
    datas = db.querySQL2map(
            "SELECT SERVICEID,TYPE,SERVICENAME,URL,ENABLED,CACHETYPE,SECRET,MSGLOG FROM USERVICE_DATA WHERE type<>1 and type<>2 and type<>8")
    result = []
    for data in datas:
        result.append(_getServiceFromDB(data))
    return result


####################################################################################################################
def _reloaddatatable(keys=[]):
    srvs = _getAllSrv()  # type=3,4,5,6,7
    for srv in srvs:
        if not (srv is None):
            redistip.putSrv2redis(srv, None, keys)
            if settings.DEBUG:
                settings.infoLogger.info("add service,key:%s" % ("SRV_URL_" + str(srv['url'])))


####################################################################################################################
def _getServiceFromDB(data):
    '''
    返回一个服务，data是非RS和REST的服务数据
    @param data:
    @return:
    '''
    result = {'serviceid': data["SERVICEID"],
              'serviceName': data["SERVICENAME"],
              'enabled': data["ENABLED"],
              'type': data["TYPE"],
              'url': data["URL"],
              'secret': data["SECRET"],
              'msglog': data["MSGLOG"],
              'cachetype': data["CACHETYPE"],
              }
    if data["TYPE"] == 5:
        # QSFramework
        dbt = db.querySQL2map(
                "SELECT SERVICEID, SQL, CREATOR,DATASOURCE FROM USERVICE_SQL WHERE SERVICEID=%s" % data[
                    "SERVICEID"])

        if len(dbt) == 0:
            return None
        result["sql"] = dbt[0]["SQL"]
        result["datasource"] = dbt[0]["DATASOURCE"]

        dbt = db.querySQL2map(
                "SELECT ID,SERVICEID,FIELDNAME,FIELDTYPE,CATALOG,FIELDDESC,FIELDDEFAULT FROM USERVICE_DATA_FIELD WHERE SERVICEID=%s" %
                data["SERVICEID"])

        if len(dbt) == 0:
            return result
        result["param"] = []
        for p in dbt:
            result["param"].append({
                'name': p["FIELDNAME"],
                'type': p["FIELDTYPE"],
                'desc': p["FIELDDESC"],
                'cagalog': p["CATALOG"],
                'default': p["FIELDDEFAULT"]
            })
        return result
    if data["TYPE"] == 6:
        # DBTable
        dbt = db.querySQL2map(
                "SELECT SERVICEID,SCHEMANAME,TABLENAME,INNERJOIN,FIELDLIST,DATASOURCE FROM USERVICE_TABLE WHERE SERVICEID=%s" %
                data["SERVICEID"])
        if len(dbt) == 0:
            return None

        result['schemaName'] = dbt[0]["SCHEMANAME"]
        result['tableName'] = dbt[0]["TABLENAME"]
        result['dict'] = _getDict(dbt[0]["SCHEMANAME"], dbt[0]["TABLENAME"])
        result['meta'] = _getMeta(dbt[0]["SCHEMANAME"], dbt[0]["TABLENAME"])
        result['fieldlist'] = dbt[0]["FIELDLIST"]
        result['innerjoin'] = dbt[0]["INNERJOIN"]
        result["datasource"] = dbt[0]["DATASOURCE"]
        return result
    if data["TYPE"] == 7:
        dbt = db.querySQL2map(
                "SELECT SERVICEID,SCHEMANAME,TABLENAME,INNERJOIN,FIELDLIST FROM USERVICE_TABLE WHERE SERVICEID=%s" %
                data["SERVICEID"])
        if len(dbt) == 0:
            return None
        result['schemaName'] = dbt[0]["SCHEMANAME"]
        result['tableName'] = dbt[0]["TABLENAME"]
        result['fieldlist'] = dbt[0]["FIELDLIST"]
        result['innerjoin'] = dbt[0]["INNERJOIN"]
        return result
    return None


####################################################################################################################
def _reloadCacheData():
    ks = GLOBAREDIS.keys("CACHE_*")
    for k in ks:
        GLOBAREDIS.delete(k)
    for item in settings.CACHE_TABLES:
        key = "CACHE_" + item[3] + "_"
        data = db.querySQL2map(item[0], None, item[1])
        for d in data:
            k = key + '_'.join(map(lambda x: d[x], item[2]))
            if (item[4] is None) or (len(item[4]) == 0):
                redistip.put2redis(k, d)
            elif len(item[4]) == 1:
                redistip.putStr2redis(k, d[item[4][0]])
            else:
                redistip.put2redis(k, dict([[r, d[r]] for r in item[4]]))