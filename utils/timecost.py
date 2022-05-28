#! /usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: UTF-8 -*-
# 手写一个性能监控模块，类似于line_profiler提供的功能。
import functools
import json
import random
import time

import tornado.concurrent


class TaskNode(object):
    def __init__(self):
        self.timecost_tree = []
        self.child_filo = []
        self.start_timecost()

    def get_cur_child(self):
        return self.child_filo[-1]

    def start_timecost(self):
        self.timecost_tree = self.create_new_child('root')
        self.child_filo = [self.timecost_tree]

    @staticmethod
    def create_new_child(step_name):
        return [step_name, 0, [], time.time() * 1000]

    def tc_child_in(self, step_name):
        cur_child = self.get_cur_child()
        new_child = self.create_new_child(step_name)
        cur_child[2].append(new_child)
        self.child_filo.append(new_child)

    def tc_child_out(self):
        cur_child = self.get_cur_child()
        cur_child[1] = time.time() * 1000 - cur_child[3]
        cur_child.pop()
        self.child_filo.pop()

    def tc_child_drop(self):
        # 放弃这个child
        self.child_filo[-2][2].pop()
        self.child_filo.pop()

    def finish_timecost(self):
        self.tc_child_out()


tn = TaskNode()


def timecost(deco_fn=None, step_name=None):
    # 放到@gen.coroutine装饰的方法上会无效
    def _timecost(fn):
        @functools.wraps(fn)
        def _wrap(*args, **kwargs):
            if step_name is None:
                _step_name = fn.__name__
            else:
                _step_name = step_name
            tn.tc_child_in(_step_name)
            ret = fn(*args, **kwargs)
            if isinstance(ret, tornado.concurrent.Future):  # 这里会丢弃掉@gen.coroutine的方法
                tn.tc_child_drop()
            else:
                tn.tc_child_out()
            return ret

        return _wrap

    if deco_fn is not None and callable(deco_fn):
        return _timecost(deco_fn)
    return _timecost


@timecost
def f1(n):
    time.sleep(n / 1)
    f2(n)


@timecost
def f2(n):
    time.sleep(n / 2)
    f3(n)


@timecost
def f3(n):
    time.sleep(n / 3)


@timecost
def test_func():
    n = random.randint(1, 10) / 100.0
    f1(n)


if __name__ == '__main__':
    test_func()
    tn.finish_timecost()
    print json.dumps(tn.timecost_tree, indent=2)
