#=======================================================================================================================
#
# python3 httpclient.py --running=redis 表示按照redis任务模式执行，定时执行reloadRedis.initJobs()中的程序，定时时间在setting中的
#                                        RELOADREDISTIME参数定义，单位秒
#   日志保存在启动目录中，不同端口号保存在不同文件中，reids模式运行保存在独立文件中
#=======================================================================================================================

__author__ = 'menghui'
# coding=utf-8
import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import mgr.redistip
import mgr.url
import service.url
import ResSearch.url
import clouds.url
import settings
import traceback
from   tornado.options import define, options
import jobs.reloadRedis as reloadRedis
import service.utils as utils
import logging
import time
import pymssql
from DBUtils.PooledDB import PooledDB


define("port", default=8000, help="run on the given port", type=int)
define("running", default="reload", type=str)
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


def callback():
    print("reload redis")


def mainrun():
    # ==================================================================================================================
    # 配置日志
    #  AU：云服务日志
    #  SR：数据服务日志
    format = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    formatter = logging.Formatter(format)
    logging.basicConfig(level=logging.DEBUG,
                        format=format,
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='root' + str(options.port) + '.log',
                        filemode='w')

    infoHandler = logging.FileHandler("logs/infoLog" + str(options.port) + '.log', 'a')
    infoHandler.setLevel(logging.INFO)
    infoHandler.setFormatter(formatter)
    settings.infoLogger = logging.getLogger("infoLog" + str(options.port) + '.log')
    settings.infoLogger.setLevel(logging.INFO)
    settings.infoLogger.addHandler(infoHandler)

    errorHandler = logging.FileHandler("logs/errorLog" + str(options.port) + '.log', 'a')
    errorHandler.setLevel(logging.ERROR)
    errorHandler.setFormatter(formatter)
    settings.errorLogger = logging.getLogger("errorLog" + str(options.port) + '.log')
    settings.errorLogger.setLevel(logging.ERROR)
    settings.errorLogger.addHandler(errorHandler)

    debugHandler = logging.FileHandler("logs/debugLog" + str(options.port) + '.log', 'a')
    debugHandler.setLevel(logging.DEBUG)
    debugHandler.setFormatter(formatter)
    settings.debugLogger = logging.getLogger("debugLog" + str(options.port) + '.log')
    settings.debugLogger.setLevel(logging.DEBUG)
    settings.debugLogger.addHandler(debugHandler)


    urls = [
    ]
    urls += mgr.url.urls
    urls += service.url.urls
    urls += ResSearch.url.urls
    urls += clouds.url.urls
    tornado.options.parse_command_line()
    settings.infoLogger.info("===========================================")
    settings.infoLogger.info("        rEstgAng starting")
    settings.infoLogger.info("              V1.0b")
    settings.infoLogger.info("===========================================")





    settings.infoLogger.info("Listening port:%s" % options.port)
    settings.infoLogger.info("")
    settings.infoLogger.info("DATABASE SETTING:")
    utils.reloadDataSource()
    ids = settings.DATABASES.keys()
    for key in ids:
        item = settings.DATABASES[key]
        settings.infoLogger.info("  ID:%s" % key)
        settings.infoLogger.info("      host:%s:%s/%s" % (item["HOST"], item["PORT"], item["NAME"]))
        settings.infoLogger.info("      username:%s" % item["USER"])

        app = tornado.web.Application(
                debug=True,
                handlers=urls,
                template_path=os.path.join(os.path.dirname(__file__), "templates"),
                static_path=os.path.join(os.path.dirname(__file__), "static"),
                autoreload=True
        )

    if not(os.path.exists(settings.MSGLOGPATH)):
        print("message log file path not exist!"+settings.MSGLOGPATH)
        return

    reboottimes = 0
    while True:
        try:
            http_server = tornado.httpserver.HTTPServer(app)
            http_server.listen(options.port)
            if options.running != "run":
                reloadRedis.initJobs()
            tornado.ioloop.IOLoop.instance().start()
        except Exception as e:
            reboottimes += 1
            if reboottimes > 3:
                settings.errorLogger.error("服务引擎发生致命错误,重新启动三次后仍然错误，系统退出")
                return
            settings.errorLogger.error("服务引擎发生致命错误,3秒后系统尝试重新启动")
            settings.errorLogger.error(traceback.format_exc())
        time.sleep(3)


if __name__ == "__main__":
    mainrun()
    #db_conn=pymssql.connect(server="192.168.1.128", user="sa", password="qweqwe1", database="stu", charset="GBK")
    # args = (0, 0, 0,5, 0, 0, None)
    # conn_kwargs = {"host": "192.168.1.128" , "user": "sa", "password": "qweqwe1","database": "stu","charset":"GBK"}
    # pool=PooledDB(pymssql, *args, **conn_kwargs)
    # db_conn = pool.connection()
    # cur = db_conn.cursor()
    # cur.execute("select * from jeda_menu")
    # resList = cur.fetchall()
    # for i in resList:
    #     print(i)
    # db_conn.close()
