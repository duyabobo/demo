#! /usr/bin/env python
# -*- coding: utf-8 -*- 
from datetime import datetime

from peewee import DateTimeField
from peewee import IntegerField

from base import BaseModel

DEAL_TYPE_PAY = 0
DEAL_TYPE_COLLECTION = 1


class UserDepositChanges(BaseModel):
    """存款变动流水表，每次交易，付款者和收款者都会在这里记录一条记录（付款者增加一条付款记录，收款者增加一条收款记录）"""

    class Meta:
        table_name = 'user_deposit_changes'

    id = IntegerField(primary_key=True)  # 自增
    user_id = IntegerField(default=0)  # uid
    partner_uid = IntegerField(default=0)  # 与之配对的 uid
    deal_type = IntegerField(default=0)  # 变动类型：0 收款，2 付款，为了简单，不实现存钱/取钱逻辑
    deal_money = IntegerField(default=0)  # 变动金额
    updated_time = DateTimeField(default=datetime.now())  # 最新更新时间
    created_time = DateTimeField(default=datetime.now())  # 创建时间

    @classmethod
    def add_one(cls, user_id, partner_uid, deal_type, deal_money):
        """
        增加一条记录，为什么要在这里封装一下 peewee 的 create 呢（一种个人习惯吧）
        方便通过编辑器找到 `增加记录方法` 的 usages 位置（如果有多个地方调用的话）
        :param user_id:
        :param partner_uid:
        :param deal_type:
        :param deal_money:
        :return:
        """
        return cls.create(
            user_id=user_id,
            partner_uid=partner_uid,
            deal_type=deal_type,
            deal_money=deal_money,
        )

    @classmethod
    def add_changes(cls, from_uid, to_uid, deal_money):
        """
        增加金额转移流水，这里也是属于依赖 dao（持久层逻辑）的业务逻辑，在充血模型中，划分到 model 层
        :param from_uid:
        :param to_uid:
        :param deal_money:
        :return:
        """
        cls.add_one(from_uid, to_uid, DEAL_TYPE_PAY, deal_money*-1)
        cls.add_one(to_uid, from_uid, DEAL_TYPE_COLLECTION, deal_money)
