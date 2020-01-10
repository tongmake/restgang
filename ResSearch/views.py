# coding=utf-8
import math
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.escape

import mgr.dbtip as db
import ResSearch.Resource_Search as resSearch


# 定义相应/ResSearch/的类
class resource_search(tornado.web.RequestHandler):
    def get(self):
        self.render(u"ResSearch/index.html")

    def post(self):
        key = self.get_argument('key')
        type = self.get_argument('type')

        page_num = 1
        page_size = 20
        try:
            page_num = int(self.get_argument('page_num'))

        except:
            page_num = 1


        if type.strip() == '' or type is None:
            type = 'ROT'

        keylist = key.split()

        default_dbcfg = resSearch.getDBcfg()

        result_list = []
       # fenye_list = []
        if type == 'DAT' or type == 'ROT':
            sql = """select a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,b.IDENTID,c.IDTITLE
                            from RD_JGHMLB a  LEFT JOIN RD_DAT b ON b.MLBH = a.MLBH  LEFT JOIN MD_IDENT_M c ON
                            c.IDENTID = b.IDENTID  """
            sql = " ".join([sql, "WHERE a.RSTYPE = '{typeone}'".format(typeone='DAT')])
            for i in [i.strip() for i in keylist if len(keylist) > 0]:
                where_or = "AND (a.MLMC like '%{keyone}%' or c.IDTITLE like '%{keyone}%') ".format(keyone=i)
                sql = " ".join([sql, where_or])
                result_list.extend(db.querySQL2map(sql, None, "mdu"))
            else:
                result_list.extend(db.querySQL2map(sql, None, "mdu"))


        if type == 'DOC' or type == 'ROT':
            pass

        if type == 'COM' or type == 'ROT':
            sql = """select a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.SUBASS_NAME,c.SUBASS_PATH,c.SUBASS_SIZE,c.SUBASS_TYPE FROM RD_JGHMLB a
                       LEFT JOIN RD_COM b ON b.MLBH = a.MLBH  LEFT JOIN {bjntu}.P_AT_SUBASSEMBLY c ON c.SUBASS_ID = b.ASSID
                       where a.RSTYPE = 'COM' """.format(bjntu=default_dbcfg["USER"])
            if len(keylist)>0:
                for i in [i.strip() for i in keylist if len(keylist) > 0]:
                    where_or = " AND (a.MLMC like '%{keyone}%' OR c.SUBASS_NAME like '%{keyone}%' or c.SUBASS_PATH like '%{keyone}%' or c.SUBASS_SIZE like '%{keyone}%' or c.SUBASS_TYPE like '%{keyone}%') ".format(keyone=i)
                    sql = " ".join([sql,where_or])
                    result_list.extend(db.querySQL2map(sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]
            else:
                result_list.extend(db.querySQL2map(sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

        if type == 'APP' or type == 'ROT':
            sql = """select a.MLBH,a.MLMC,a.RSTYPE,b.APPID,c.APP_IP,c.APP_NAME,c.APP_URL FROM RD_JGHMLB a
                     LEFT JOIN RD_APP b ON a.MLBH = b.MLBH  LEFT JOIN {bjntu}.p_appinfo c ON c.APP_ID = b.APPID
                      where a.RSTYPE = 'APP' """.format(bjntu=default_dbcfg["USER"])
            if len(keylist) > 0:
                for i in [i.strip() for i in keylist if len(keylist) > 0]:
                    where_or = "AND (a.MLMC like '%{keyone}%' or c.APP_ID like '%{keyone}%' or c.APP_NAME like '%{keyone}%' or c.APP_URL like '%{keyone}%') ".format(
                        keyone=i)
                    sql = " ".join([sql, where_or])
                    result_list.extend(db.querySQL2map(sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]
            else:
                result_list.extend(db.querySQL2map(sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]
        if type == 'USR' or type == 'ROT':
            sql = """SELECT a.MLBH, a.MLMC, a.FJMLBH, a.STATUS, a.RSTYPE,c.USER_ID,c.USER_NAME,c.USER_GENDER,d.ORG_NAME  FROM RD_JGHMLB a
                      LEFT JOIN RD_USR b on a.MLBH = b.MLBH LEFT JOIN {bjntu}.jeda_user c on  c.USER_ID = b.USER_ID
                      RIGHT JOIN {bjntu}.JEDA_ORG d  on c.ORG_ID =d.ORG_ID WHERE a.RSTYPE = 'USR' """.format(
                bjntu=default_dbcfg["USER"])
            if len(keylist) > 0:
                for i in [i.strip() for i in keylist if len(keylist) > 0]:
                    where_or = """ AND (a.MLMC like '%{keyone}%'
                                    or c.LOGIN_NAME like '%{keyone}%'
                                    or c.USER_NAME like '%{keyone}%'
                                    or d.ORG_NAME like '%{keyone}%')""".format(keyone=i)
                    sql = " ".join([sql, where_or])
                    result_list.extend(db.querySQL2map(sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]
            else:
                result_list.extend(db.querySQL2map(sql, None, "mdu"))
        if type == 'SRV' or type == 'ROT':
            if len(keylist) > 0:
                for i in [i.strip() for i in keylist if len(keylist) > 0]:
                    """用于查询webservice型服务"""
                    WS_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,d.ORIGIALURL,c.ENABLED,c.SECRET,d.NAMESPACE  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_WS  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                 AND (a.MLMC like '%{keyone}%' OR c.SERVICENAME like '%{keyone}%') """.format(bjntu=default_dbcfg["USER"], keyone=i)
                    result_list.extend(db.querySQL2map(WS_sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                    """用于查询表封装服务"""
                    table_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,d.SCHEMANAME,d.TABLENAME  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_TABLE  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                 AND (a.MLMC like '%{keyone}%' OR c.SERVICENAME like '%{keyone}%') """.format(
                        bjntu=default_dbcfg["USER"], keyone=i)
                    result_list.extend(db.querySQL2map(table_sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                    """用于查询数据查询服务"""
                    sql_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,d.SQL  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_SQL  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                 AND (a.MLMC like '%{keyone}%' OR c.SERVICENAME like '%{keyone}%') """.format(
                        bjntu=default_dbcfg["USER"], keyone=i)
                    result_list.extend(db.querySQL2map(sql_sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                    """用于查询rest服务和urlget以及urlpost服务"""
                    rest_sql = """ SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,
                                d.ORIGIALURL  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_REST  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                 AND (a.MLMC like '%{keyone}%' OR c.SERVICENAME like '%{keyone}%') """.format(
                        bjntu=default_dbcfg["USER"], keyone=i)
                    result_list.extend(db.querySQL2map(rest_sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                    """用于大平台查询服务"""
                    sql_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,d.SERVICEID,d.ORIGIALURL,d.SERVICETYPE,d.ORIGIALSECURITY,d.META,c.SERVICENAME,c.NOTE,c.TYPE,c.URL,c.ENABLED,c.SECRET,f.AREA  FROM RD_JGHMLB a
                                    RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH
                                    RIGHT JOIN {bjntu}.USERVICE_DATA  c ON c. SERVICEID = b.SERVICEID
                                    RIGHT JOIN {bjntu}.USERVICE_CLOUD d on d.SERVICEID = c.SERVICEID
                                    RIGHT JOIN {bjntu}.USERVICE_CLOUDROLE e ON e.SERVICEID = d.SERVICEID
                                    RIGHT JOIN {bjntu}.P_PLATFORM f ON f.PLATID = e.PLATID
                                    where a.RSTYPE = 'SRV'
                                     AND (a.MLMC like '%{keyone}%' OR c.SERVICENAME like '%{keyone}%')""".format(
                        bjntu=default_dbcfg["USER"], keyone=i)
                    result_list.extend(db.querySQL2map(sql_sql, None, "mdu"))
                    result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]


            else:
                WS_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,d.ORIGIALURL,d.NAMESPACE  FROM RD_JGHMLB a
                            RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                            {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                            RIGHT JOIN {bjntu}.USERVICE_WS  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                              """.format(bjntu=default_dbcfg["USER"])
                result_list.extend(db.querySQL2map(WS_sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                """用于查询表封装服务"""
                table_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,d.SCHEMANAME,d.TABLENAME  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_TABLE  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                """.format(bjntu=default_dbcfg["USER"])
                result_list.extend(db.querySQL2map(table_sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                """用于查询数据查询服务"""
                sql_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,d.SQL  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_SQL  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                """.format(bjntu=default_dbcfg["USER"])
                result_list.extend(db.querySQL2map(sql_sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                """用于查询rest服务和urlget以及urlpost服务"""
                rest_sql = """ SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.NOTE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL,c.ENABLED,c.SECRET,d.ORIGIALURL  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH RIGHT JOIN
                                {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_REST  d ON d. SERVICEID = c.SERVICEID where a.RSTYPE = 'SRV'
                                """.format(bjntu=default_dbcfg["USER"])
                result_list.extend(db.querySQL2map(rest_sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]
                # sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,c.SERVICEID,c.SERVICENAME,c.TYPE,c.URL  FROM RD_JGHMLB a
                #             LEFT JOIN RD_SRV b on a.MLBH = b.MLBH LEFT JOIN
                #             {bjntu}.USERVICE_DATA c on c.SERVICEID = b.SERVICEID
                # result_list.extend(db.querySQL2map(sql, None, "mdu"))
                # result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

                """用于大平台查询服务"""
                sql_sql = """SELECT a.MLBH,a.MLMC,a.FJMLBH,a.STATUS,a.RSTYPE,d.SERVICEID,d.ORIGIALURL,d.SERVICETYPE,d.ORIGIALSECURITY,d.META,c.SERVICENAME,c.NOTE,c.TYPE,c.URL,c.ENABLED,c.SECRET,f.AREA  FROM RD_JGHMLB a
                                RIGHT JOIN RD_SRV b on a.MLBH = b.MLBH
                                RIGHT JOIN {bjntu}.USERVICE_DATA  c ON c. SERVICEID = b.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_CLOUD d on d.SERVICEID = c.SERVICEID
                                RIGHT JOIN {bjntu}.USERVICE_CLOUDROLE e ON e.SERVICEID = d.SERVICEID
                                RIGHT JOIN {bjntu}.P_PLATFORM f ON f.PLATID = e.PLATID
                                where a.RSTYPE = 'SRV'
                                """.format(bjntu=default_dbcfg["USER"])
                result_list.extend(db.querySQL2map(sql_sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

        if type == 'OTH' or type == 'ROT':
            sql = """SELECT a.MLBH, a.MLMC,a. FJMLBH, a.STATUS, a.RSTYPE,b.ATTNAME,b.ATTTYPE,b.ATTMEMO,c.ATTVALUE,c.RESID
                      FROM RD_JGHMLB a LEFT JOIN RD_OTH_DICT b on b.MLBH = a.MLBH
                      LEFT JOIN  RD_OTH_RES c on c.ATTNAME = b.ATTNAME  INNER JOIN RD_JGHMLB d on a.MLBH = c.MLBH where a.RSTYPE = 'OTH' """
            for i in [i.strip() for i in keylist if len(keylist) > 0]:
                where_or = " AND (a.MLMC like '%{keyone}%' OR b.ATTNAME like '%{keyone}%') ".format(keyone=i)
                sql = " ".join([sql,where_or])
                result_list.extend(db.querySQL2map(sql, None, "mdu"))
                result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]

        # 这句话是去重的
        result_list = [dict(t) for t in set([tuple(d.items()) for d in result_list])]
        self.render(u"ResSearch/indexpost.html",
                    item=result_list[(page_num-1)*20:page_num*20+1],p_num=page_num,p_next=page_num+1,p_air=page_num-1,p_last=math.ceil(len(result_list)/20.0),p_type=type,p_nums=len(result_list),keylist_len=len(keylist))
        #result_list[0:1] = fenye_list
    def write_error(self, status_code, **kwargs):
        self.write("Gosh darnit, user! You caused a %d error." % status_code)



