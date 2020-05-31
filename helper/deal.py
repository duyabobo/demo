#!/usr/bin/env python
# -*-coding: utf-8 -*-
from dao.user_deposit import get_deposit_by_uid
from dao.user_deposit import update_deposit
from dao.user_deposit_changes import add_user_deposit_change
from model_const import DEAL_TYPE_COLLECTION
from model_const import DEAL_TYPE_PAY

def transfer_money(db_session, from_uid, to_uid, deal_money):
    """
    转账，面向过程还是面向对象，都能实现业务逻辑，也都有办法实现高内聚低耦合，都能很好实现代码复用，最主要的区别就是属性是否可以共享。
    分层清晰后，helper 层并不会出现复杂混乱的调用关系，
    面向过程编程灵活，每一个函数不依赖于某个类，而是依赖于某个业务逻辑聚合（逻辑耦合度高就放到一个文件中，拆分的时候拆分文件就行，各个函数之间不共享属性，也就没有属性拆分的困扰），
    函数级别测试方便，
    handler 调用方便不需要实例化。
    :param db_session:
    :param from_uid:
    :param to_uid:
    :param deal_money:
    :return:
    """
    update_deposit(db_session, from_uid, deal_money * (-1))
    update_deposit(db_session, to_uid, deal_money)


def add_transfer_history(db_session, from_uid, to_uid, deal_money):
    """
    记录转账记录，贫血模型的缺点就是参数走到哪里带到哪里，而不是像 oop 里一个class里互相共享属性。
    :param db_session:
    :param from_uid:
    :param to_uid:
    :param deal_money:
    :return:
    """
    add_user_deposit_change(db_session, from_uid, to_uid, DEAL_TYPE_PAY, deal_money*(-1))
    add_user_deposit_change(db_session, to_uid, from_uid, DEAL_TYPE_COLLECTION, deal_money)


def make_deal(db_session, from_uid, to_uid, deal_money):
    """
    交易，贫血模型与充血模型对比，这里缺点就是严重面向过程，参数都要传进来，而不是先实例化一个服务对象（在实例化的时候传一部分参数）
    :param db_session:
    :param from_uid:
    :param to_uid:
    :param deal_money:
    :return:
    """
    if deal_money <= 0:
        return -1

    from_deposit = get_deposit_by_uid(db_session, from_uid)
    if not from_deposit:
        return -1
    if from_deposit.need_check_money and from_deposit.money < deal_money:  # 余额不足
        return -1

    transfer_money(db_session, from_uid, to_uid, deal_money)
    add_transfer_history(db_session, from_uid, to_uid, deal_money)
    return 0
