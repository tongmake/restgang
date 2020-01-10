# coding=utf-8
__author__ = 'menghui'
import clouds.cloudservice as cloudservice

urls = [
    (r"/clouds/(\w+)", cloudservice.CloudSrvHandler)
]
