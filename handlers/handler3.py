#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

import requests
from tornado.concurrent import run_on_executor

from base_handler import BaseHandler
from utils.concurrency import ConcurrencyExecutor
from utils.time_logger import time_logger

APPLE_AUTH_KEY_URL = 'https://appleid.apple.com/auth/keys'
BAIDU_URL = 'https://www.baidu.com'


class ExampleHandler3(BaseHandler):
    # 这里的例子用来实验 time_logger 和 ConcurrencyExecutor
    __model__ = ''

    def __init__(self, application, request, **kwargs):
        self.executor = application.executor
        super(ExampleHandler3, self).__init__(application, request, **kwargs)

    @time_logger
    def __request_apple(self, url):
        """发出某个url的网络请求"""
        ret = requests.get(url, timeout=3)
        return len(ret.text)

    @time_logger
    def __request_baidu(self, url):
        """发出某个url的网络请求"""
        ret = requests.get(url, timeout=3)
        return len(ret.text)

    @run_on_executor
    @time_logger
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
        resp_data = {'msg': 'abc', 'icp': '京ICP备20005743号-1', 'ret': ret}
        return self.response(resp_data=resp_data)
