#!/usr/bin/env python
# -*-coding: utf-8 -*-
import pickle

from peewee import ModelSelect
from tornado.web import RequestHandler

WHITE_LIST = ['::1']  # 内部服务器ip列表


class Handler(object):

    def __init__(self, func_list=None):
        if func_list is None:
            func_list = []
        self.func_list = func_list

    @classmethod
    def object_2_dict(cls, input_object):
        """将结构体对象序列化为dict结构"""
        for ins in [list, tuple, set]:
            if isinstance(input_object, ins):
                return ins(cls.object_2_dict(v) for v in input_object)
        if isinstance(input_object, dict):
            return {k: cls.object_2_dict(v) for k, v in input_object.items()}
        if isinstance(input_object, ModelSelect):
            return [cls.object_2_dict(v) for v in input_object]
        if hasattr(input_object, '__data__'):  # peewee 单个查询对象
            return cls.object_2_dict(input_object.__data__)
        if hasattr(input_object, '__dict__'):  # node
            return cls.object_2_dict(input_object.__dict__)

        return input_object

    @classmethod
    def get_rpc_handler(cls, module, func):
        class RPCHandler(RequestHandler):
            def post(self):
                if self.request.remote_ip not in WHITE_LIST:
                    return self.response({'error_no': -1, 'error_msg': 'remote_ip error'})
                res = func(**pickle.loads(self.request.body))
                return self.response({'error_no': 0, 'data': cls.object_2_dict(res)})

            def response(self, res):
                return self.write(pickle.dumps(res))

        path = '.{}.{}.{}$'.format(module.__module__, module.__name__, func.__name__)
        url = path.replace('.', '/')
        return url, RPCHandler

    @property
    def handlers(self):
        _rpc_handlers = []
        for module, func in self.func_list:
            _rpc_handlers.append(self.get_rpc_handler(module, func))
        return _rpc_handlers
