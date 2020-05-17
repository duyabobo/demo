#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

from tornado.concurrent import run_on_executor

from base_handler import BaseHandler
from utils.concurrency import ConcurrencyExecutor
from utils.time_logger import time_logger


class ExampleHandler2(BaseHandler):
    # 这里的例子用来实验 time_logger 和 ConcurrencyExecutor
    __model__ = ''

    def __init__(self, application, request, **kwargs):
        self.executor = application.executor
        super(ExampleHandler2, self).__init__(application, request, **kwargs)

    @run_on_executor
    @time_logger
    def get(self):
        """注释
        """
        print(time.time())
        para_name = self.get_argument('para_name', default='default')  # 接受参数，如果必传就不给出默认值
        print(para_name)
        con_exe = ConcurrencyExecutor()
        con_exe.add_job(time.sleep, 10)
        con_exe.add_job(time.sleep, 10)
        con_exe()
        resp_data = {'msg': 'abc', 'icp': '京ICP备20005743号-1'}
        return self.response(resp_data=resp_data)
