#coding=utf-8
import cx_Oracle

import settings


# class ResSearchDB():
#     def getConnect(self,dbid="default"):
#         """
#             连接数据库，根据dbid
#         @param dbid:
#         @return:
#         """
#         # if dbid is None:
#         #     dbid = "default"
#
#         dbcfg = settings.DATABASES[dbid]
#         con = cx_Oracle.connect("".join([dbcfg["USER"],'/',dbcfg["PASSWORD"],'@',dbcfg['HOST'],'/',dbcfg["NAME"]]))
#         return con
#
#     def querySql(self,sql,callBack,param=None,dbid='default'):
#         """
#         执行sql，成功后调用callBack
#         @param sql:
#         @param callBack:
#         @param param:
#         @param dbid:
#         @return:
#         """
#         conn = self.getConnect(dbid)
#         cur = None
#         if not isF

def getDBcfg(dbid="default"):
    return settings.DATABASES[dbid]