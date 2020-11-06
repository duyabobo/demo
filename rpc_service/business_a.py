#!/usr/bin/env python
# -*-coding: utf-8 -*-
# 这里记录一个业务A提供的rpc列表
from rpc_service.helper.client import Shadow

test_rpc_func = Shadow("user", "service.deposit.PayService.test_rpc_func", default_res=())
test_rpc_func2 = Shadow("user", "service.deposit.PayService.test_rpc_func2", default_res=())
test_rpc_func3 = Shadow("user", "service.deposit.PayService.test_rpc_func3", default_res=())
test_rpc_func4 = Shadow("user", "service.deposit.PayService.test_rpc_func4", default_res=())
test_rpc_func5 = Shadow("user", "service.deposit.PayService.test_rpc_func5", default_res=())
test_rpc_func6 = Shadow("user", "service.deposit.PayService.test_rpc_func6", default_res=())
