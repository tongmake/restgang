
import service.utils as utils
from mgr.redistip import GLOBAREDIS
from apscheduler.schedulers.background import BackgroundScheduler
import jobs.msglog as msglog
import jobs.hugesqlservice as hugesqlservie
import threading

def reloadRedis_appkey():
    utils._reloadAppky(None)
    utils._reloadPlant()


def reloadRedis_DataSource():
    utils.reloadDataSource()


def reloadRedis_CacheData():
    utils._reloadCacheData()


def reloadRedis_ws():
    '''
    @return:
    '''
    ks = GLOBAREDIS.keys("SRV_URL_*")
    ks = ks + GLOBAREDIS.keys("SRV_ID_*")
    utils._reloadwssrv(ks)  # type==1
    utils._reloaddatatable(ks)  #
    utils._reloadrestsrv(ks)  # type==2
    hugesqlservie.reloadhugeSQL(ks)
    for k in ks:
        GLOBAREDIS.delete(k)


def initJobs():
    scheduler = BackgroundScheduler()  # 后台运行调度程序
    scheduler.add_job(reloadRedis_ws,           "interval", seconds=10)  # 时间间隔方式执行调度
    scheduler.add_job(reloadRedis_appkey,       "interval", seconds=60)  # 时间间隔方式执行调度
    scheduler.add_job(reloadRedis_DataSource,   "interval", seconds=60)  # 时间间隔方式执行调度
    scheduler.add_job(reloadRedis_CacheData,    "interval", seconds=600)  # 时间间隔方式执行调度
    #scheduler.add_job(msglog.msgLog2DB, "interval", seconds=2)  # 时间间隔方式执行调度
    scheduler.start()
    t2 = threading.Thread(target=msglog.msgLog2DB)
    t2.start()

