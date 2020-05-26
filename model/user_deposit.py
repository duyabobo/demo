#! /usr/bin/env python
# -*- coding: utf-8 -*-
from datetime import datetime

from peewee import DateTimeField
from peewee import IntegerField

from base import BaseModel

DEPOSIT_TYPE_NORMAL = 0
DEPOSIT_TYPE_BUSINESS = 1
DEPOSIT_TYPE_PERSONAL_VIP = 2
DEPOSIT_TYPE_GOVERNMENT = 3
DEPOSIT_TYPE_BLACK_CARD = 4
DEPOSIT_TYPE_BANK_SPECIAL = 5


class UserDepositModel(BaseModel):
    """用户存款信息表"""

    class Meta:
        table_name = 'user_deposit'

    id = IntegerField(primary_key=True)  # 自增
    user_id = IntegerField(default=0)  # 用户id
    money = IntegerField(default=0)  # 存款余额
    # deposit_type 是为了实现一种与持久化逻辑无关的业务逻辑，而加的一个臆想字段：
    deposit_type = IntegerField(default=0)  # 账户类型：0 普通储蓄，1 企业客户，2 个人vip，3 政府机构，4 黑卡用户，5 银行特别账户
    updated_time = DateTimeField(default=datetime.now())  # 最新更新时间
    created_time = DateTimeField(default=datetime.now())  # 创建时间

    @classmethod
    def update_money(cls, user_id, money_changed):
        """
        余额变更
        :param user_id:
        :param money_changed:  变动金额数，正值为增加，负值为减少
        :return:
        """
        return cls.update(money=cls.money + money_changed).where(cls.user_id == user_id).execute()

    @classmethod
    def change_money(cls, from_uid, to_uid, money_changed):
        """
        余额转移，这就不是简单的 dao（即持久化操作），也不是简单的与 dao（即持久化操作）无关的单条记录属性这样的业务逻辑
        而是与 dao（即持久化操作）有关的业务逻辑，在充血模型中，就要划分到 model 层
        :param from_uid:
        :param to_uid:
        :param money_changed:
        :return:
        """
        cls.update_money(from_uid, money_changed * -1)  # 付款逻辑
        cls.update_money(to_uid, money_changed)  # 收款逻辑

    @classmethod
    def get_deposit(cls, user_id):
        """
        查询用户的存款
        :param user_id:
        :return:
        """
        return cls.select().where(cls.user_id == user_id)

    @property
    def need_check_money(self):
        """
        交易过程是否需要检查余额（假设有些账户类型可以不用检查余额）
        :return:
        """
        return self.deposit_type in [
            DEPOSIT_TYPE_NORMAL,
            DEPOSIT_TYPE_BUSINESS,
            DEPOSIT_TYPE_PERSONAL_VIP
        ]
