#! /usr/bin/env python
# -*- coding: utf-8 -*- 
import functools
import time

import jwt

SIGN_SECRET = 'SIGN_SECRET'  # 客户端和服务端共享
ALGORITHM_SIGN = 'HS256'  # sign 加密方式，每次请求都会产生一个单独的 sign

ALGORITHM_TOKEN = 'RS256'
PUBLIC_KEY_TOKEN = '''-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC+9fewqxVaIDXFfXmeuWiRb7o9
gqkWfofItU5OyPtlfGXCQyyZpT5L1ToCfKTmZt9s7cb4/lmKPtAr+4URT3GAYR5U
kfrdkgAswuGDfBuc7OH8OU4rxkCpiZ0u8gfH0aStVytGK8TTWOTBxPvYdBZhRd+F
XUqVM8LA5kwKoOyoyQIDAQAB
-----END PUBLIC KEY-----
'''  # 各其他微服务使用
PRIVATE_KEY_TOKEN = '''-----BEGIN PRIVATE KEY-----
MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAL7197CrFVogNcV9
eZ65aJFvuj2CqRZ+h8i1Tk7I+2V8ZcJDLJmlPkvVOgJ8pOZm32ztxvj+WYo+0Cv7
hRFPcYBhHlSR+t2SACzC4YN8G5zs4fw5TivGQKmJnS7yB8fRpK1XK0YrxNNY5MHE
+9h0FmFF34VdSpUzwsDmTAqg7KjJAgMBAAECgYEAkLvMp9KDtHOFTdH0RCEy6EhO
WCCYF7x/HdiNKZmbMSg/2CUhwLJFrSRHe2sNcLO308/EZyQgqW9CSJOyH5Se6Ob+
Pz276wx5MliMw2HGNUB2LFbb0FstAXo3QxMbD0/a4bBKX1OdCs1Havq4qq6hPyln
X1d/YJ4TIR1Rt5yenoECQQDqFBhaQEVQBPDNt2UxCAF87qRGx6kL8zx/nrdGhk+1
GGziRppDl4JXZ0xHs8MjWo24E1Ip708/Gx/0FEaE/yu1AkEA0NgmOKkxA74jARWw
YV/Dzw02J1dDu5gcj6jN8/+fOWXbttdQl4H4g2VWeRk3tIhMt3KvT2ZdGV8w4SJC
cqT9RQJAJeVO8/2HuyaxnXxdY4y6QPGZouPcGFUurDKT1VUVPmpP5moru1mh/mh4
zvrpUqXsX6qxGJznpX3MtIU7zXhKKQJBAMpzruGgikZRjIdhqiFK/3t5GDUc8Ckr
tQxCnJxbAdRXfJ2LrrGgqfNeSmyMWKbmtk/jmjTDS57r22tzlayjam0CQQDWRlY9
4EWdeW3dbazwfEOTPR8SlTHd7DALfDPc7S+IL1VMl0yt2FDTZbHG0Plp40IzSkmI
erQFLJ3WFjlsRPPr
-----END PRIVATE KEY-----
'''  # 认知服务独有


def auth_checker(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sign = self.get_argument('sign')
        response = None
        try:
            data = jwt.decode(sign, SIGN_SECRET, algorithm=ALGORITHM_SIGN)
            req_id = data['exp']
            access_token = data['access_token']  # token 里可以解析出 user_id
            token_info = jwt.decode(access_token, PUBLIC_KEY_TOKEN, algorithm=ALGORITHM_TOKEN)
            user_id = token_info['user_id']
            self.user_id = user_id
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
    access_token = jwt.encode({'user_id': 41, 'exp': expire_time},
                              PRIVATE_KEY_TOKEN, algorithm=ALGORITHM_TOKEN)  # 服务端产生，作为 restfull 请求时无状态请求的令牌
    expire_time = time.time() + 60
    sign = jwt.encode({'access_token': access_token, 'exp': expire_time},
                      SIGN_SECRET, algorithm=ALGORITHM_SIGN)  # 客户端生成后，传给服务端验证

    print(sign)  # 产生一个 sign，拿去请求 restful
