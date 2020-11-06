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
from handlers.handler7 import ExampleHandler7
from handlers.handler8 import LoginHandler, WatchViedoHandler, NotWatchViedoHandler

from rpc_service.helper.service import Handler
from service.deposit import PayService

rpc_server_handlers = Handler([
    (PayService, 'test_rpc_func'),
    (PayService, 'test_rpc_func2'),
    (PayService, 'test_rpc_func3'),
    (PayService, 'test_rpc_func4'),
    (PayService, 'test_rpc_func5'),
    (PayService, 'test_rpc_func6'),
]).handlers  # 同一个业务线下的rpc和业务共享同一个套代码，但是建议rpc服务器和业务服务器分开部署，同时建议rpc的这些func都专门定义在特定类的静态方法中。


handlers = [
    (r'/1$', ExampleHandler1),  # run_on_executor demo
    (r'/2$', ExampleHandler2),  # gevent + time_log + sleep demo
    (r'/3$', ExampleHandler3),  # gevent + time_log + request demo
    (r'/4$', ExampleHandler4),  # jwt + 多重装饰器 demo
    (r'/5$', ExampleHandler5),  # celery demo
    (r'/6$', ExampleHandler6),  # 充血模型 demo
    (r'/7$', ExampleHandler7),  # 贫血模型 demo
    (r'/8$', LoginHandler),  # 验证码登陆
    (r'/9$', WatchViedoHandler),  # 看视频
    (r'/10$', NotWatchViedoHandler),  # 不是看视频
]

handlers.extend(rpc_server_handlers)
