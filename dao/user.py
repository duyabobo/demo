#!/usr/bin/env python
# -*-coding: utf-8 -*-
from models import User


def get_user_by_id(db_session, user_id):
    """
    查询用户信息
    :param db_session:
    :param user_id:
    :return:
    """
    return db_session.query(User).filter(User.id == user_id).first()
