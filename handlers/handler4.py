#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json
import time

import requests
from tornado.web import RequestHandler

from utils.concurrency import ConcurrencyExecutor
from utils.time_logger import time_logger
from utils.monitor import monitor

APPLE_AUTH_KEY_URL = 'https://appleid.apple.com/auth/keys'
BAIDU_URL = 'https://www.baidu.com'


class ExampleHandler4(RequestHandler):
    # 这里的例子用来实验 monitor 和 auth_checker
    __model__ = ''

    def __init__(self, application, request, **kwargs):
        self.executor = application.executor
        super(ExampleHandler4, self).__init__(application, request, **kwargs)

    @time_logger
    def __request_apple(self, url):
        """发出某个url的网络请求"""
        ret = requests.get(url)
        return len(ret.text)

    @time_logger
    def __request_baidu(self, url):
        """发出某个url的网络请求"""
        ret = requests.get(url)
        return len(ret.text)

    @monitor
    def get(self):
        """注释
        """
        para_name = self.get_argument('para_name', default='default')  # 接受参数，如果必传就不给出默认值
        print(para_name)
        con_exe = ConcurrencyExecutor()
        con_exe.add_job(self.__request_apple, APPLE_AUTH_KEY_URL)
        con_exe.add_job(self.__request_baidu, BAIDU_URL)
        con_exe.add_job(time.sleep, 6)
        ret = con_exe()
        # ret = self.__request_some_url(APPLE_AUTH_KEY_URL)
        response = {'msg': 'abc', 'icp': '京ICP备20005743号-1', 'ret': ret}
        return response
