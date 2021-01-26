#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

# from tornado.concurrent import run_on_executor
from tornado import gen
from base_handler import BaseHandler


class ExampleHandler1(BaseHandler):
    # 这里的例子用来实验 run_on_executor 的作用
    # 值得注意的是，如果本地启动了服务之后，使用浏览器打开多个窗口，同时请求访问这个接口，效果确是串行的！
    # 通过服务器这边日志可以显示串行的接受到请求，也就是说这是因为浏览器的一种防止并发行为。
    # 可以在请求这个接口的时候，后面加上不同的请求参数，就可以看到异步非阻塞效果了！！
    __model__ = ''

    @gen.coroutine
    def get(self):
        """注释
        """
        print(time.time())
        a = 1/0
        para_name = self.get_argument('para_name', default='default')  # 接受参数，如果必传就不给出默认值
        print(para_name)
        time.sleep(10)
        resp_data = {'msg': 'abc', 'icp': '京ICP备20005743号-1'}
        return self.response(resp_data=resp_data)
