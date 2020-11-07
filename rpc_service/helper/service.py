#!/usr/bin/env python
# -*-coding: utf-8 -*-
import json
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
    def get_rpc_handler(cls, module, func_name):
        class RPCHandler(RequestHandler):
            def post(self):
                if self.request.remote_ip not in WHITE_LIST:
                    return
                func = getattr(module, func_name, None)
                if not func:
                    return
                res = func(**json.loads(self.request.body))
                return self.write(pickle.dumps(cls.object_2_dict(res)))

        path = '.{}.{}.{}$'.format(module.__module__, module.__name__, func_name)
        url = path.replace('.', '/')
        return url, RPCHandler

    @property
    def handlers(self):
        _rpc_handlers = []
        for module, func_name in self.func_list:
            _rpc_handlers.append(self.get_rpc_handler(module, func_name))
        return _rpc_handlers
