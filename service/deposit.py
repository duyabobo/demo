#! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime
from time import time

from model.user_deposit import UserDepositModel
from model.user_deposit_changes import UserDepositChangesModel
from models_with_peewee import UserAnswer


class Node(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b


class PayService(object):
    """service 层边界：根据业务耦合度划分 service，管理事务控制，并调用多个领域层（也就是 model 层）"""

    def __init__(self, from_uid, to_uid):
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.__from_deposit = None
        # 需要对 from_uid 和 to_uid 加个唯一锁，同一个用户同一时间，只能有一个交易处理，setnx 就好，这里不做实现。

    @property
    def from_deposit(self):
        if not self.__from_deposit:
            self.__from_deposit = UserDepositModel.get_deposit(self.from_uid)
        return self.__from_deposit

    @staticmethod
    def test_rpc_func(**kwargs):
        return kwargs, 1, datetime.now()

    @staticmethod
    def test_rpc_func2(**kwargs):
        return kwargs, 2, time()

    @staticmethod
    def test_rpc_func3(**kwargs):
        return kwargs, 3, Node(kwargs.get('a', 1), kwargs.get('b', 2))

    @staticmethod
    def test_rpc_func4(**kwargs):
        return kwargs, 4, (kwargs.get('a', 1), kwargs.get('b', 2))

    @staticmethod
    def test_rpc_func5(**kwargs):
        return kwargs, 5, [kwargs.get('a', 1), kwargs.get('b', 2)]

    @staticmethod
    def test_rpc_func6(**kwargs):
        answers = UserAnswer.get_answers_by_uid(user_id=1)
        return kwargs, 6, answers

    def pay(self, deal_money):
        """
        支付行为
        :param deal_money:
        :return: 0 成功，-1 失败
        """
        if deal_money <= 0:
            return -1
        if not self.from_deposit:
            return -1
        if self.from_deposit.need_check_money and self.from_deposit.money < deal_money:  # 余额不足
            return -1
        # 为了简单，不实现单次/单日消费上限这些逻辑

        # 这里把同一个数据模型的，依赖于 dao（即持久层逻辑）的业务逻辑也划分到 model 层
        # 但是仍然保留了不同数据模型的业务逻辑在 service 层
        # 同时权限检查/事务管理等这些逻辑，也都需要继续保留在 service 层
        UserDepositModel.change_money(self.from_uid, self.to_uid, deal_money)
        UserDepositChangesModel.add_changes(self.from_uid, self.to_uid, deal_money)
        return 0
