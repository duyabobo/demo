from __future__ import absolute_import, unicode_literals

from celery_tasks.celery import app


@app.task
def add(x, y):
    print 'add x , y: %s, %s' % (x, y)
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
