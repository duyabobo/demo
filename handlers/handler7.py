#! /usr/bin/env python
# -*- coding: utf-8 -*-

from base_handler import BaseHandler

from dao.user import get_user_by_id
from dao.user_deposit import get_deposit_by_uid
from helper.deal import make_deal
from utils.monitor import monitor


class ExampleHandler7(BaseHandler):
    """ handler 层边界：接收参数，调用 dao、helper，处理返回"""
    __model__ = ''

    @monitor
    def get(self):
        """查询个人账户
        """
        user_id = int(self.get_argument('user_id'))
        user_info = get_user_by_id(self.db_session, user_id)
        deposit_info = get_deposit_by_uid(self.db_session, user_id)
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

    @monitor
    def put(self):
        """账户变更：付款交易
        """
        from_uid = self.get_argument('user_id')
        to_uid = self.get_argument('to_uid')
        deal_money = self.get_argument('deal_money')
        ret = make_deal(self.db_session, from_uid, to_uid, deal_money)
        resp_data = {'pay_ret': ret}
        return self.response(resp_data=resp_data)
