#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handler1 import ExampleHandler1
from handler2 import ExampleHandler2

handlers = [
    (r'/1$', ExampleHandler1),
    (r'/2$', ExampleHandler2),
]
