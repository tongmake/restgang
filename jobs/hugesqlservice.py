import os
import codecs
import settings

import json
import mgr.redistip as redistip

def reloadhugeSQL(keys):
    servicefile =settings.HUGESQLPATH + "/services.json"
    if not(os.path.exists(servicefile)):
        return
    f=codecs.open(servicefile,'r','utf-8')
    try:
        services=json.load(f)
        for item in services:

           if not(item["sqlfile"] is None):
                filename=settings.HUGESQLPATH + "/"+item["sqlfile"]
                if not(os.path.exists(filename)):
                    continue
                fsql=codecs.open(filename,'r','utf-8')
                try:
                    item["sql"]=fsql.read()

                except Exception as e2:
                    pass
                finally:
                    fsql.close()
                redistip.putSrv2redis(item,None,keys)
    except  Exception as e:
        pass
    finally:
        f.close()

if __name__ == "__main__":
    reloadhugeSQL()