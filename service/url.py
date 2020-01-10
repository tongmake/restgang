# coding=utf-8
__author__ = 'menghui'
import service.restview as restview
import service.sqlService as sqlService

urls = [
    (r"/services/(\w+)", restview.ProxyHandler),
    (r"/ds", sqlService.sqlSrvHandler)
]
