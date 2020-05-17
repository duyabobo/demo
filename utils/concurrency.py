#!/usr/bin/env python
# coding=utf-8
# 并发
import gevent
from gevent import monkey
monkey.patch_all()


class ConcurrencyExecutor(object):
    def __init__(self):
        self.job_dict = {}  # key 是任务的函数名，value 是 greenlet

    def add_job(self, job, *args, **kwargs):
        """
        增加并发任务
        :param job: 实际的任务函数
        :param args:
        :param kwargs: 参数
        :return:
        """
        job_name = job.__name__
        # if job_name in self.job_dict:
        #     raise KeyError("duplicated job: %s" % job_name)
        self.job_dict[job_name] = gevent.spawn(job, *args, **kwargs)

    def __call__(self, *args, **kwargs):
        """
        开启协程，返回结果
        :return:
        """
        gevent.joinall(self.job_dict.values())
        return {k: self.job_dict[k].value for k in self.job_dict}
