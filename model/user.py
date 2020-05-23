#! /usr/bin/env python
# -*- coding: utf-8 -*- 
from datetime import datetime

from peewee import CharField
from peewee import DateTimeField
from peewee import IntegerField

from base import BaseModel


class User(BaseModel):
    """用户表"""

    class Meta:
        table_name = 'user'

    id = IntegerField(primary_key=True)  # 自增
    name = CharField(default='')  # 姓名
    updated_time = DateTimeField(default=datetime.now())  # 最新更新时间
    created_time = DateTimeField(default=datetime.now())  # 创建时间

    @classmethod
    def get_user_info(cls, user_id):
        """
        查询用户信息
        :param user_id:
        :return:
        """
        return cls.select().where(cls.id == user_id)
