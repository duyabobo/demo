#! /usr/bin/env python
# -*- coding: utf-8 -*- 
import functools

from tornado.concurrent import run_on_executor

from utils.auth_checker import auth_checker
from utils.time_logger import time_logger


def monitor(func):
    """多个装饰器，整合成一个。"""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        __func = run_on_executor(time_logger(auth_checker(func)))
        ret = __func(self, *args, **kwargs)
        return ret
    return wrapper
