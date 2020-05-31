#! /usr/bin/env python
# -*- coding: utf-8 -*-
# 这里只完成一件事：数据表映射，以及简单的实例属性加持。
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

from model_const import DEPOSIT_TYPE_BUSINESS
from model_const import DEPOSIT_TYPE_NORMAL
from model_const import DEPOSIT_TYPE_PERSONAL_VIP

Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)  # 自增
    name = Column(String)  # 用户 id
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间


class UserDeposit(Base):
    """用户存款信息表"""
    __tablename__ = 'user_deposit'

    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer, default=0)  # 用户id
    money = Column(Integer, default=0)  # 存款余额
    # deposit_type 是为了实现一种与持久化逻辑无关的业务逻辑，而加的一个臆想字段：
    deposit_type = Column(Integer, default=0)  # 账户类型：0 普通储蓄，1 企业客户，2 个人vip，3 政府机构，4 黑卡用户，5 银行特别账户
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间

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


class UserDepositChanges(Base):
    """存款变动流水表，每次交易，付款者和收款者都会在这里记录一条记录（付款者增加一条付款记录，收款者增加一条收款记录）"""
    __tablename__ = 'user_deposit_changes'

    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer, default=0)  # 用户id
    partner_uid = Column(Integer, default=0)  # 与之配对的 uid
    deal_type = Column(Integer, default=0)  # 变动类型：0 收款，2 付款，为了简单，不实现存钱/取钱逻辑
    deal_money = Column(Integer, default=0)  # 变动金额(分)
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间
