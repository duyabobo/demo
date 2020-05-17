#! /usr/bin/env python
# -*- coding: utf-8 -*- 
# 到 celery_tasks 父目录下，执行：celery -A celery_tasks worker -l info &，就会自动寻找 celery_tasks 目录下的 celery 文件
from __future__ import absolute_import, unicode_literals

from celery import Celery

app = Celery('proj',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['celery_tasks.task1'])  # 这里要为celery消费者注册一下异步任务

# Optional configuration, see the application user guide.
app.conf.update(
    result_expires=3600,
)

if __name__ == '__main__':
    app.start()
