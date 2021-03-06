#! /usr/bin/env python
# -*- coding: utf-8 -*-
from tornado.concurrent import run_on_executor

from base_handler import BaseHandler
from model.user import UserModel
from model.user_deposit import UserDepositModel
from service.deposit import PayService
from utils.monitor import monitor


class ExampleHandler6(BaseHandler):
    """ handler 层边界：接收参数，调用应用层服务或领域层（也就是 service 层/ model 层），处理返回"""
    __model__ = ''

    @monitor
    def get(self):
        """查询个人账户
        """
        user_info = UserModel.get_user_info(self.user_id)
        deposit_info = UserDepositModel.get_deposit(self.user_id)
        resp_data = {
            'user_info': {
                'user_id': self.user_id,
                'name': user_info.name,
            },
            'deposit_info': {
                'money': deposit_info.money,
                'deposit_type': deposit_info.deposit_type,
            },
        }
        return self.response(resp_data=resp_data)

    @monitor
    def put(self):
        """账户变更：付款交易
        """
        from_uid = self.user_id
        to_uid = self.get_argument('to_uid')
        deal_money = self.get_argument('deal_money')
        ds = PayService(from_uid, to_uid)
        ret = ds.pay(deal_money)
        resp_data = {'pay_ret': ret}
        return self.response(resp_data=resp_data)
