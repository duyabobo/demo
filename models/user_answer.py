#! /usr/bin/env python
# -*- coding: utf-8 -*-
# peewee demo
# 和 sqlalchemy 相比，通过 peewee 建立的 model 可以更方便的把 dao 层逻辑加进来。
from datetime import datetime

from peewee import DateTimeField
from peewee import IntegerField

from base import BaseModel


class UserAnswer(BaseModel):
    """用户回答问题记录"""

    class Meta:
        table_name = 'user_answer'

    id = IntegerField(primary_key=True)  # 自增
    user_id = IntegerField(default=0)  # 用户 id
    question_id = IntegerField(default=0)  # 问题 id
    answer_id = IntegerField(default=0)  # 答案 id
    updated_time = DateTimeField(default=datetime.now())  # 最新更新时间
    created_time = DateTimeField(default=datetime.now())  # 创建时间

    @classmethod
    def add_answer(cls, user_id, question_id, answer_id):
        """
        增加回答记录
        :param user_id:
        :param question_id:
        :param answer_id:
        :return:
        """
        obj, _ = cls.get_or_create(
            user_id=user_id,
            question_id=question_id,
            answer_id=answer_id,
        )
        return obj

    @classmethod
    def get_answer_cnts(cls, question_id):
        """
        统计回答数
        :param question_id:
        :return:
        """
        return cls.select(cls.id).where(cls.question_id == question_id).count()

    @classmethod
    def get_answers_by_uid(cls, user_id):
        """
        获取一个用户的回答
        :param user_id:
        :return:
        """
        return cls.select().where(cls.user_id == user_id)
