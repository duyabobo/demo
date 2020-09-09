#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 结合 redis 实现一人一密的接口安全认证方案。加密方案使用jwt，但是实际落地不仅限于 jwt（md5等均可），jwt 方便之处是可以自带并自检 exp。
# 可以防止撞库，撞对一个的概率是1/(52**32)。如果有撞库现象，可以对 ip 进行频次监控。
# 不怕密钥泄漏，密钥不会传输，不怕被抓取。如果用户主动伪造攻击，可以对 uid 进行频次监控。
# 不怕加密算法泄漏，因为一人一密。
# 可以防止重放攻击。
import functools
import random
import time

import jwt
from tornado.log import gen_log

from const import RESP_AUTH_CHECK_ERROR, RESP_TOP_MONITOR_ERROR
from database import redis_cli

ALGORITHM_SIGN = 'HS256'
UNIQUE_EXP_KEY = 'unique:exp:{exp}'
SECRET_UID_KEY = 'secret:uid:{user_id}'
SUCCESS_CNT_ONE_MINUTE = 'success_cnt:one_minute:{user_id}'
FAILED_CNT_ONE_MINUTE = 'failed_cnt:one_minute:{remote_ip}'
SUCCESS_CNT_LIMIT_ONE_MINUTE = 300
FAILED_CNT_LIMIT_ONE_MINUTE = 10


class Checker(object):
    def __init__(self, redis_cli, remote_ip, user_id, sign):
        self.redis_cli = redis_cli
        self.remote_ip = remote_ip
        self.user_id = user_id
        self.sign = sign

    def check(self):
        """对请求进行检查，拦截无效/非法/恶意的请求。
        攻击是不能完全防控的，还需要监控日志识别恶意ip和虚假user，并进行管控和清理。"""
        self.check_failed_cnt()  # 有爬取用户信息攻击行为时放开，1次redis查询操作
        secret = self.check_secret()  # 1次redis查询操作
        exp = self.check_sign(secret)  # 1次解密操作
        self.check_unique(exp)  # 1～2次redis写入操作
        self.check_success_cnt()  # 有消耗服务资源攻击行为时放开，1～4次redis写入操作

    def fail(self):
        """失败处理"""
        key = FAILED_CNT_ONE_MINUTE.format(remote_ip=self.remote_ip)
        failed_cnt = self.redis_cli.incr(key)
        if failed_cnt == 1:
            self.redis_cli.expire(60)

    def check_failed_cnt(self):
        """防止撞库"""
        key = FAILED_CNT_ONE_MINUTE.format(remote_ip=self.remote_ip)
        failed_cnt = self.redis_cli.get(key) or 0
        assert failed_cnt < FAILED_CNT_LIMIT_ONE_MINUTE, 'failed too frequent'

    def check_secret(self):
        """身份认证"""
        key = SECRET_UID_KEY.format(user_id=self.user_id)
        secret = self.redis_cli.get(key)
        assert secret, 'get secret error'
        return secret

    @staticmethod
    def check_sign(secret):
        """签名认证"""
        data = jwt.decode(sign, secret, algorithm=ALGORITHM_SIGN)  # 完成有效期校验和 secret 校验，具体加密方式多种多样不一定jwt
        return data['exp']  # 过期时间戳，精确到微秒，假设不会有两个请求的 exp 是一样的

    def check_unique(self, exp):
        """防止重放"""
        key = UNIQUE_EXP_KEY.format(exp=exp)
        assert exp < time.time() + 60, 'exp is too big'
        ret = self.redis_cli.setnx(key, 1)
        assert int(ret), 'set unique error'
        self.redis_cli.expireat(key)

    def check_success_cnt(self):
        """防止伪造"""
        success_cnt_key = SUCCESS_CNT_ONE_MINUTE.format(user_id=self.user_id)
        success_cnt = self.redis_cli.incr(success_cnt_key)
        if success_cnt == 1:
            self.redis_cli.expire(60)
        if success_cnt > SUCCESS_CNT_LIMIT_ONE_MINUTE:
            self.redis_cli.delete(success_cnt_key)
            secret_key = SECRET_UID_KEY.format(user_id=self.user_id)
            self.redis_cli.delete(secret_key)
            raise Exception('success too frequent')


def request_checker(func):
    """
    校验，装饰器放到 view 方法上即可。
    :param func:
    :return:
    """
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        sign = self.get_argument('sign')
        user_id = self.get_argument('user_id')
        remote_ip = self.request.remote_ip
        request_msg = 'remote_ip: %s, params:%s, body:%s' % \
                      (remote_ip, self.request.query_arguments, self.request.body)

        response = None
        checker = Checker(redis_cli, remote_ip, user_id, sign)
        try:
            checker.check()
        except Exception as e:
            checker.fail()
            response = RESP_AUTH_CHECK_ERROR
            gen_log.error('request_msg[%s], err[%s]', request_msg, e)

        if not response:
            try:
                response = func(self, *args, **kwargs)
            except Exception as e:
                response = RESP_TOP_MONITOR_ERROR
                gen_log.exception('request_msg[%s] err[%s]', request_msg, e)
        self.write(response)

        log_msg = 'request_msg[%s] ret[%s]' % (request_msg, response)
        gen_log.info(log_msg)
        return response

    return wrapper


if __name__ == '__main__':
    expire_time = time.time() + 60
    # 假设客户端已经和服务端通过认证握手，获得了一人一密的 user_id 和 secret, 服务端也存储了这个 user_id/secret
    user_id, secret = 23331342, ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 32))
    sign = jwt.encode({'exp': expire_time}, secret, algorithm=ALGORITHM_SIGN)
    print(sign)  # 产生一个 sign，拿去请求 restful.

    s = time.time()
    # 本地执行一万次对称解密，耗时小于1s，每次平均耗时不到0.1ms。
    for i in range(10000):
        try:
            jwt.decode(sign, secret, algorithm=ALGORITHM_SIGN)
        except Exception as e:
            pass
    e = time.time()
    print(e - s)
