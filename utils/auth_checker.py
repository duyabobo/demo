#! /usr/bin/env python
# -*- coding: utf-8 -*- 
import functools
import time

import jwt

SIGN_SECRET = 'SIGN_SECRET'  # 客户端和服务端共享
TOKEN_SECRET = 'TOKEN_SECRET'  # 只有服务端知晓
ALGORITHM = 'HS256'


def auth_checker(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sign = self.get_argument('sign')
        response = None
        try:
            data = jwt.decode(sign, SIGN_SECRET, algorithm=ALGORITHM)
            req_id = data['exp']
            access_token = data['access_token']  # token 里可以解析出 user_id
            token_info = jwt.decode(access_token, TOKEN_SECRET, algorithm=ALGORITHM)
            user_id = token_info['user_id']
            # 把 req_id 放到缓存，设置缓存过期时间5分钟，同一个 req_id，只会处理一次，否则就丢弃掉
            # task_node = self.task_node
            # key = 'user_id:%s:req_id:%s' % (user_id, req_id)
            # if not task_node.public_redis.setnx(key, 1, 300):
            #     response = {'msg': 'duplicated req_id[%s]' % req_id}
        except Exception as e:
            response = {'msg': 'request error, e[%s]' % e}
        if not response:
            response = func(self, *args, **kwargs)
        self.write(response)
        return response
    return wrapper


if __name__ == '__main__':
    expire_time = time.time() + 7*24*3600
    access_token = jwt.encode({'user_id': 'user_id', 'exp': expire_time},
                              TOKEN_SECRET, algorithm=ALGORITHM)  # 服务端产生，作为 restfull 请求时无状态请求的令牌
    expire_time = time.time() + 10
    sign = jwt.encode({'access_token': access_token, 'exp': expire_time},
                      SIGN_SECRET, algorithm=ALGORITHM)  # 客户端生成后，传给服务端验证

    print(sign)
