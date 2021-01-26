#!/usr/bin/env python
# coding=utf-8
# 耗时日志
import functools
import time

from tornado.log import gen_log


def time_logger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start_time = time.time()
            ret = func(*args, **kwargs)
            end_time = time.time()
            log_msg = '耗时日志：func_name[%s] args[%s] kwargs[%s] ret[%s] running_time[%s]' \
                  % (func.__name__, args, kwargs, ret, end_time-start_time)
            gen_log.info(log_msg)
            print(log_msg)
            return ret
        except:
            print 'error'
            return
    return wrapper
