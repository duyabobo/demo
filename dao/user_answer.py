#! /usr/bin/env python
# -*- coding: utf-8 -*-
from models import UserAnswer


def get_answers_by_uid(db_session, user_id):
    """
    获取某个人答题数据
    :param db_session:
    :param user_id:
    :return:
    """
    return db_session.query(UserAnswer).filter(UserAnswer.user_id == user_id).all()


def get_answer_cnts(db_session, question_id):
    """
    查询某个问题的回答人数
    :param db_session:
    :param question_id:
    :return:
    """
    return db_session.query(UserAnswer).filter(UserAnswer.question_id == question_id).count()


def add_answer(db_session, user_id, question_id, answer_id):
    """
    提交答案
    :param db_session:
    :param user_id:
    :param question_id:
    :param answer_id:
    :return:
    """
    user_answer = UserAnswer(
        user_id=user_id,
        question_id=question_id,
        answer_id=answer_id,
    )
    db_session.add(user_answer)
    db_session.flush()
    return user_answer
