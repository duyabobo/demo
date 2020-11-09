#! /usr/bin/env python
# -*- coding: utf-8 -*- 
from datetime import datetime
from time import time

from rpc_service.business_a import test_rpc_func, test_rpc_func2, test_rpc_func3, test_rpc_func4, test_rpc_func5, \
    test_rpc_func6

s = time()
ret1, ret2, ret3, ret4, ret5, ret6 = [[0]] * 6
for i in range(1000):
    ret1 = test_rpc_func(a=i, b=i**2, c=i*2, d=datetime.now())  # 模拟远程调用
    ret2 = test_rpc_func2(a=i, b=i**2, c=i*2, d=time())  # 模拟远程调用
    ret3 = test_rpc_func3(a=i, b=i**2, c=i*2, d=[1, 2, 3])  # 模拟远程调用
    ret4 = test_rpc_func4(a=i, b=i**2, c=i*2, d=(4, 5, 6))  # 模拟远程调用
    ret5 = test_rpc_func5(a=i, b=i**2, c=i*2, d={'d': 'd'})  # 模拟远程调用
    ret6 = test_rpc_func6(a=i, b=i**2, c=i*2)  # 模拟远程调用
e = time()
for ret in [ret1, ret2, ret3, ret4, ret5, ret6]:
    print ret
    for r in ret:
        print type(r)
print e - s
