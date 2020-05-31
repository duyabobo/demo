#!/usr/bin/env python
# -*-coding: utf-8 -*-
from models import UserDeposit


def get_deposit_by_uid(db_session, user_id):
    """
    查询用户的存款
    :param
    user_id:
    :return:
    """
    return db_session.query(UserDeposit).filter(UserDeposit.user_id == user_id).first()


def update_deposit(db_session, user_id, money_changed):
    """
    更新余额
    :param db_session:
    :param user_id:
    :param money_changed:
    :return:
    """
    ret = db_session.query(UserDeposit).filter(UserDeposit.user_id == user_id).\
        update({"money": UserDeposit.money + money_changed})
    if ret:
        db_session.flush()
    return ret
