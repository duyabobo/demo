#!/usr/bin/env python
# -*-coding: utf-8 -*-
from models import UserDepositChanges


def add_user_deposit_change(db_session, user_id, partner_uid, deal_type, deal_money):
    """
    加一条用户资金变动记录
    :param db_session:
    :param user_id:
    :param partner_uid:
    :param deal_type:
    :param deal_money:
    :return:
    """
    user_deposit_change = UserDepositChanges(
        user_id=user_id,
        partner_uid=partner_uid,
        deal_type=deal_type,
        deal_money=deal_money,
    )
    db_session.add(user_deposit_change)
    db_session.flush()
    return user_deposit_change
