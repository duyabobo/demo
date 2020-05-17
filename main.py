#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
import sys

import tornado.httpserver
import tornado.ioloop
import tornado.web
# 这个并发库, python3 自带, python2 需要: pip install futures
from concurrent.futures import ThreadPoolExecutor

from urls import handlers
from utils.database import engine

reload(sys)
sys.setdefaultencoding('utf-8')


def main():
    port = 9999
    debug = True

    application = tornado.web.Application(handlers, **{
        'debug': debug,
        'template_path': 'template',
        'static_path': 'static',
    })
    application.executor = ThreadPoolExecutor(10)
    application.engine = engine
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    print ('>>>>> Starting development server at http://localhost:{}/ <<<<<'.format(port))
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
