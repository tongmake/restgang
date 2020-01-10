# coding=utf-8
__author__ = 'menghui'
import mgr.views as views

urls = [
    (r"/mgr/(\w+)", views.MgrHandler),
    (r"/redis/(\w+)", views.RedisHanler),
    (r"/redis/", views.RedisIndex)
    #(r"/redis/del",views.RedisOtherHanler)
]
