#! /usr/bin/env python
# -*- coding: utf-8 -*-
import json

from sqlalchemy.orm import sessionmaker
from tornado.web import RequestHandler

from utils.const import RESP_OK
from utils.database import redis_cli


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        self.application = application
        self.executor = application.executor
        self.redis_cli = redis_cli
        self._db_session = None
        self.user_info = None
        self.user_id = None
        super(BaseHandler, self).__init__(self.application, request, **kwargs)

    @property
    def db_session(self):
        """
        数据库链接在需要的时候才会初始化, 而且不会重复初始化
        :return:
        """
        if hasattr(self, '_db_session') and self._db_session:
            return self._db_session
        self._db_session = sessionmaker(bind=self.application.engine)()
        return self._db_session

    def response(self, resp_data=None, resp_status=RESP_OK):
        if not resp_data:
            resp_data = {}
        resp_data.update(self.user_info)  # 每个接口都返回用户当前是否是最新登陆的设备，客户端可酌情提醒是否重新登陆
        resp_data.update(resp_status)
        resp = json.dumps(resp_data)
        self.write(resp)
        self.finish_db_operation(resp_status)
        return resp

    def finish_db_operation(self, resp_normal):
        """
        关闭数据库链接
        :return:
        """
        if resp_normal['code'] == 0:
            self.db_session.commit()
        else:
            self.db_session.rollback()
        self.db_session.close()
