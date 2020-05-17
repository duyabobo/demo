#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

from tornado.concurrent import run_on_executor

from base_handler import BaseHandler
from utils.time_logger import time_logger

from celery_tasks.task1 import add
from celery_tasks.celery import app


class ExampleHandler5(BaseHandler):
    # 这里的例子用来实验 celery
    __model__ = ''

    def __init__(self, application, request, **kwargs):
        self.executor = application.executor
        super(ExampleHandler5, self).__init__(application, request, **kwargs)

    @run_on_executor
    @time_logger
    def get(self):
        """注释
        """
        para_name = self.get_argument('para_name', default='default')  # 接受参数，如果必传就不给出默认值
        print(para_name)
        add.delay(2, 2)  # 适合 celery 任务代码和 业务代码放到一个代码仓库里
        # If the task isn’t registered in the current process you can use
        app.send_task('celery_tasks.task1.add', (2, 2))  # 可以实现 celery 代码和 业务代码不在一个仓库的异步调用
        resp_data = {'msg': 'abc', 'icp': '京ICP备20005743号-1'}
        return self.response(resp_data=resp_data)
