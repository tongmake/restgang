import settings
import mgr.redistip as redis

if __name__ == "__main__":
    list=[]
    count=0
    mina=999999999999
    maxa=0
    ct=0
    for key in redis.getKeys("SRV_ID_*"):
        srv=redis.getfromRedis(key)
        c=redis.getStrfromRedis("SRV_COUNT_" + key.decode()[7:])
        if(not(c is None)):
            count=count+int(c)
        mi=redis.getStrfromRedis("SRV_MINTIME_" + key.decode()[7:])
        if(not(mi is None)):
            if(float(mi)<mina):
                mina=float(mi)
        ma=redis.getStrfromRedis("SRV_MAXTIME_" + key.decode()[7:])
        if(not(ma is None)):
            if(float(ma)>maxa):
                maxa=float(ma)
        s={
            "id":srv["serviceid"],
            "name":srv["serviceName"],
            "url":srv["url"],
            "type":srv["type"],
            "count": c,
            "maxtime": ma,
            "mintime": mi
        }

        print(s)
    print("count:"+str(count))
    print("max time:"+str(maxa))
    print("min time:" + str(mina))