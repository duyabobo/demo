#!/usr/bin/env python
# -*-coding: utf-8 -*-
# 这里用于封装实现 rpc 服务，可以放到 git 的 submodule 里去共享给所有业务项目
# 为了防止服务之间循环调用，就需要限制一下，rpc 调用必须发生在 handler 层，rpc 定义必须发生在 service 层。
