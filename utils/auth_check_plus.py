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

# 下面是限流方案。滑动窗口算法实现，更精准，但也更复杂，姑且不考虑。如有意，可以加多个限流标准：比如现在建立的是分钟级别的，可以增加十分钟级别的，半小时级别的...。
# nginx ngx_http_limit_req_module 进行频率限制，也可以应用程序结合 redis 进行频率监控。
# 后者对嫌疑请求的处理更灵活（比如出滑块，返回假数据，返回错误提示等），前者对恶意 ip 或关键 url 进行保护（直接拒绝响应）。
# 一般应用程序内部滑块处理：
# 0，什么都不可信：不会有人知道这个接口？不会有人知道加密算法？不会有人无聊到压测这个接口？不会有人想获取这个接口到返回数据？no。所以，尽可能多的接口使用 sign 验证。
# 1，无 sign 接口，对 ip 进行频次监控并处理。
# 2，有 sign 接口，只需要 uid 进行频次监控并处理。
# 3，对关键接口保护，比如读写关键数据的接口，比如资源消耗严重的接口，在1，2的基础上，增加对于指定 url 的监控和处理。
# 4，一般 1/2 对触发频次阈值非常宽松，3 可以适当严格。
# 5, 滑块验证通过后，可以对请求放行，并对频次清零重新计数监控，做到对正常用户的最小影响。
# 6，尽可能实时的自动化的维护一个 ip 黑名单，以及一个 uid 黑名单，并在应用中对这些 ip/uid 发出的请求进行处理。
# 7，如果 6 中黑名单请求量特别大，已经影响到系统正常提供服务，就直接在 ng 进行 503 拒绝响应。
FAILED_CNT_ONE_MINUTE = 'failed_cnt:one_minute:{remote_ip}'
SUCCESS_CNT_ONE_MINUTE = 'success_cnt:one_minute:{user_id}'
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
        self.check_success_cnt()  # 有消耗服务资源攻击行为时放开，1～3次redis操作
        secret = self.check_secret()  # 1次redis查询操作
        exp = self.check_sign(secret)  # 1次解密操作
        self.check_unique(exp)  # 1～2次redis写入操作

    def fail(self):
        """校验失败处理"""
        failed_key = FAILED_CNT_ONE_MINUTE.format(remote_ip=self.remote_ip)
        failed_cnt = self.redis_cli.incr(failed_key)
        if failed_cnt == 1:
            self.redis_cli.expire(60)

    def success(self):
        """校验成功处理"""
        success_cnt_key = SUCCESS_CNT_ONE_MINUTE.format(user_id=self.user_id)
        success_cnt = self.redis_cli.incr(success_cnt_key)
        if success_cnt == 1:
            self.redis_cli.expire(60)
        return success_cnt

    def check_failed_cnt(self):
        """防止撞库"""
        failed_key = FAILED_CNT_ONE_MINUTE.format(remote_ip=self.remote_ip)
        failed_cnt = self.redis_cli.get(failed_key) or 0
        assert failed_cnt < FAILED_CNT_LIMIT_ONE_MINUTE, 'failed too frequent'

    def check_success_cnt(self):
        """防止伪造"""
        success_cnt_key = SUCCESS_CNT_ONE_MINUTE.format(user_id=self.user_id)
        success_cnt = self.redis_cli.get(success_cnt_key) or 0
        if success_cnt > SUCCESS_CNT_LIMIT_ONE_MINUTE:
            self.redis_cli.delete(success_cnt_key)
            secret_key = SECRET_UID_KEY.format(user_id=self.user_id)
            self.redis_cli.delete(secret_key)
            raise Exception('success too frequent')

    def check_secret(self):
        """身份认证"""
        key = SECRET_UID_KEY.format(user_id=self.user_id)
        secret = self.redis_cli.get(key)
        assert secret, 'get secret error'
        return secret

    def check_sign(self, secret):
        """签名认证"""
        data = jwt.decode(self.sign, secret, algorithm=ALGORITHM_SIGN)  # 完成有效期校验和 secret 校验，具体加密方式多种多样不一定jwt
        return data['exp']  # 过期时间戳，精确到微秒，假设不会有两个请求的 exp 是一样的

    def check_unique(self, exp):
        """防止重放"""
        key = UNIQUE_EXP_KEY.format(exp=exp)
        assert exp < time.time() + 60, 'exp is too big'
        ret = self.redis_cli.setnx(key, 1)
        assert int(ret), 'set unique error'
        self.redis_cli.expireat(key)


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
        else:
            checker.success()

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
