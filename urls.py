#!/usr/bin/env python
# coding=utf-8
# __author__ = ‘duyabo‘
# __created_at__ = '2020/1/1'
from handlers.handler1 import ExampleHandler1
from handlers.handler2 import ExampleHandler2
from handlers.handler3 import ExampleHandler3
from handlers.handler4 import ExampleHandler4
from handlers.handler5 import ExampleHandler5
from handlers.handler6 import ExampleHandler6

handlers = [
    (r'/1$', ExampleHandler1),
    (r'/2$', ExampleHandler2),
    (r'/3$', ExampleHandler3),
    (r'/4$', ExampleHandler4),
    (r'/5$', ExampleHandler5),
    (r'/6$', ExampleHandler6),
]
