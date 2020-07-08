#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 举几个例子，说明 jwt 在 sign_checker, token_checker, right_checker 三级验证上的实例
from base_handler import BaseHandler
from utils.auth_checker import sign_checker, token_checker, right_checker


class LoginHandler(BaseHandler):
    """登陆认证"""

    @sign_checker
    def get(self):
        """
        app 验证码登陆，如果用户不存在，就注册一个用户
        :return:
        """
        phone = self.get_argument('phone')  # 必填就不要写 default
        code = self.get_argument('code')  # 短信验证码
        check_code_ret = check_code(phone, code)

        resp_data = {}
        if check_code_ret:
            login_user = get_login_user(self.db_session, phone)
            access_token = gen_access_token(login_user)
            resp_data = {
                'access_token': access_token  # 返回 access_token 而不是 session_id
            }
        return self.response(resp_data=resp_data)

    @sign_checker
    def post(self):
        """
        app 获取验证码，不需要滑块
        :return:
        """
        phone = self.get_argument('phone')
        # 1，手机号 phone 格式校验，校验不通过就直接拒绝。phone 格式校验先忽略。
        # 2，对 ip/phone/设备号 进行`验证码请求`对频率检查，频率检查不通过直接拒绝。这里也忽略。
        gen_code(phone)
        return self.response()


def NotWatchViedoHandler(BaseHandler):

    @token_checker
    def get(self):
        """
        非看课程，多设备登陆后，每个设备都可以请求获取数据
        :param self:
        :return:
        """
        # not_watch_video(self.user_info)
        return self.response()


def WatchViedoHandler(BaseHandler):

    @right_checker
    def get(self):
        """
        看课程，只允许最新一次登陆的设备可以看课程，比如返回一个一次性的视频链接
        :return:
        """
        # watch_video(self.user_info)
        return self.response()
