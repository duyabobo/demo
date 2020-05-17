#! /usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import TIMESTAMP
from sqlalchemy import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class UserAnswer(Base):
    """用户回答问题记录"""
    __tablename__ = 'user_answer'
    id = Column(Integer, primary_key=True)  # 自增
    user_id = Column(Integer)  # 用户 id
    question_id = Column(Integer)  # 问题 id
    answer_id = Column(Integer)  # 答案 id
    updated_time = Column(TIMESTAMP, default=func.now(), onupdate=func.now())  # 最新更新时间
    created_time = Column(TIMESTAMP, default=func.now())  # 创建时间
