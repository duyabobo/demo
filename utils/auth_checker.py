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
'''  # 认证服务独有


def _check_sign(sign):
    data = jwt.decode(sign, SIGN_SECRET, algorithm=ALGORITHM_SIGN)
    exp = data['exp']  # 过期时间戳，精确到微秒，假设不会有两个请求的 exp 是一样的
    assert request_is_first_received(exp)  # 就是一个 redis 的 setnx 操作，防止重放攻击，设置 redis 缓存过期时间到 exp 本身

    return data


def _get_user_info(sign):
    """
    从 sign 解析用户信息
    :return:
    """
    data = _check_sign(sign)
    access_token = data['access_token']  # token 里可以解析出 user_id
    token_info = jwt.decode(access_token, PUBLIC_KEY_TOKEN, algorithm=ALGORITHM_TOKEN)

    # get_newest_login_mark 依赖 redis，具体不做实现
    is_newest_login_device = token_info['login_mark'] == get_newest_login_mark(token_info['user_id'])
    return {"user_id": token_info['user_id'], "is_newest_login_device": is_newest_login_device}


def sign_checker(func):
    """
    校验 sign，sign 的作用在于：能够证明客户端身份。游客请求的接口认证，登录前的认证，比如请求验证码接口。
    除非 app 被反编译了（h5另说）。
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sign = self.get_argument('sign')
        response = None
        try:
            _check_sign(sign)
        except Exception as e:
            response = {'msg': 'request error, e[%s]' % e}
        if not response:
            response = func(self, *args, **kwargs)
        self.write(response)
        return response

    return wrapper


def token_checker(func):
    """
    检查 sign 和 access_token，access_token 的作用在于：能够证明用户身份。登录后的普通接口请求认证。
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sign = self.get_argument('sign')
        response = None
        try:
            self.user_info = _get_user_info(sign)
            self.user_id = self.user_info['user_id']
        except Exception as e:
            response = {'msg': 'request error, e[%s]' % e}
        if not response:
            response = func(self, *args, **kwargs)
        self.write(response)
        return response
    return wrapper


def right_checker(func):
    """
    检查 sign 和 access_token 和 right，right 的作用在于：能够证明用户权限。只能最新登陆的用户才有权限请求的接口，比如看课程视频，比如共享单车会员扫码骑车。
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sign = self.get_argument('sign')
        response = None
        try:
            self.user_info = _get_user_info(sign)
            self.user_id = self.user_info['user_id']
            assert self.user_info['is_newest_login_device']
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
    s = time.time()
    # 本地执行 一万次 对称解密 + 一万次 非对称解密，大概消耗 7 s。每次对称解密0.2毫秒，每次非对称解密0.5毫秒左右。
    for i in range(10000):
        data = _check_sign(sign)
        access_token = data['access_token']  # token 里可以解析出 user_id
        token_info = jwt.decode(access_token, PUBLIC_KEY_TOKEN, algorithm=ALGORITHM_TOKEN)
        # print token_info
    e = time.time()
    print (e-s)
