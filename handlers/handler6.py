#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.concurrent import run_on_executor

from base_handler import BaseHandler
from model.user import User
from model.user_deposit import UserDeposit
from service.deposit import DepositService
from utils.time_logger import time_logger


class ExampleHandler6(BaseHandler):
    __model__ = ''

    @run_on_executor
    @time_logger
    def get(self):
        """查询个人账户
        """
        user_id = int(self.get_argument('user_id'))
        user_info = User.get_user_info(user_id)
        deposit_info = UserDeposit.get_deposit(user_id)
        resp_data = {
            'user_info': {
                'user_id': user_id,
                'name': user_info.name,
            },
            'deposit_info': {
                'money': deposit_info.money,
                'deposit_type': deposit_info.deposit_type,
            },
        }
        return self.response(resp_data=resp_data)

    @run_on_executor
    @time_logger
    def put(self):
        """账户变更：交易或者存/取钱
        """
        from_uid = self.get_argument('user_id')
        to_uid = self.get_argument('to_uid')
        deal_money = self.get_argument('deal_money')
        ds = DepositService(from_uid, to_uid)
        ret = ds.deposit_change(deal_money)
        resp_data = {'deposit_change_ret': ret}
        return self.response(resp_data=resp_data)
