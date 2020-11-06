#!/usr/bin/env python
# -*-coding: utf-8 -*-
import json
import pickle

import urllib3

CONNECT_POOL = urllib3.PoolManager(retries=2, timeout=10, num_pools=200, maxsize=200)

HOST_DICT = {
    'user': "http://localhost:9999",
}


class RouteParse(object):
    def __init__(self, business_name, path):
        self.business_name = business_name
        self.path = path

    @property
    def url(self):
        return HOST_DICT[self.business_name] + '/' + self.path.replace('.', '/')


class Shadow(object):
    def __init__(self, business_name, path, default_res):
        self.business_name = business_name
        self.route = RouteParse(self.business_name, path)
        self.default_res = default_res

    def __call__(self, **kwargs):
        body = kwargs
        try:
            response = CONNECT_POOL.request("POST", self.route.url, body=json.dumps(body))
            res = pickle.loads(response.data)
            # log
        except Exception as e:
            res = self.default_res
            # log
        return res
