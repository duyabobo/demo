#! /usr/bin/env python
# -*- coding: utf-8 -*-
from model.user_deposit import UserDeposit
from model.user_deposit_changes import DEAL_TYPE_COLLECTION
from model.user_deposit_changes import DEAL_TYPE_PAY
from model.user_deposit_changes import UserDepositChanges


class DepositService(object):

    def __init__(self, from_uid, to_uid):
        self.from_uid = from_uid
        self.to_uid = to_uid
        self.__from_deposit = None
        # 需要对 from_uid 和 to_uid 加个唯一锁，同一个用户同一时间，只能有一个交易处理，setnx 就好，这里不做实现。

    @property
    def from_deposit(self):
        if not self.__from_deposit:
            self.__from_deposit = UserDeposit.get_deposit(self.from_uid)
        return self.__from_deposit

    def deposit_change(self, deal_money):
        """
        完成交易
        :param deal_money:
        :return: 0 成功，-1 失败
        """
        if not self.from_deposit:
            return -1
        if self.from_deposit.need_check_money and self.from_deposit.money < deal_money:  # 余额不足
            return -1
        # 为了简单，不实现单次/单日消费上限这些逻辑

        UserDeposit.update_money(self.from_uid, deal_money*-1)  # 付款逻辑
        UserDepositChanges.add_one(self.from_uid, self.to_uid, DEAL_TYPE_PAY, deal_money*-1)

        UserDeposit.update_money(self.to_uid, deal_money)  # 收款逻辑
        UserDepositChanges.add_one(self.to_uid, self.from_uid, DEAL_TYPE_COLLECTION, deal_money)
        return 0
